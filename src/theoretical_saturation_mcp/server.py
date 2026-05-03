import os
import json
import yaml
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Theoretical Saturation")

# Default files
PAPERS_FILE = "theo-sat/papers.json"
TAXONOMY_FILE = "theo-sat/taxonomy.yaml"
LOG_FILE = "theo-sat/log.yaml"

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
def add_papers(papers: dict[str, str], filepath: str = PAPERS_FILE) -> str:
    """Registers new paper IDs and titles in the database with 'pending' status. Returns the number of new papers registered and the number of papers that already existed. """
    path = Path(filepath)
    registry = read_json(path)
    added = 0
    
    for pid, title in papers.items():
        if pid not in registry:
            registry[pid] = {
                "title": title,
                "status": "pending",
                "operations": []
            }
            added += 1
            
    if added > 0:
        write_json(path, registry)
    return f"Success: {added} new papers registered. {len(papers) - added} already existed."

@mcp.tool()
def update_paper(paper_id: str, status: str = None, title: str = None, add_operation: str = None, remove_operation: str = None, filepath: str = PAPERS_FILE) -> str:
    """Updates paper attributes. Supports status in [in_scope, out_of_scope, pending], title, add/remove operations. Returns success message or error message if paper not found"""
    path = Path(filepath)
    registry = read_json(path)
    
    if paper_id not in registry:
        return f"Error: Paper {paper_id} not found in the registry."
        
    paper = registry[paper_id]
    changed = False
    
    if status is not None and paper.get("status") != status:
        paper["status"] = status
        changed = True
        
    if title is not None and paper.get("title") != title:
        paper["title"] = title
        changed = True
        
    if add_operation and add_operation not in paper.get("operations", []):
        paper.setdefault("operations", []).append(add_operation)
        changed = True
        
    if remove_operation and remove_operation in paper.get("operations", []):
        paper["operations"].remove(remove_operation)
        changed = True
        
    if changed:
        write_json(path, registry)
        return f"Success: Paper {paper_id} updated."
        
    return f"Success: No changes made to paper {paper_id}."

@mcp.tool()
def get_papers(status: str = None, filepath: str = PAPERS_FILE) -> list[dict]:
    """Filters papers by status and returns a list of paper objects. If status is None, returns all papers."""
    path = Path(filepath)
    registry = read_json(path)
    
    if status:
        return [{"id": pid, **paper} for pid, paper in registry.items() if paper.get("status") == status]
    return [{"id": pid, **paper} for pid, paper in registry.items()]

@mcp.tool()
def get_actionable_papers(status: str, missing_operation: str, limit: int = 1, filepath: str = PAPERS_FILE) -> list[str]:
    """Returns a list of paper IDs (up to limit) that have the given status and have NOT undergone the missing_operation."""
    path = Path(filepath)
    registry = read_json(path)
    
    actionable = []
    for pid, paper in registry.items():
        if paper.get("status") == status and missing_operation not in paper.get("operations", []):
            actionable.append(pid)
            if len(actionable) >= limit:
                break
                
    return actionable

@mcp.tool()
def get_taxonomy_state(taxonomy_filepath: str = TAXONOMY_FILE) -> dict | list:
    """Returns the entire contents of the taxonomy and metadata."""
    return read_yaml(Path(taxonomy_filepath))

@mcp.tool()
def initialize_project(seed_paper_id: str, seed_paper_title: str, positivity_scope: str, negativity_scope: str, taxonomy_filepath: str = TAXONOMY_FILE, papers_filepath: str = PAPERS_FILE) -> str:
    """Initializes the project with the seed paper and scope definitions, setting current_phase=1 and redundancy_counter=0."""
    taxonomy = {
        "metadata": {
            "seed_paper_id": seed_paper_id,
            "seed_paper_title": seed_paper_title,
            "positivity_scope": positivity_scope,
            "negativity_scope": negativity_scope,
            "current_phase": 1,
            "redundancy_counter": 0
        }
    }
    write_yaml(Path(taxonomy_filepath), taxonomy)
    
    registry = {
        seed_paper_id: {
            "title": seed_paper_title,
            "status": "in_scope",
            "operations": []
        }
    }
    write_json(Path(papers_filepath), registry)
    return "Success: Project initialized."

@mcp.tool()
def add_taxonomy_concept(category: str, concept: str, taxonomy_filepath: str = TAXONOMY_FILE) -> str:
    """Adds a new mathematical concept, method, or constraint to the taxonomy."""
    path = Path(taxonomy_filepath)
    taxonomy = read_yaml(path)
    
    if category not in taxonomy:
        taxonomy[category] = []
        
    if isinstance(taxonomy[category], list) and concept not in taxonomy[category]:
        taxonomy[category].append(concept)
        write_yaml(path, taxonomy)
        return f"Success: '{concept}' added to category '{category}'."
        
    return f"Warning: Concept '{concept}' already exists or invalid category."


@mcp.tool()
def update_metadata_state(current_phase: int, redundancy_counter: int, taxonomy_filepath: str = TAXONOMY_FILE) -> str:
    """Updates the AI's loop control state (Phase and Redundancy) in memory."""
    path = Path(taxonomy_filepath)
    taxonomy = read_yaml(path)
    
    if "metadata" not in taxonomy:
        taxonomy["metadata"] = {}
        
    taxonomy["metadata"]["current_phase"] = current_phase
    taxonomy["metadata"]["redundancy_counter"] = redundancy_counter
    
    write_yaml(path, taxonomy)
    return f"Success: State updated -> Phase {current_phase}, Redundancy {redundancy_counter}/5."



@mcp.tool()
def log_decision(paper_id: str, title: str, brought_novelty: bool, novelty_description: str, decision: str, discover_phase: str, log_filepath: str = LOG_FILE) -> str:
    """Logs the evaluation decision for a paper in the audit log."""
    path = Path(log_filepath)
    log = read_yaml(path)
    if not isinstance(log, list):
        log = []
        
    entry = {
        "paperId": paper_id,
        "title": title,
        "brought_novelty": brought_novelty,
        "novelty_description": novelty_description,
        "decision": decision,
        "discover_phase": discover_phase
    }
    
    log.append(entry)
    write_yaml(path, log)
    return f"Success: Decision for '{paper_id}' recorded in the log."
