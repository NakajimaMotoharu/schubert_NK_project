import ast
import json
import unittest
from pyflakes.api import checkPath
import pg4862_current_preservation_readonly as role


class CurrentRead(unittest.TestCase):
    def test_actual_original_checks_and_functions_remain_unchanged(self):
        old = (role.W/role.PREVIOUS/'payload.private.py').read_text(); new = role.payload()
        original = {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(old).body if isinstance(n,ast.FunctionDef)}
        fresh = {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(original,fresh)
        self.assertNotIn('save=base/'+repr(role.PREVIOUS),new)
        self.assertIn('save=base/'+repr(role.SLOT),new)
        for text in ["sum(p.endswith('.exec')for p in full11['native'])==72", "len(full11['rows'])==24", "'nativeCandidateCredit':False", "'genuineCompletion':FRESH_DONE", "current_normal_or_gc(terminal,current_bootstrap)"]:
            self.assertIn(text,new)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))

    def test_no_stale_candidate_or_old_before_override(self):
        m=json.loads((role.W/role.PREVIOUS/'manifest.safe.json').read_bytes())
        self.assertEqual(role.BEFORE,m['result']['beforeSha256'])
        self.assertNotEqual(role.SOURCE,'04bbdb73b532537e3546191d72dee913b17629a0')
        self.assertEqual(11,len(role.FIELDS));self.assertEqual(11,len(set(role.FIELDS)))


if __name__ == '__main__':unittest.main()
