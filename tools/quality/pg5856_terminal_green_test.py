import unittest
import pg5856_terminal_green as target


class TerminalGreenInventoryTest(unittest.TestCase):
    def test_exact70_all_six_module_guards_eight_targets(self):
        from pg5540_snapshot_scratch_selected import ROOT
        total=0
        for module,classes in target.CASES.items():
            for cls in classes:
                path=ROOT/('src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk')/(cls.replace('.','/')+'.java')
                count=len(target.previous.previous.source_test_names(path));self.assertEqual(target.COUNTS[cls.rsplit('.',1)[1]],count);total+=count
        self.assertEqual(70,total);self.assertEqual(20,sum(map(len,target.CASES.values())))
        self.assertEqual(8,sum(map(len,target.TARGETS.values())))
        raw=target.runner_source();self.assertNotIn('failIfNoTests=false',raw);self.assertIn('len(physical)==1666',raw)


if __name__=='__main__':unittest.main()
