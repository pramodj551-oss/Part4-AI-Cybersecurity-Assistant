import ast
from pathlib import Path


PROTECTED_ENTRYPOINTS = (
    Path("app.py"),
    Path("pages/Chat.py"),
    Path("pages/Incident_Search.py"),
    Path("pages/Knowledge_Base.py"),
    Path("pages/Settings.py"),
)


def _active_auth_calls(source: str) -> set[str]:
    tree = ast.parse(source)
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"require_auth", "render_logout"}:
                calls.add(node.func.id)
    return calls


def _auth_imported(source: str) -> bool:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "src.auth":
            imported = {alias.name for alias in node.names}
            if {"require_auth", "render_logout"}.issubset(imported):
                return True
    return False


def test_all_streamlit_entrypoints_enforce_authentication():
    missing: list[str] = []

    for path in PROTECTED_ENTRYPOINTS:
        source = path.read_text(encoding="utf-8")
        calls = _active_auth_calls(source)
        if not _auth_imported(source) or not {"require_auth", "render_logout"}.issubset(calls):
            missing.append(str(path))

    assert not missing, (
        "Protected Streamlit entry points must import and actively call "
        f"require_auth() and render_logout(): {missing}"
    )
