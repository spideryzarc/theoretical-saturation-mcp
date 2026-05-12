import pytest
from pathlib import Path
from theoretical_saturation_mcp import server


@pytest.fixture(autouse=True)
def patch_file_paths(tmp_path, monkeypatch):
    """Redirect all global file paths to isolated tmp_path locations."""
    monkeypatch.setattr(server, "PAPERS_FILE", str(tmp_path / "papers.json"))
    monkeypatch.setattr(server, "TAXONOMY_FILE", str(tmp_path / "taxonomy.yaml"))
    monkeypatch.setattr(server, "LOG_FILE", str(tmp_path / "log.yaml"))


# --- Papers ---

def test_add_papers_registers_new(tmp_path):
    result = server.add_papers({"p1": "Title 1", "p2": "Title 2"})
    assert "2 new papers registered" in result
    assert "0 already existed" in result

    registry = server.read_json(Path(server.PAPERS_FILE))
    assert registry["p1"]["status"] == "pending"
    assert registry["p1"]["title"] == "Title 1"


def test_add_papers_skips_duplicates():
    server.add_papers({"p1": "Title 1"})
    result = server.add_papers({"p1": "Title 1", "p2": "Title 2"})
    assert "1 new papers registered" in result
    assert "1 already existed" in result


def test_update_paper_status_and_operations():
    server.add_papers({"p1": "Old Title"})
    result = server.update_paper("p1", status="in_scope", title="New Title", add_operation="snowball")
    assert "Success" in result

    registry = server.read_json(Path(server.PAPERS_FILE))
    assert registry["p1"]["status"] == "in_scope"
    assert registry["p1"]["title"] == "New Title"
    assert "snowball" in registry["p1"]["operations"]


def test_update_paper_remove_operation():
    server.add_papers({"p1": "T"})
    server.update_paper("p1", add_operation="snowball")
    server.update_paper("p1", remove_operation="snowball")

    registry = server.read_json(Path(server.PAPERS_FILE))
    assert "snowball" not in registry["p1"]["operations"]


def test_update_paper_not_found():
    result = server.update_paper("ghost", status="in_scope")
    assert "Error" in result


def test_get_papers_filtered():
    server.add_papers({"p1": "T1", "p2": "T2"})
    server.update_paper("p1", status="in_scope")

    result = server.get_papers(status="in_scope")
    ids = [p["id"] for p in result]
    assert "p1" in ids
    assert "p2" not in ids


def test_get_actionable_papers():
    server.add_papers({"p1": "T1", "p2": "T2"})
    server.update_paper("p1", status="in_scope", add_operation="snowball")
    server.update_paper("p2", status="in_scope")

    result = server.get_actionable_papers(status="in_scope", missing_operation="snowball")
    assert result == ["p2"]


# --- Taxonomy: add ---

def test_add_taxonomy_concept_creates_category():
    result = server.add_taxonomy_concept("methods", "genetic_algorithm")
    assert "Success" in result

    taxonomy = server.read_yaml(Path(server.TAXONOMY_FILE))
    assert "genetic_algorithm" in taxonomy["methods"]


def test_add_taxonomy_concept_duplicate():
    server.add_taxonomy_concept("methods", "genetic_algorithm")
    result = server.add_taxonomy_concept("methods", "genetic_algorithm")
    assert "already exists" in result


# --- Taxonomy: remove concept ---

def test_remove_taxonomy_concept():
    server.add_taxonomy_concept("methods", "genetic_algorithm")
    result = server.remove_taxonomy_concept("methods", "genetic_algorithm")
    assert "Success" in result

    taxonomy = server.read_yaml(Path(server.TAXONOMY_FILE))
    assert "genetic_algorithm" not in taxonomy["methods"]


def test_remove_taxonomy_concept_not_found():
    server.add_taxonomy_concept("methods", "genetic_algorithm")
    result = server.remove_taxonomy_concept("methods", "nonexistent")
    assert "Warning" in result


def test_remove_taxonomy_concept_category_not_found():
    result = server.remove_taxonomy_concept("ghost_category", "concept")
    assert "Error" in result


# --- Taxonomy: update concept ---

def test_update_taxonomy_concept():
    server.add_taxonomy_concept("methods", "Fuzzy Logic")
    result = server.update_taxonomy_concept("methods", "Fuzzy Logic", "fuzzy_logic")
    assert "Success" in result

    taxonomy = server.read_yaml(Path(server.TAXONOMY_FILE))
    assert "fuzzy_logic" in taxonomy["methods"]
    assert "Fuzzy Logic" not in taxonomy["methods"]


def test_update_taxonomy_concept_not_found():
    server.add_taxonomy_concept("methods", "genetic_algorithm")
    result = server.update_taxonomy_concept("methods", "nonexistent", "new_name")
    assert "Warning" in result


# --- Taxonomy: remove category ---

def test_remove_taxonomy_category():
    server.add_taxonomy_concept("methods", "genetic_algorithm")
    result = server.remove_taxonomy_category("methods")
    assert "Success" in result

    taxonomy = server.read_yaml(Path(server.TAXONOMY_FILE))
    assert "methods" not in taxonomy


def test_remove_taxonomy_category_not_found():
    result = server.remove_taxonomy_category("ghost")
    assert "Warning" in result


def test_remove_taxonomy_category_metadata_protected():
    result = server.remove_taxonomy_category("metadata")
    assert "Error" in result


# --- Taxonomy: get concepts ---

def test_get_taxonomy_concepts_specific_category():
    server.add_taxonomy_concept("methods", "genetic_algorithm")
    server.add_taxonomy_concept("methods", "tabu_search")
    result = server.get_taxonomy_concepts("methods")
    assert "genetic_algorithm" in result
    assert "tabu_search" in result


def test_get_taxonomy_concepts_all_categories():
    server.add_taxonomy_concept("methods", "genetic_algorithm")
    server.add_taxonomy_concept("constraints", "capacity_limit")
    result = server.get_taxonomy_concepts()
    assert "methods" in result
    assert "constraints" in result
    assert "metadata" not in result


def test_get_taxonomy_concepts_empty_category():
    result = server.get_taxonomy_concepts("nonexistent")
    assert result == []


# --- Metadata state ---

def test_update_metadata_state():
    result = server.update_metadata_state(current_phase=2, redundancy_counter=3)
    assert "Success" in result

    taxonomy = server.read_yaml(Path(server.TAXONOMY_FILE))
    assert taxonomy["metadata"]["current_phase"] == 2
    assert taxonomy["metadata"]["redundancy_counter"] == 3


# --- Log decision ---

def test_log_decision():
    result = server.log_decision(
        paper_id="p1",
        title="Some Paper",
        brought_novelty=True,
        novelty_description="Introduced constraint X",
        decision="Added to taxonomy",
        discover_phase="Phase 1",
    )
    assert "Success" in result

    log = server.read_yaml(Path(server.LOG_FILE))
    assert len(log) == 1
    assert log[0]["paperId"] == "p1"
    assert log[0]["brought_novelty"] is True
    assert log[0]["discover_phase"] == "Phase 1"


# --- Path validation ---

def test_invalid_extension_raises(tmp_path):
    with pytest.raises(ValueError, match="Invalid extension"):
        server.validate_path(tmp_path / "data.txt", (".json",))


def test_directory_raises(tmp_path):
    with pytest.raises(ValueError, match="points to a directory"):
        server.validate_path(tmp_path, (".json",))
