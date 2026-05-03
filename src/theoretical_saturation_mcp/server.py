import os
import json
import yaml
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Inicializa o servidor MCP
mcp = FastMCP("Theoretical Saturation")

# --- FUNÇÕES AUXILIARES DE LEITURA/ESCRITA ---

def validate_path(filepath: Path, valid_extensions: tuple[str, ...]):
    """Valida a extensão do arquivo e verifica se não é um diretório."""
    if filepath.is_dir():
        raise ValueError(f"O caminho '{filepath}' aponta para um diretório, mas deve ser um arquivo.")
    if filepath.suffix.lower() not in valid_extensions:
        raise ValueError(f"Extensão inválida para '{filepath.name}'. Esperado: {valid_extensions}")

def read_json(filepath: Path) -> dict:
    validate_path(filepath, ('.json',))
    if not filepath.exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(filepath: Path, data: dict):
    validate_path(filepath, ('.json',))
    # Garante que o diretório pai existe
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
    # Garante que o diretório pai existe
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

# --- FERRAMENTAS MCP EXPOSTAS PARA O LLM ---

@mcp.tool()
def register_candidate_papers(paper_ids: list[str], registry_file: str = "theo-sat/papers.json") -> str:
    """Registra novos IDs de artigos no banco de dados com status 'pending'."""
    path = Path(registry_file)
    registry = read_json(path)
    added = 0
    
    for pid in paper_ids:
        if pid not in registry:
            registry[pid] = {
                "title": "Aguardando processamento",
                "status": "pending",
                "operations_done": []
            }
            added += 1
            
    write_json(path, registry)
    return f"Sucesso: {added} novos artigos registrados. {len(paper_ids) - added} já existiam."

@mcp.tool()
def update_paper_status(paper_id: str, status: str, title: str = None, new_operation: str = None, registry_file: str = "theo-sat/papers.json") -> str:
    """Atualiza o status (in_scope/out_of_scope) e registra operações feitas em um artigo."""
    path = Path(registry_file)
    registry = read_json(path)
    
    if paper_id not in registry:
        return f"Erro: Artigo {paper_id} não encontrado no registro."
        
    registry[paper_id]["status"] = status
    if title:
        registry[paper_id]["title"] = title
    if new_operation and new_operation not in registry[paper_id]["operations_done"]:
        registry[paper_id]["operations_done"].append(new_operation)
        
    write_json(path, registry)
    return f"Sucesso: Artigo {paper_id} atualizado para status '{status}'."

@mcp.tool()
def add_taxonomy_concept(category: str, concept: str, taxonomy_file: str = "theo-sat/taxonomy.yaml") -> str:
    """Adiciona um novo conceito matemático, método ou restrição à taxonomia."""
    path = Path(taxonomy_file)
    taxonomy = read_yaml(path)
    
    if category not in taxonomy:
        taxonomy[category] = []
        
    if isinstance(taxonomy[category], list) and concept not in taxonomy[category]:
        taxonomy[category].append(concept)
        write_yaml(path, taxonomy)
        return f"Sucesso: '{concept}' adicionado à categoria '{category}'."
        
    return f"Aviso: Conceito '{concept}' já existe ou categoria inválida."

@mcp.tool()
def log_audit_decision(paper_id: str, title: str, novelty: bool, decision: str, justification: str, audit_file: str = "theo-sat/audit_log.yaml") -> str:
    """Registra a avaliação de um artigo no log de auditoria."""
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
    return f"Sucesso: Decisão sobre '{paper_id}' registrada no log."

@mcp.tool()
def update_metadata_state(current_phase: int, redundancy_counter: int, taxonomy_file: str = "theo-sat/taxonomy.yaml") -> str:
    """Atualiza o controle de loop (Fase e Redundância) da IA na memória."""
    path = Path(taxonomy_file)
    taxonomy = read_yaml(path)
    
    if "metadata" not in taxonomy:
        taxonomy["metadata"] = {}
        
    taxonomy["metadata"]["current_phase"] = current_phase
    taxonomy["metadata"]["redundancy_counter"] = redundancy_counter
    
    write_yaml(path, taxonomy)
    return f"Sucesso: Estado atualizado -> Fase {current_phase}, Redundância {redundancy_counter}/5."
