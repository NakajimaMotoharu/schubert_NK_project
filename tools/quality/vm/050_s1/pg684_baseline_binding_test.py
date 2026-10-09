"""Readonly profile literals and GC narrowness; no guest operations."""
import ast
import unittest
from pg684_completed_baseline import source


class BaselineTest(unittest.TestCase):
    def test_actual_completed_actor_and_current_twenty_one_fields(self):
        raw = source(); tree = ast.parse(raw)
        assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
        payload = ast.literal_eval(assignment.value)
        for literal in ('fa1cd96cc5110f8bb582d7befecb9fd13f66cea63f707b1a03db9e3d5287ef98',
                        'pg684-completed-baseline-v1', 'current_gc_after_known20(known,current)',
                        "old['parentPid1']", "==514", 'require(len(v)==21)',
                        'pg664-bootstrap-tools-v1', 'pg664-bootstrap-verify-v1', 'pg664-bootstrap-existing-v1',
                        "actor['ticks']=='11164505'", '095f6d1d7f8442b7b2b44ae59a4314f5'):
            self.assertIn(literal, payload)
        self.assertNotIn("old['pid1']", payload)
        self.assertNotIn("v['units']==old['units']and", payload)
        compile(raw, '<readonly host>', 'exec'); compile(payload, '<readonly guest>', 'exec')
        self.assertIn("'GC_SOURCE='", raw)
        self.assertNotIn('StartUnit', payload)
        self.assertNotIn('StopUnit', payload)
        self.assertNotIn('daemon-reload', payload)


if __name__ == '__main__':
    unittest.main()
