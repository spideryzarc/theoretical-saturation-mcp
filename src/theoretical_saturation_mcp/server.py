import os
import json
import yaml
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Theoretical Saturation")

# --- HELPER FUNCTIONS FOR READING/WRITING ---

def validate_path(filepath: Path, valid_extensions: tuple[str, ...]):
    """Validates the file extension and checks that it's not a directory."""
    if filepath.is_dir():
        raise ValueError(f"The path '{filepath}' points to a directory, but it must be a file.")
    if filepath.suffix.lower() not in valid_extensions:
        raise ValueError(f"Invalid extension for '{filepath.name}'. Expected: {valid_extensions}")

def read_json(filepath: Path) -> dict:
    validate_path(filepath, ('.json',))
    if not filepath.exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(filepath: Path, data: dict):
    validate_path(filepath, ('.json',))
    # Ensure the parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_yaml(filepath: Path) -> dict | list:
    validate_path(filepath, ('.yaml', '.yml'))
    if not filepath.exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def write_yaml(filepath: Path, data: dict | list):
    validate_path(filepath, ('.yaml', '.yml'))
    # Ensure the parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

# --- MCP TOOLS EXPOSED TO THE LLM ---

@mcp.tool()
def register_candidate_papers(paper_ids: list[str], registry_file: str = "theo-sat/papers.json") -> str:
    """Registers new paper IDs in the database with 'pending' status."""
    path = Path(registry_file)
    registry = read_json(path)
    added = 0
    
    for pid in paper_ids:
        if pid not in registry:
            registry[pid] = {
                "title": "Awaiting processing",
                "status": "pending",
                "operations_done": []
            }
            added += 1
            
    write_json(path, registry)
    return f"Success: {added} new papers registered. {len(paper_ids) - added} already existed."

@mcp.tool()
def update_paper_status(paper_id: str, status: str, title: str = None, new_operation: str = None, registry_file: str = "theo-sat/papers.json") -> str:
    """Updates the status (in_scope/out_of_scope) and logs operations performed on a paper."""
    path = Path(registry_file)
    registry = read_json(path)
    
    if paper_id not in registry:
        return f"Error: Paper {paper_id} not found in the registry."
        
    registry[paper_id]["status"] = status
    if title:
        registry[paper_id]["title"] = title
    if new_operation and new_operation not in registry[paper_id]["operations_done"]:
        registry[paper_id]["operations_done"].append(new_operation)
        
    write_json(path, registry)
    return f"Success: Paper {paper_id} updated to status '{status}'."

@mcp.tool()
def add_taxonomy_concept(category: str, concept: str, taxonomy_file: str = "theo-sat/taxonomy.yaml") -> str:
    """Adds a new mathematical concept, method, or constraint to the taxonomy."""
    path = Path(taxonomy_file)
    taxonomy = read_yaml(path)
    
    if category not in taxonomy:
        taxonomy[category] = []
        
    if isinstance(taxonomy[category], list) and concept not in taxonomy[category]:
        taxonomy[category].append(concept)
        write_yaml(path, taxonomy)
        return f"Success: '{concept}' added to category '{category}'."
        
    return f"Warning: Concept '{concept}' already exists or invalid category."

@mcp.tool()
def log_audit_decision(paper_id: str, title: str, novelty: bool, decision: str, justification: str, audit_file: str = "theo-sat/audit_log.yaml") -> str:
    """Logs the evaluation decision for a paper in the audit log."""
    path = Path(audit_file)
    log = read_yaml(path)
    if not isinstance(log, list):
        log = []
        
    entry = {
        "paperId": paper_id,
        "title": title,
        "brought_novelty": novelty,
        "decision": decision,
        "justification": justification
    }
    
    log.append(entry)
    write_yaml(path, log)
    return f"Success: Decision for '{paper_id}' recorded in the log."

@mcp.tool()
def update_metadata_state(current_phase: int, redundancy_counter: int, taxonomy_file: str = "theo-sat/taxonomy.yaml") -> str:
    """Updates the AI's loop control state (Phase and Redundancy) in memory."""
    path = Path(taxonomy_file)
    taxonomy = read_yaml(path)
    
    if "metadata" not in taxonomy:
        taxonomy["metadata"] = {}
        
    taxonomy["metadata"]["current_phase"] = current_phase
    taxonomy["metadata"]["redundancy_counter"] = redundancy_counter
    
    write_yaml(path, taxonomy)
    return f"Success: State updated -> Phase {current_phase}, Redundancy {redundancy_counter}/5."
