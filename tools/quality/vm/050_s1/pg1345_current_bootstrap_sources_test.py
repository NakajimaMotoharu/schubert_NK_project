"""Source tuple and actual sent helpers independently pinned before compilation."""
import ast
import unittest
import pg1345_current_bootstrap_sources as p

class Test(unittest.TestCase):
    def test_literal_current_tuple_and_closing_contract(self):
        values = p.files('b' * 64)
        raw = '\n'.join(values.values())
        for expected in (p.SOURCE, 'ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99',
                         'd2e3a86f-27a4-4c2a-be21-b512eebf1216',
                         '841b507c-2713-4ffe-8882-68f5fb3f87f5', '75132489604',
                         'cbca8738-3b24-4090-b77c-bf029677cdd6', '==634'):
            self.assertIn(expected, raw)
        for old in ('40ef6e894573d2ffab1d1732124960f9c98d5f97', 'pg978', 'PG932',
                    'Pg983', 'pg963', '202927375873', 'cc9ed874'):
            self.assertNotIn(old, raw)
        self.assertIn('lease.confirmClosed()', values['Pg1345BootstrapExisting.java'])
        helper = values['pg1345_bootstrap_existing.py']
        tree = ast.parse(helper)
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main']
        self.assertEqual(1, len(functions))
        global_names = {x for n in functions[0].body if isinstance(n, ast.Global) for x in n.names}
        self.assertEqual({'MODE', 'SAVE'}, global_names)
        self.assertIn("for selected in (path,closing):", values['pg1345_bootstrap_contract.py'])
        self.assertIn('pg1334_parent_receipt.py', values)

if __name__ == '__main__':
    unittest.main()
