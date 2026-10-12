"""Inspect actual complete payload, not a stub or old successful observation."""
import ast
import unittest
from pyflakes.api import check
import pg1639_completed_current_preflight as p


class ReadonlyCurrentTest(unittest.TestCase):
    def test_complete_generated_scope_and_current_identity(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual completed current before>'))
        ast.parse(raw)
        for literal in ['3d69f5af-6bac-46b1-a540-7591c4a79a0d', '0.1.0-PG1544', 'e36d39f470bedf445e182f03e926c4c22252ef37952fde5b9a12614e60b0f07c', 'd28eead2-941c-4b97-9747-1758c0809e29', '39951854181', 'len(rows)==24', "==after['runtime']", "==after['native']", 'pg1639-completed-current-before-v1']:
            self.assertIn(literal, raw)
        for operation in ['systemctl start', 'systemctl stop', 'daemon-reload', 'StartupPermitFiles', 'INSERT INTO', 'UPDATE schubert']:
            self.assertNotIn(operation, raw)
        self.assertIn("'formalAccepted':False", raw)


if __name__ == '__main__':
    unittest.main()
