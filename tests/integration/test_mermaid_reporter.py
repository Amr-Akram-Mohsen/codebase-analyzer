"""
Integration tests for the Mermaid Diagram Generator.
"""

from pathlib import Path

from codebase_analyzer.core.model import AnalysisResult, Module
from codebase_analyzer.reporting.mermaid import generate_mermaid_diagram


def test_generate_mermaid_diagram(tmp_path: Path) -> None:
    # Set up some dummy modules
    modules = [
        Module(path="app/domains/user/models.py", qualified_name="app.domains.user.models", classes=[], functions=[], imports=[]),
        Module(path="app/domains/user/service.py", qualified_name="app.domains.user.service", classes=[], functions=[], imports=[]),
        Module(path="app/web/routes/user.py", qualified_name="app.web.routes.user", classes=[], functions=[], imports=[]),
        Module(path="app/infrastructure/db/session.py", qualified_name="app.infrastructure.db.session", classes=[], functions=[], imports=[]),
    ]
    
    # User service imports User models and DB session
    # Web routes imports User service
    graph = {
        "app.domains.user.models": [],
        "app.domains.user.service": ["app.domains.user.models", "app.infrastructure.db.session"],
        "app.web.routes.user": ["app.domains.user.service"],
        "app.infrastructure.db.session": [],
    }
    
    result = AnalysisResult(project_root="/dummy", modules=modules, findings=[])
    
    out_file = tmp_path / "architecture.md"
    generate_mermaid_diagram(result, graph, str(out_file))
    
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    
    # Check that it contains mermaid blocks
    assert "```mermaid" in content
    assert "graph TD" in content
    
    # Check that the components were correctly aggregated to 3 levels
    # app.domains.user.models and app.domains.user.service -> app.domains.user
    assert 'app_domains_user["app.domains.user"]' in content
    assert 'app_web_routes["app.web.routes"]' in content
    assert 'app_infrastructure_db["app.infrastructure.db"]' in content
    
    # Check that the edges are correctly mapped between aggregated components
    # app.web.routes -> app.domains.user
    assert "app_web_routes --> app_domains_user" in content
    # app.domains.user -> app.infrastructure.db
    assert "app_domains_user --> app_infrastructure_db" in content
