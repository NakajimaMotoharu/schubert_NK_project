"""Actual full seal uses independent current terminal/rows, four identities and normal Ref finally."""
import ast
import unittest
from pg2025_fresh_resume_full_live_seal import payload


class FullSeal(unittest.TestCase):
    def test_actual_three_boundaries_and_complete_globals(self):
        raw=payload({'boot':'3d69f5af6bac46b1a5407591c4a79a0d','invocation':'1eb0d77ce4704e7481ecc07beddcdf0c','job':'187092','start':106318294326,'run':'4148e3e8-f107-431a-ab27-d6e6d1f1772e','cutoff':'2026-10-12T18:20:32.598894Z','activation':'e31b627c-c0e2-4120-bd64-c0777479e800'})
        tree=ast.parse(raw)
        constants={t.id:n.value.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.value,ast.Constant)for t in n.targets if isinstance(t,ast.Name)}
        self.assertTrue("'normalUnit0or10':True"in constants['GUARD'])
        self.assertTrue('newSkippedSteps' in constants['ORACLE']and "protected_count']==4"in constants['ORACLE'])
        self.assertTrue('pg2015-completed-run-fresh-resume-once-v1/before.private.json'in raw)
        self.assertTrue('PG1846'in raw and 'pg1846-manifest.sig'in raw)
        self.assertTrue('current==capture()'in raw and 'manager.UnrefUnit(unit)'in raw)
        self.assertTrue('configurationFields' in raw and 'signedArtifacts' in raw)


if __name__=='__main__':unittest.main()
