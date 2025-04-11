import argparse
import asyncio
import logging
from . import server

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('mcp_policloud_agent_oci')

def main():
    logger.debug("Starting mcp-server-OCI main()")
    parser = argparse.ArgumentParser(description='MCP Server OCI')
    parser.add_argument('--access-token', help='OCI access token')
    args = parser.parse_args()
    
    logger.debug(f"Access token from args: {args.access_token}")
    # Run the async main function
    logger.debug("About to run server.main()")
    asyncio.run(server.main(args.access_token))
    logger.debug("Server main() completed")

if __name__ == "__main__":
    main()

# Expose important items at package level
__all__ = ["main", "server"] 