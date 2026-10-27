import ast
import unittest
from pathlib import Path

SOURCE = Path("Network-Toolkit-V22.py")
CODE = SOURCE.read_text(encoding="utf-8")
TREE = ast.parse(CODE)

class V22UITests(unittest.TestCase):
    def test_python_syntax(self):
        compile(CODE, str(SOURCE), "exec")

    def test_all_22_menu_entries(self):
        for number in range(1, 23):
            self.assertIn(f'("{number}",', CODE)

    def test_exit_option_is_13(self):
        self.assertIn('if choice == "13":', CODE)

    def test_grouped_menu_categories(self):
        for category in (
            "NETWORK TOOLS",
            "REPORTS & EXPORT",
            "WEB & SECURITY",
            "VALIDATION & PRACTICE",
            "PASSWORD TOOLS",
        ):
            self.assertIn(category, CODE)

    def test_required_functions_exist(self):
        functions = {
            node.name for node in ast.walk(TREE)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        required = {
            "main",
            "safe_public_url",
            "password_strength_checker",
            "export_json_report",
            "ssl_certificate_checker",
            "security_headers_checker",
            "http_status_checker",
        }
        self.assertTrue(required.issubset(functions))

    def test_action_mapping_contains_expected_options(self):
        main = next(
            node for node in TREE.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        )
        actions = next(
            node.value for node in main.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "actions"
                for target in node.targets
            )
        )
        mapping = {
            key.value: value.id
            for key, value in zip(actions.keys, actions.values)
            if isinstance(key, ast.Constant)
            and isinstance(key.value, str)
            and isinstance(value, ast.Name)
        }
        self.assertEqual(mapping.get("1"), "check_ip_address")
        self.assertEqual(mapping.get("11"), "http_header_checker")
        self.assertEqual(mapping.get("14"), "password_strength_checker")
        self.assertEqual(mapping.get("19"), "ssl_certificate_checker")
        self.assertEqual(mapping.get("22"), "export_json_report")
        self.assertNotIn("13", mapping)

if __name__ == "__main__":
    unittest.main(verbosity=2)
