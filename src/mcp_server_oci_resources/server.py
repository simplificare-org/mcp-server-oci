import argparse
import json
import logging

import os
from typing import Any
from pydantic import AnyUrl

import oci
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from operator import itemgetter

from syntropaibox.mcp.base import BaseQuerier, DEFAULT_ALLOWED_MODULES, BaseSession


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


from syntropaibox.mcp.base import BaseSession

class OCISession(BaseSession):
    def __init__(self, config: dict):
        self.config = config

    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--config-file',
            default=os.environ.get('OCI_CONFIG_FILE', os.path.expanduser("~/.oci/config"))
        )
        parser.add_argument(
            '--profile',
            default=os.environ.get('OCI_PROFILE', 'DEFAULT')
        )

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "OCISession":
        config = oci.config.from_file(args.config_file, args.profile)
        return cls(config)


class OCIResourceQuerier(BaseQuerier):
    def __init__(self):
        parser = argparse.ArgumentParser()
        OCISession.configure_parser(parser)
        args = parser.parse_args()

        session = OCISession.from_args(args)

        namespace = {
            "oci": oci,
            "config": session.config,
        }

        allowed_module_prefixes = ("oci",)
        custom_modules = DEFAULT_ALLOWED_MODULES

        super().__init__(allowed_module_prefixes, custom_modules, namespace)


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
                description="Execute a oci python code snippet to query OCI resources",
                inputSchema=oci_querier.build_code_snippet_schema("oci sdk to query OCI resources")
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
        
        if name == "read_create_update_oci_resources":
            result_str = oci_querier.run_code_tool(arguments)
            return [types.TextContent(type="text", text=result_str)]
        else:
            raise ValueError(f"Unknown tool: {name}")



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
