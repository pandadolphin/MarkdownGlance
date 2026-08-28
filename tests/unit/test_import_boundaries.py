import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parents[3] / "preview"


class ImportBoundaryTest(unittest.TestCase):
    def test_pure_layers_do_not_import_sublime(self):
        for layer in ("domain", "renderer", "assets", "application"):
            for path in (ROOT / layer).glob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
                self.assertNotIn("sublime", imports, str(path))

    def test_production_syntax_parses_as_python_38(self):
        for path in ROOT.rglob("*.py"):
            ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
                feature_version=(3, 8),
            )
