import unittest
import pg5828_isolation_green as target


class IsolationPlanTest(unittest.TestCase):
    def test_explicit_six_module_inventory_and_non_vacuous_targets(self):
        self.assertEqual(6,len(target.CASES))
        self.assertEqual(18,sum(map(len,target.CASES.values())))
        self.assertEqual(66,sum(target.COUNTS[c.rsplit('.',1)[1]]for s in target.CASES.values()for c in s))
        self.assertEqual(8,sum(map(len,target.TARGETS.values())))
        raw=target.runner_source()
        for text in('!=66','!=18','len(physical)==1666','len(target_counters)==8','failIfNoTests=false'):
            if text=='failIfNoTests=false':self.assertNotIn(text,raw)
            else:self.assertIn(text,raw)
        self.assertNotIn('lan_server',raw);self.assertNotIn('systemctl',raw)


if __name__=='__main__':unittest.main()
