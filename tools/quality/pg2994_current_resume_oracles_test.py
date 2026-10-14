"""Independent existing normal/foreign/null/replay fixtures against final current exports."""
import ast
import json
import unittest
from unittest.mock import patch
import pg2021_fresh_resume_terminal_receipt_test as terminal_fixture
import pg2023_fresh_resume_rows_oracle_test as rows_fixture
from pg1446_current_cold_stage import W
import pg2992_current_resume_terminal as terminal
import pg2994_current_resume_rows as rows
from pg2366_current_resume_rows import qualify


class CurrentTerminal(terminal_fixture.Receipt):
    def setUp(self):
        self.addCleanup(patch.stopall)
        actual = json.loads((W / 'pg2990-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
        raw = terminal.payload({**actual['binding'], 'rootPid': actual['rootPid']})
        nodes = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name in ['_normal_classify', 'classify']]
        self.assertEqual(2, len(nodes))
        scope = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual current terminal pure exports>', 'exec'), scope)
        patch.object(terminal_fixture, 'classify', scope['classify']).start()
        patch.object(terminal_fixture, 'payload', lambda b: terminal.payload({**b, 'rootPid': 122976})).start()


class CurrentRows(rows_fixture.Rows):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch.object(rows_fixture, 'qualify', qualify).start()
        patch.object(rows_fixture, 'payload', rows.payload).start()

    def fixture(self):
        old, new = super().fixture()
        old['schubert.inbox_inspection_progress'][0]['protected_count'] = 10
        new['schubert.inbox_inspection_progress'][0]['protected_count'] = 10
        return old, new


if __name__ == '__main__':
    unittest.main()
