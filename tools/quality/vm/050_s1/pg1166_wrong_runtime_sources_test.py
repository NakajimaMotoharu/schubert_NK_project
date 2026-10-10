import ast
import unittest
from pg1166_wrong_runtime_sources import files,HASH


class WrongRuntimeTest(unittest.TestCase):
    def test_typed_heldentry_single_retirement_and_live_observation(self):
        v=files();j=v['Pg1166WrongRuntimeRetirement.java'];s=v['pg1166_wrong_runtime_refs.py'];ast.parse(s)
        self.assertEqual(j.count('runtime.unlinkEntry("pg1160-once-resume.conf")'),1)
        self.assertTrue('runtime.atExistingEntryHandle'in j);self.assertTrue('refs.check("removed")'in j)
        self.assertTrue('runtime.sync()'in j);self.assertTrue('wrongRuntimeRetired'in j)
        self.assertTrue(HASH in s);self.assertTrue("save('runtime-before.private',dropin)"in s)
        self.assertFalse('runtime.owned_prepare'in s);self.assertFalse('systemctl start'in s)
        self.assertTrue("if action=='removed':changed=True"in s)
        self.assertFalse("if action=='prepare':"in s)


if __name__=='__main__':unittest.main()
