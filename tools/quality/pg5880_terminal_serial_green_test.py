import unittest
import pg5880_terminal_serial_green as target


class LegalSync83InventoryTest(unittest.TestCase):
    def test_exact83_existing_suites_no_same_session_reentry(self):
        from pg5540_snapshot_scratch_selected import ROOT
        from pg5800_rollback_green import source_test_names
        total=0
        for module,classes in target.CASES.items():
            for cls in classes:
                p=ROOT/('src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk')/(cls.replace('.','/')+'.java');count=len(source_test_names(p));self.assertEqual(target.COUNTS[cls.rsplit('.',1)[1]],count);total+=count
        self.assertEqual(83,total);self.assertEqual(22,sum(map(len,target.CASES.values())))
        self.assertEqual(8,sum(map(len,target.TARGETS.values())))
        raw=target.runner_source();self.assertNotIn('failIfNoTests=false',raw);self.assertIn('len(physical)==1666',raw)


if __name__=='__main__':unittest.main()
