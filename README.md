# Oracle Cloud Infrastructure (OCI) MCP Server - SyntropAI Ecosystem

**Part of the [SyntropAI MCP Ecosystem](https://github.com/paihari/documentation-syntropai)** - A unified multi-cloud abstraction framework.

This MCP (Model Context Protocol) server provides secure, dynamic access to Oracle Cloud Infrastructure services through the innovative SyntropAI abstraction layer. Unlike traditional hardcoded service catalogs, this server supports **any OCI service** through dynamic SDK access with built-in security sandboxing.

## 🚀 Key Features

- **Universal OCI Access**: Dynamic access to all Oracle Cloud services without hardcoded limitations
- **Secure Code Execution**: AST-based validation and sandboxed execution environment
- **Provider-Agnostic Design**: Built on SyntropAI's unified abstraction pattern
- **Future-Proof Architecture**: Automatically supports new OCI services without updates
- **Docker Containerization**: Production-ready deployment

## 🏗️ Architecture

This server implements the SyntropAI abstraction pattern:

```
Claude Desktop → MCP Protocol → OCI MCP Server → SyntropAIBox → OCI SDK → Oracle Cloud
```

### Core Components:
- **OCISession**: Unified OCI credential management using `BaseSession`
- **OCIResourceQuerier**: Secure query execution extending `BaseQuerier`
- **AST Sandbox**: Safe code execution with timeout protection
- **Dynamic Schema**: Runtime API documentation generation

## 📋 Prerequisites

- Python 3.10 or higher
- OCI credentials configured (via `~/.oci/config` or environment variables)
- Docker (recommended)
- [SyntropAIBox](https://test.pypi.org/project/syntropaibox/) core library
- Valid OCI tenancy and user credentials

## 🐳 Docker Installation (Recommended)

### Build and Run
```bash
# Build the image
docker build -t mcp-server-oci-resources .

# Run with OCI config file (recommended)
docker run -i --rm \
  -v ~/.oci:/root/.oci \
  mcp-server-oci-resources:latest

# Run with custom profile
docker run -i --rm \
  -e OCI_PROFILE=MYPROFILE \
  -v ~/.oci:/root/.oci \
  mcp-server-oci-resources:latest

# Run with custom config location
docker run -i --rm \
  -e OCI_CONFIG_FILE=/root/.oci/custom_config \
  -v /path/to/your/.oci:/root/.oci \
  mcp-server-oci-resources:latest
```

## ⚙️ Claude Desktop Integration

Add to your `claude_config.json`:

```json
{
  "mcpServers": {
    "oci-resources": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/Users/yourusername/.oci:/root/.oci",
        "mcp-server-oci-resources:latest"
      ]
    }
  }
}
```

## 🛡️ Security Features

### AST-Based Validation
- Prevents malicious code injection
- Whitelisted imports and functions
- Controlled execution environment

### Safe Execution
- Timeout protection (2-second default)
- Isolated namespace
- JSON-serialized responses

### Example Safe Query
```python
# User provides this code snippet:
import oci
compute_client = oci.core.ComputeClient(config)
result = compute_client.list_instances(compartment_id="ocid1.compartment...")
```

The system:
1. ✅ Validates AST syntax
2. ✅ Checks allowed imports (`oci` approved)
3. ✅ Executes in sandbox with timeout
4. ✅ Returns JSON-serialized results

## 🔧 Usage Examples

### List Compute Instances
```python
import oci
compute_client = oci.core.ComputeClient(config)
result = [instance.data for instance in compute_client.list_instances(compartment_id="your_compartment_id").data]
```

### Object Storage Operations
```python
import oci
object_storage = oci.object_storage.ObjectStorageClient(config)
namespace = object_storage.get_namespace().data
result = [bucket.name for bucket in object_storage.list_buckets(namespace, "your_compartment_id").data]
```

### Virtual Cloud Networks
```python
import oci
network_client = oci.core.VirtualNetworkClient(config)
result = [vcn.data for vcn in network_client.list_vcns(compartment_id="your_compartment_id").data]
```

### Identity and Access Management
```python
import oci
identity_client = oci.identity.IdentityClient(config)
result = [user.data for user in identity_client.list_users(compartment_id="your_compartment_id").data]
```

### Database Services
```python
import oci
database_client = oci.database.DatabaseClient(config)
result = [db.data for db in database_client.list_db_systems(compartment_id="your_compartment_id").data]
```

## 🌟 SyntropAI Ecosystem Benefits

### Unified Multi-Cloud
- Same patterns work across AWS, Azure, OCI
- Consistent authentication and error handling
- Provider-agnostic abstractions

### Non-Hardcoded Services
- Supports **any** OCI service automatically
- No service catalog limitations
- Future services work immediately

### Enterprise Ready
- Security-first design
- Docker containerization
- Comprehensive logging

## 🔐 OCI Authentication Setup

### 1. OCI CLI Configuration (Recommended)
```bash
oci setup config
```

### 2. Manual Configuration
Create `~/.oci/config`:
```ini
[DEFAULT]
user=ocid1.user.oc1..your_user_ocid
fingerprint=your_key_fingerprint
tenancy=ocid1.tenancy.oc1..your_tenancy_ocid
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

### 3. Environment Variables
```bash
export OCI_CONFIG_FILE=~/.oci/config
export OCI_PROFILE=DEFAULT
```

### 4. Instance Principal (OCI Compute)
For applications running on OCI Compute instances, use instance principals for authentication.

## 🔗 Related Projects

- **[Main Documentation](https://github.com/paihari/documentation-syntropai)**: Complete ecosystem overview and architecture
- **[SyntropAIBox Core](https://test.pypi.org/project/syntropaibox/)**: Shared abstraction library
- **[AWS MCP Server](../mcp-server-for-aws)**: AWS implementation
- **[Azure MCP Server](../mcp-server-azure)**: Azure implementation
- **[Finviz MCP Server](../mcp_finviz)**: Financial data server

## 🏆 Technical Highlights

This implementation showcases:
- **Advanced Abstraction Patterns**: Clean separation of concerns
- **Security Engineering**: AST validation and sandboxed execution
- **Cloud Architecture**: Scalable, maintainable multi-cloud design
- **DevOps Excellence**: Containerized, configurable deployment

## 📞 Support

For questions about the SyntropAI MCP ecosystem:
- **Documentation**: [SyntropAI Documentation Project](https://github.com/paihari/documentation-syntropai)
- **Author**: Hari Bantwal (hpai.bantwal@gmail.com)

## 🔄 Manual Installation (Development)

```bash
# Clone repository
git clone <repository-url>
cd mcp-server-oci

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run server
python -m mcp_server_oci_resources.server
```

## 🌐 OCI Services Coverage

The server provides access to all OCI services including:
- **Compute**: Instances, Images, Boot Volumes
- **Networking**: VCNs, Subnets, Load Balancers
- **Storage**: Object Storage, Block Volumes, File Storage
- **Database**: Autonomous Database, MySQL, NoSQL
- **Identity**: Users, Groups, Policies, Compartments
- **AI/ML**: Data Science, AI Platform services
- **Security**: Vault, Certificates, Web Application Firewall
- **DevOps**: Build, Deploy, Code Repositories

And many more - all accessible through the unified SyntropAI interface.

---

*This server demonstrates cutting-edge cloud abstraction technology, providing secure, unified access to Oracle Cloud Infrastructure through innovative architectural patterns.*