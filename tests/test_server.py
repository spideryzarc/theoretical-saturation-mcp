import json
import yaml
import pytest
from pathlib import Path
from theoretical_saturation_mcp import server

def test_register_candidate_papers(tmp_path):
    registry_file = str(tmp_path / "papers_registry.json")
    
    # Test registering new papers
    result = server.register_candidate_papers(["paper1", "paper2"], registry_file=registry_file)
    assert "2 novos artigos registrados" in result
    assert "0 já existiam" in result
    
    # Verify file content
    registry = server.read_json(Path(registry_file))
    assert "paper1" in registry
    assert registry["paper1"]["status"] == "pending"
    
    # Test registering duplicate paper
    result = server.register_candidate_papers(["paper2", "paper3"], registry_file=registry_file)
    assert "1 novos artigos registrados" in result
    assert "1 já existiam" in result

def test_update_paper_status(tmp_path):
    registry_file = str(tmp_path / "papers_registry.json")
    
    # Initialize paper
    server.register_candidate_papers(["paper1"], registry_file=registry_file)
    
    # Update status
    result = server.update_paper_status("paper1", "in_scope", title="My Paper", new_operation="extraction", registry_file=registry_file)
    assert "Sucesso" in result
    
    registry = server.read_json(Path(registry_file))
    assert registry["paper1"]["status"] == "in_scope"
    assert registry["paper1"]["title"] == "My Paper"
    assert "extraction" in registry["paper1"]["operations_done"]
    
    # Try updating non-existent
    result = server.update_paper_status("nonexistent", "in_scope", registry_file=registry_file)
    assert "Erro" in result

def test_add_taxonomy_concept(tmp_path):
    taxonomy_file = str(tmp_path / "taxonomy.yaml")
    
    # Add new concept
    result = server.add_taxonomy_concept("methodology", "case_study", taxonomy_file=taxonomy_file)
    assert "Sucesso" in result
    
    # Add another
    server.add_taxonomy_concept("methodology", "survey", taxonomy_file=taxonomy_file)
    
    # Verify file content
    taxonomy = server.read_yaml(Path(taxonomy_file))
    assert "case_study" in taxonomy["methodology"]
    assert "survey" in taxonomy["methodology"]
    
    # Try adding duplicate
    result = server.add_taxonomy_concept("methodology", "case_study", taxonomy_file=taxonomy_file)
    assert "já existe" in result

def test_log_audit_decision(tmp_path):
    audit_file = str(tmp_path / "audit_log.yaml")
    
    # Log decision
    result = server.log_audit_decision(
        paper_id="paper1",
        title="Test Paper",
        novelty=True,
        decision="included",
        justification="Highly relevant",
        audit_file=audit_file
    )
    assert "Sucesso" in result
    
    # Verify file content
    log = server.read_yaml(Path(audit_file))
    assert len(log) == 1
    assert log[0]["paperId"] == "paper1"
    assert log[0]["brought_novelty"] is True
    assert log[0]["decision"] == "included"

def test_update_metadata_state(tmp_path):
    taxonomy_file = str(tmp_path / "taxonomy.yaml")
    
    # Update state
    result = server.update_metadata_state(current_phase=2, redundancy_counter=1, taxonomy_file=taxonomy_file)
    assert "Sucesso" in result
    
    # Verify file content
    taxonomy = server.read_yaml(Path(taxonomy_file))
    assert taxonomy["metadata"]["current_phase"] == 2
    assert taxonomy["metadata"]["redundancy_counter"] == 1

def test_path_validation(tmp_path):
    # Test invalid extension
    invalid_ext = str(tmp_path / "data.txt")
    with pytest.raises(ValueError, match="Extensão inválida"):
        server.register_candidate_papers(["paper1"], registry_file=invalid_ext)
        
    with pytest.raises(ValueError, match="Extensão inválida"):
        server.add_taxonomy_concept("cat", "concept", taxonomy_file=invalid_ext)
        
    # Test directory instead of file
    dir_path = str(tmp_path)
    with pytest.raises(ValueError, match="aponta para um diretório"):
        server.register_candidate_papers(["paper1"], registry_file=dir_path)
