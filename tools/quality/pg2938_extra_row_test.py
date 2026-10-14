"""No Main compile/VM use; target counter from real executions, not synthetic flags."""
import unittest
import pg2938_extra_row_selected as p


class ExtraRowInputs(unittest.TestCase):
    def test_real_agent_target_and_current_full(self):
        raw=p.server()
        for s in ['source-full-PG2930','-javaagent:',"'targetClassFour100':True",'NativeCoverageXml471','BackupFailureSnapshot',"counters[k]['missed']==0"]:
            self.assertIn(s,raw)
        self.assertTrue(all('/src/main/'not in n for n in p.FILES))


if __name__=='__main__':unittest.main()
