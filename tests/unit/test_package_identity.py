import ast
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class PackageIdentityTest(unittest.TestCase):
    def load(self, name):
        with open(os.path.join(ROOT, name), encoding="utf-8") as source:
            return json.load(source)

    def test_metadata_is_linux_st4200_and_dependency_free(self):
        metadata = self.load("docs/package-control-entry.json")
        self.assertEqual(metadata["name"], "MarkdownGlance")
        release = metadata["releases"][0]
        self.assertEqual(release["sublime_text"], ">=4200")
        self.assertEqual(release["platforms"], ["linux"])
        self.assertIs(release["tags"], True)
        self.assertEqual(self.load("dependencies.json")["*"][">=4200"], [])

    def test_public_command_and_key_context_namespaces_are_unique(self):
        commands = self.load("Default.sublime-commands")
        self.assertTrue(
            all(item["command"].startswith("mdglance_") for item in commands)
        )
        keymap = self.load("Default (Linux).sublime-keymap")
        self.assertTrue(all(item["command"].startswith("mdglance_") for item in keymap))
        for item in keymap:
            for context in item.get("context", ()):
                self.assertTrue(context["key"].startswith("mdglance."))
                self.assertIs(context["operand"], True)

    def test_runtime_selector_is_python_38_compatible(self):
        with open(os.path.join(ROOT, ".python-version"), encoding="ascii") as source:
            self.assertEqual(source.read().strip(), "3.8")

    def test_plugin_link_commands_accept_sublime_event_argument(self):
        path = os.path.join(ROOT, "preview", "adapter", "commands.py")
        with open(path, encoding="utf-8") as source:
            module = ast.parse(source.read(), path)
        classes = {
            node.name: node for node in module.body if isinstance(node, ast.ClassDef)
        }
        for name in ("MdglanceNavigateCommand", "MdglanceOpenRelativeCommand"):
            run = next(
                node
                for node in classes[name].body
                if isinstance(node, ast.FunctionDef) and node.name == "run"
            )
            self.assertIn("event", [argument.arg for argument in run.args.args])


if __name__ == "__main__":
    unittest.main()
