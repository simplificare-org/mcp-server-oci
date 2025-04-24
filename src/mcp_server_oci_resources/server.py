import argparse
import json
import logging
import ast
import os
from typing import Any
from pydantic import AnyUrl

import oci
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from operator import itemgetter

logger = logging.getLogger("mcp_oci_resources_server")


def parse_arguments() -> argparse.Namespace:
    """Use argparse to allow values to be set as CLI switches
    or environment variables

    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-file',
        default=os.environ.get('OCI_CONFIG_FILE', os.path.expanduser("~/.oci/config"))
    )
    parser.add_argument(
        '--profile',
        default=os.environ.get('OCI_PROFILE', 'DEFAULT')
    )
    return parser.parse_args()


class CodeExecutor(ast.NodeTransformer):
    """Custom AST NodeTransformer to validate and transform the code"""
    def __init__(self):
        self.has_result = False
        self.imported_modules = set()

    def visit_Assign(self, node):
        """Track if 'result' variable is assigned"""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'result':
                self.has_result = True
        return node

    def visit_Import(self, node):
        """Track imported modules"""
        for alias in node.names:
            self.imported_modules.add(alias.name)
        return node

    def visit_ImportFrom(self, node):
        """Track imported modules"""
        self.imported_modules.add(node.module)
        return node


class OCIResourceQuerier:
    def __init__(self):
        """Initialize OCI session using environment variables"""
        args = parse_arguments()
        self.config = oci.config.from_file(args.config_file, args.profile)

    def execute_query(self, code_snippet: str) -> str:
        """
        Execute a oci sdk code snippet and return the results and if errors make sure it is clearly documented

        Args:
            code_snippet (str): Python code using oci sdk to query OCI resources

        Returns:
            str: JSON string containing the query results or error message
        """

        try:
            tree = ast.parse(code_snippet)
            executor = CodeExecutor()
            executor.visit(tree)

            allowed_modules = {
                'oci', 'operator', 'json', 'datetime', 'pytz', 'dateutil', 're', 'time', 'sys', 'base64'
            }
            unauthorized_imports = executor.imported_modules - allowed_modules
            if unauthorized_imports:
                return json.dumps({
                    "error": f"Unauthorized imports: {', '.join(unauthorized_imports)}. "
                             f"Only {', '.join(allowed_modules)} are allowed."
                })

            # Create execution namespace
            local_ns = {
                'oci': oci,
                'config': self.config,
                'result': None,
                'itemgetter': itemgetter,
                '__builtins__': {
                    name: getattr(__builtins__, name)
                    for name in [
                        'dict', 'list', 'tuple', 'set', 'str', 'int', 'float', 'bool',
                        'len', 'max', 'min', 'sorted', 'filter', 'map', 'sum', 'any', 'all',
                        '__import__', 'hasattr', 'getattr', 'isinstance', 'print'
                    ]
                }
            }

            # Compile and execute the code
            compiled_code = compile(tree, '<string>', 'exec')
            exec(compiled_code, local_ns)
            
            # Get the result
            result = local_ns.get('result')
            
            # Validate result was set

            if not executor.has_result:
                return json.dumps({"error": "Code must set a 'result' variable with the query output"})

            # Convert result to JSON-serializable format
            if result is not None:
                if hasattr(result, 'to_dict'):
                    result = result.to_dict()
                return json.dumps(result, default=str)
            else:
                return json.dumps({"error": "Result cannot be None"})

        except SyntaxError as e:
            logger.error(f"Syntax error in code: {str(e)}")
            return json.dumps({"error": f"Syntax error: {str(e)}"})
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return json.dumps({"error": str(e)})


async def main():
    """Run the OCI Resources MCP server."""
    logger.info("Starting OCI resource server...")
    oci_querier = OCIResourceQuerier()
    server = Server("oci-resources-manager")

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri=AnyUrl("oci://query_resources"),
                name="OCI Resources Query",
                description="Execute OCI SDK queries for resources",
                mimeType="application/json",
            )
        ]

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        if uri.scheme != "oci":
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

        path = str(uri).replace("oci://", "")
        if path == "query_resources":
            # Return empty result as this endpoint requires a specific query
            return json.dumps({"message": "Please use the read_create_update_oci_resources tool to execute specific queries"})
        else:
            raise ValueError(f"Unknown resource path: {path}")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="read_create_update_oci_resources",
                description="Execute a code snippet using OCI Python SDK to query resources",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code_snippet": {
                            "type": "string",
                            "description": (
                                "Python code using OCI SDK to query resources. "
                                "The code must assign the result to a variable named 'result'."
                            ),
                        }
                    },
                    "required": ["code_snippet"]
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "read_create_update_oci_resources":
                if not arguments or "code_snippet" not in arguments:
                    raise ValueError("Missing code_snippet argument")

                results = oci_querier.execute_query(arguments["code_snippet"])
                return [types.TextContent(type="text", text=str(results))]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="oci-resources",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
