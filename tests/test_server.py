import json
import yaml
import pytest
from pathlib import Path
from theoretical_saturation_mcp import server

def test_register_candidate_papers(tmp_path):
    registry_file = str(tmp_path / "papers.json")
    
    # Test registering new papers
    result = server.add_papers({"paper1": "Title 1", "paper2": "Title 2"}, filepath=registry_file)
    assert "2 new papers registered" in result
    assert "0 already existed" in result
    
    # Verify file content
    registry = server.read_json(Path(registry_file))
    assert "paper1" in registry
    assert registry["paper1"]["status"] == "pending"
    assert registry["paper1"]["title"] == "Title 1"
    
    # Test registering duplicate paper
    result = server.add_papers({"paper2": "Title 2", "paper3": "Title 3"}, filepath=registry_file)
    assert "1 new papers registered" in result
    assert "1 already existed" in result

def test_update_paper_status(tmp_path):
    registry_file = str(tmp_path / "papers.json")
    
    # Initialize paper
    server.add_papers({"paper1": "Old Title"}, filepath=registry_file)
    
    # Update status
    result = server.update_paper("paper1", status="in_scope", title="My Paper", add_operation="extraction", filepath=registry_file)
    assert "Success" in result
    
    registry = server.read_json(Path(registry_file))
    assert registry["paper1"]["status"] == "in_scope"
    assert registry["paper1"]["title"] == "My Paper"
    assert "extraction" in registry["paper1"]["operations"]
    
    # Test remove operation
    server.update_paper("paper1", remove_operation="extraction", filepath=registry_file)
    registry = server.read_json(Path(registry_file))
    assert "extraction" not in registry["paper1"]["operations"]
    
    # Try updating non-existent
    result = server.update_paper("nonexistent", status="in_scope", filepath=registry_file)
    assert "Error" in result

def test_add_taxonomy_concept(tmp_path):
    taxonomy_file = str(tmp_path / "taxonomy.yaml")
    
    # Add new concept
    result = server.add_taxonomy_concept("methodology", "case_study", taxonomy_filepath=taxonomy_file)
    assert "Success" in result
    
    # Add another
    server.add_taxonomy_concept("methodology", "survey", taxonomy_filepath=taxonomy_file)
    
    # Verify file content
    taxonomy = server.read_yaml(Path(taxonomy_file))
    assert "case_study" in taxonomy["methodology"]
    assert "survey" in taxonomy["methodology"]
    
    # Try adding duplicate
    result = server.add_taxonomy_concept("methodology", "case_study", taxonomy_filepath=taxonomy_file)
    assert "already exists" in result

def test_log_audit_decision(tmp_path):
    audit_file = str(tmp_path / "log.yaml")
    
    # Log decision
    result = server.log_decision(
        paper_id="paper1",
        title="Test Paper",
        novelty=True,
        decision="included",
        justification="Highly relevant",
        log_filepath=audit_file
    )
    assert "Success" in result
    
    # Verify file content
    log = server.read_yaml(Path(audit_file))
    assert len(log) == 1
    assert log[0]["paperId"] == "paper1"
    assert log[0]["brought_novelty"] is True
    assert log[0]["decision"] == "included"

def test_update_metadata_state(tmp_path):
    taxonomy_file = str(tmp_path / "taxonomy.yaml")
    
    # Update state
    result = server.update_metadata_state(current_phase=2, redundancy_counter=1, taxonomy_filepath=taxonomy_file)
    assert "Success" in result
    
    # Verify file content
    taxonomy = server.read_yaml(Path(taxonomy_file))
    assert taxonomy["metadata"]["current_phase"] == 2
    assert taxonomy["metadata"]["redundancy_counter"] == 1

def test_path_validation(tmp_path):
    # Test invalid extension
    invalid_ext = str(tmp_path / "data.txt")
    with pytest.raises(ValueError, match="Invalid extension"):
        server.add_papers({"paper1": "Title"}, filepath=invalid_ext)
        
    with pytest.raises(ValueError, match="Invalid extension"):
        server.add_taxonomy_concept("cat", "concept", taxonomy_filepath=invalid_ext)
        
    # Test directory instead of file
    dir_path = str(tmp_path)
    with pytest.raises(ValueError, match="points to a directory"):
        server.add_papers({"paper1": "Title"}, filepath=dir_path)
