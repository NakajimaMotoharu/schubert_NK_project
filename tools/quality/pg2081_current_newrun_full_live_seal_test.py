"""Whole closure plus independent guards attached after positive body binding."""
import ast
import unittest
from pg2081_current_newrun_full_live_seal import payload


class Seal(unittest.TestCase):
    def test_independent_guards_and_current_admission_rows(self):
        binding={'boot':'3d69f5af6bac46b1a5407591c4a79a0d','invocation':'2c37fef2a2ff48e7b6a05cfc23f84c19','job':'204748','start':113070840714,'run':'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','cutoff':'2026-10-13T03:08:18.452473Z','activation':'9026b2ab-bb42-49cd-a2bd-4c661049dce3','rootPid':588342}
        raw=payload(binding);tree=ast.parse(raw)
        values={t.id:n.value.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.value,ast.Constant)for t in n.targets if isinstance(t,ast.Name)}
        self.assertTrue("binding.get('run')=='4148e3e8-f107-431a-ab27-d6e6d1f1772e'"in values['GUARD'])
        self.assertTrue("binding.get('activation')=='e31b627c-c0e2-4120-bd64-c0777479e800'"in values['GUARD'])
        self.assertTrue('newBackupSteps'in values['ORACLE']and '_selectors'in values['ORACLE'])
        for marker in ['pg2072-current-noargs-newrun-once-v1/before.private.json','current==capture()','manager.UnrefUnit(unit)','configurationFields','signedArtifacts']:
            self.assertTrue(marker in raw,marker)


if __name__=='__main__':unittest.main()
