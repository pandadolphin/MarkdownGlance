import ast
import copy
import json
import os
import unittest

from MarkdownGlance.preview.domain.contracts import RenderSettings

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BINDINGS = ("sublime-keymap", "sublime-mousemap")
PLATFORMS = ("Linux", "OSX", "Windows")
# Sublime names the "=" and "-" keys on macOS; the literal characters Linux and
# Windows accept never match there, so the OSX keymap must spell them out.
MACOS_KEY_NAMES = {"=": "equals", "-": "minus"}


def as_macos_key(key):
    prefix, plus, last = key.replace("ctrl+", "super+").rpartition("+")
    return prefix + plus + MACOS_KEY_NAMES.get(last, last)


def as_macos(bindings):
    macos = copy.deepcopy(bindings)
    for item in macos:
        item["keys"] = [as_macos_key(key) for key in item.get("keys", ())]
        item["modifiers"] = [
            modifier.replace("ctrl", "super") for modifier in item.get("modifiers", ())
        ]
        for name in ("keys", "modifiers"):
            if not item[name]:
                del item[name]
    return macos


class PackageIdentityTest(unittest.TestCase):
    def load(self, name):
        with open(os.path.join(ROOT, name), encoding="utf-8") as source:
            return json.load(source)

    def test_metadata_is_st4200_every_platform_and_dependency_free(self):
        metadata = self.load("docs/package-control-entry.json")
        self.assertEqual(metadata["name"], "MarkdownGlance")
        release = metadata["releases"][0]
        self.assertEqual(release["sublime_text"], ">=4200")
        self.assertEqual(release["platforms"], ["*"])
        self.assertIs(release["tags"], True)
        self.assertEqual(metadata["labels"], ["markdown", "preview"])
        # Package Control installs no library for this package; the absence of
        # the file is the declaration, and an empty one is dead metadata.
        self.assertFalse(os.path.exists(os.path.join(ROOT, "dependencies.json")))

    def test_public_command_and_key_context_namespaces_are_unique(self):
        commands = self.load("Default.sublime-commands")
        self.assertTrue(
            all(item["command"].startswith("mdglance_") for item in commands)
        )
        for platform in PLATFORMS:
            for suffix in BINDINGS:
                name = "Default ({}).{}".format(platform, suffix)
                for item in self.load(name):
                    self.assertTrue(item["command"].startswith("mdglance_"), name)
                    for context in item.get("context", ()):
                        self.assertTrue(context["key"].startswith("mdglance."), name)
                        self.assertIs(context["operand"], True)

    def test_platform_bindings_differ_only_by_macos_key_spelling(self):
        for suffix in BINDINGS:
            linux = self.load("Default (Linux).{}".format(suffix))
            self.assertNotEqual(as_macos(linux), linux, suffix)
            self.assertEqual(
                self.load("Default (Windows).{}".format(suffix)), linux, suffix
            )
            self.assertEqual(
                self.load("Default (OSX).{}".format(suffix)), as_macos(linux), suffix
            )

    def test_shipped_settings_keep_mermaid_opt_in(self):
        # The default settings file is what users actually get; a "true" here
        # sends diagram source to mermaid_server without anyone opting in.
        path = os.path.join(ROOT, "MarkdownGlance.sublime-settings")
        with open(path, encoding="utf-8") as source:
            shipped = source.read()
        self.assertIn('"enable_mermaid": false', shipped)
        self.assertNotIn('"enable_mermaid": true', shipped)
        self.assertFalse(RenderSettings().enable_mermaid)

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
