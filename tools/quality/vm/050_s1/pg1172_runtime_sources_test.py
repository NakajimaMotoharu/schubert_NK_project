import ast
import unittest
from pg1172_runtime_sources import files,BASE,HASH


class CorrectRuntimeTest(unittest.TestCase):
    def test_current_same_directory_correct_effective_declaration(self):
        v=files();s=v['pg1172_runtime_refs.py'];ast.parse(s)
        for p in [BASE,HASH,'runtime.owned_prepare(','left[1]+\' --resume \'+runtime.RUN_ID','m[:6]==runtime_parent[:6]',"str(RUNTIME/runtime.NAME)",'runtime_tree()','manager.UnrefUnit(u)']:
            self.assertTrue(p in s,p)
        w=v['pg1172_runtime_writer.py'];ast.parse(w)
        self.assertTrue("NAME='zz-pg1160-once-resume.conf'"in w)
        self.assertFalse('os.mkdir('in w)
        self.assertTrue('pg1172-runtime-resume-v1'in v['Pg1172RuntimeResume.java'])


if __name__=='__main__':unittest.main()
