# Theoretical Saturation MCP

An MCP (Model Context Protocol) server written in Python, focused on managing the theoretical saturation state for systematic literature reviews in autonomous agents workflows.

This project is structured with best practices to be easily executable via `uvx`, allowing it to be used as a standalone, zero-installation tool.

## ⚙️ Features

The server provides a robust set of tools specifically designed to handle the state management of an Autonomous Theoretical Saturation Agent:

- **State Initialization**: `initialize_project` creates the initial taxonomy and papers registry.
- **State Queries**: `get_taxonomy_state` retrieves current scope and phase data, while `get_papers` returns the full or filtered registry.
- **Anti-Looping Filtering**: `get_actionable_papers` selects papers that have not yet undergone specific recursive operations.
- **Data Enrichment**: `add_papers` registers new discoveries as pending, and `update_paper` flags operations performed.
- **Taxonomy Evolution**: `add_taxonomy_concept` registers novel concepts discovered during analysis.
- **Loop Control**: `update_metadata_state` handles phase transitions and redundancy limits.
- **Audit Logging**: `log_decision` records each novelty evaluation decision directly into the activity history.

## 📄 Generated State Artifacts

The MCP automatically manages and mutates three primary local files to persist the agent's state:

### `taxonomy.yaml`
Acts as the core memory, defining boundaries and the extracted domain knowledge:
```yaml
metadata:
  seed_paper_id: "semantic_scholar_id"
  seed_paper_title: "Paper Title"
  positivity_scope: "what is IN scope"
  negativity_scope: "what is OUT scope"
  current_phase: 1
  redundancy_counter: 0
mathematical_constraints:
  - capacity limits
solution_methods:
  - genetic algorithm
```

### `papers.json`
An index tracking the status and operations performed on discovered papers to prevent infinite loops:
```json
{
  "paper_id_123": {
    "title": "A Great Paper on Optimization",
    "status": "in_scope",
    "operations": [
      "trace_citations_snowball_backward"
    ]
  }
}
```

### `log.yaml`
An incremental audit log of the agent's novelty evaluation decisions:
```yaml
- paperId: "paper_id_123"
  title: "A Great Paper on Optimization"
  brought_novelty: true
  novelty_description: "Introduced a new constraint: capacity limits"
  decision: "Added to taxonomy"
  discover_phase: "Phase 2"
```

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
