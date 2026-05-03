# Theoretical Saturation MCP

An MCP (Model Context Protocol) server written in Python, focused on managing the theoretical saturation state for your systematic literature reviews.

This project is structured with best practices to be easily executable via `uvx`, allowing it to be used as a standalone, zero-installation tool.

## 🚀 Usage with `uvx`

The Python package structure of this project allows the server to be fetched, installed, and executed directly via GitHub using the `uv` CLI (specifically the `uvx` command).

To run it from anywhere in your terminal without cloning the repository, use:

```bash
# If the repository is public (replace 'your-username' with your GitHub username)
uvx --from git+https://github.com/your-username/theoretical-saturation-mcp theoretical-saturation-mcp
```

### 🔌 Claude Desktop Integration

Add the following configuration to your `claude_desktop_config.json` to load the MCP automatically:

```json
{
  "mcpServers": {
    "theoretical-saturation": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/your-username/theoretical-saturation-mcp",
        "theoretical-saturation-mcp"
      ]
    }
  }
}
```

## 🛠️ Local Development

To modify and test the code locally:

1. **Install `uv`** (if you haven't already):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone this repository** and enter its directory:
   ```bash
   git clone https://github.com/your-username/theoretical-saturation-mcp.git
   cd theoretical-saturation-mcp
   ```

3. **Run the server locally**:
   The `uv run` command automatically prepares a virtual environment and downloads dependencies for you.
   ```bash
   uv run theoretical-saturation-mcp
   ```

## 📁 Project Structure

* `pyproject.toml`: Package configuration, project metadata, and dependencies. Defines the `[project.scripts]` entrypoint used by `uvx`.
* `src/theoretical_saturation_mcp/main.py`: Entrypoint module that starts the MCP server.
* `src/theoretical_saturation_mcp/server.py`: Source code where the tools, resources, and FastMCP instance reside.
