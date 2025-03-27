# Model Context Protocol (MCP) Server for OCI Resources

The MCP Server for OCI Resources is a Python-based server that allows you to create and delete Oracle Cloud Infrastructure (OCI) resources using the Model Context Protocol (MCP). It is lightweight, easy to deploy, and supports containerized execution using Docker.

---

## Features

- Create OCI resources
- Delete OCI resources
- Supports containerized deployment with Docker
- Built with Python and libraries like `oci`, `mcp`, and `pydantic`

---

## Requirements

- Python 3.10 or higher
- Docker (optional, for containerized deployment)

---

## Installation

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t mcp-server-oci-resources:latest .
   ```

2. Run the container:
   ```bash
    docker run -i --rm \
  -e OCI_PROFILE=DEFAULT \
  -e OCI_CONFIG_FILE=/root/.oci/config \
  -v /path/to/your/.oci/config:/root/.oci/config \
  -v /path/to/your/.oci/private_key.pem:/root/.oci/private_key.pem \
  mcp-server-oci-resources:latest
   ```

For additional Docker commands and usage, refer to the `commands` file in the project directory.

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcp-server-oci
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Run the server:
   ```bash
   python -m mcp_server_oci_resources.server
   ```

---

## Usage

The server exposes endpoints to create and delete OCI resources. You can interact with the server using HTTP requests. Refer to the API documentation (if available) for details on the endpoints and request/response formats.

To integrate this server with your system, add the following configuration to your `claude_config.json` file (or a similar configuration file for other LLM host applications):

```json
{
  "mcpServers": {
    "oci-resources": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "OCI_PROFILE=DEFAULT",
        "-e",
        "OCI_CONFIG_FILE=/root/.oci/config",
        "-v",
        "/Users/bantwal/.oci/config:/root/.oci/config",
        "-v",
        "/Users/bantwal/.oci/hpai.bantwal@me.com_2024-09-25T19_55_49.831Z.pem:/root/.oci/hpai.bantwal@me.com_2024-09-25T19_55_49.831Z.pem",
        "mcp-server-oci-resources:latest"
      ]
    }
  }
}
```

This configuration can be used with any LLM host applications (e.g., Claude Desktop, IDEs, or other tools) that initiate connections to MCP servers.

---

## Development

To contribute to this project:

1. Fork the repository and create a new branch for your feature or bugfix.
2. Make your changes and ensure they are well-tested.
3. Submit a pull request for review.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
