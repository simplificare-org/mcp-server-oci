# Use Python base image
FROM python:3.13-slim-bookworm

# Install the project into `/app`
WORKDIR /app

# Copy the entire project
COPY . /app

# Install dependencies first for better caching
RUN pip install --no-cache-dir oci mcp pydantic

# Install the package in development mode
RUN pip install --extra-index-url https://test.pypi.org/simple/ -e .

# Run the server
ENTRYPOINT ["python", "-m", "mcp_server_oci_resources.server"] 