"""Whole emitted read-only namespace and current-cohort guards before any guest execution."""
import ast
import unittest
from pyflakes.api import check,checkPath
import pg5712_failed_cohort_full_capture as entry


class Capture(unittest.TestCase):
    def test_current_failed_source_sole_actor_and_all_preservation_guards(self):
        raw=entry.payload(entry.admission.live());tree=ast.parse(raw)
        self.assertEqual(0,check(raw,'<independent emitted reader>'))
        self.assertEqual(0,checkPath(entry.__file__))
        self.assertEqual(0,checkPath(__file__))
        self.assertIn(entry.admission.SOURCE,raw);self.assertIn(entry.admission.BOM,raw)
        self.assertIn(entry.admission.PUBLICATION,raw)
        self.assertIn("m['ExecMainStatus']=='30'",raw)
        self.assertIn("set(actors)=={'artemis.service'}",raw)
        self.assertIn("first['database']['rows']==second['database']['rows']",raw)
        self.assertIn("first['native']==second['native']",raw)
        self.assertIn("not second['database']['peers']",raw)
        self.assertIn("manager.UnrefUnit(unit)",raw)
        self.assertIn("'recoveryAuthorityIssued':False",raw)
        for node in ast.walk(tree):
            if isinstance(node,ast.List):
                literals=[n.value for n in node.elts if isinstance(n,ast.Constant)]
                self.assertNotIn('stop',literals);self.assertNotIn('start',literals);self.assertNotIn('daemon-reload',literals)


if __name__=='__main__':unittest.main()
