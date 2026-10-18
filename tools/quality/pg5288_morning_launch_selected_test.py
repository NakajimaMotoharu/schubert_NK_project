import re
import unittest
import pg5288_morning_launch_selected as role


class MorningLaunchScope(unittest.TestCase):
    def test_related39_cases_four_new_suites28_cases(self):
        folder=role.selected.ROOT/'src/schubert-nk-batch/src/test/java'
        actual={}
        for name in role.RELATED:
            raw=(folder/(name.replace('.','/')+'.java')).read_text()
            cases=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',raw)
            self.assertEqual(len(cases),raw.count('@Test'))
            self.assertEqual(len(cases),len(set(cases)))
            actual[name.rpartition('.')[2]]=len(cases)
        self.assertEqual(actual,{'MorningNewRunAdmissionTest':12,'MorningResumeAdmissionTest':11,
            'MorningStartupLaunchOwnerTest':3,'MorningStartupLaunchOwnerAdmissionTest':2,'MorningProcessMainTest':11})
        self.assertEqual(sum(actual.values()),39)
        self.assertEqual(set(role.RELATED)&set(role.previous.extra_suites()),{'dev.codex.schubert.nk.batch.file.MorningResumeAdmissionTest'})
        self.assertEqual(len(role.extra_suites()),93)

    def test_nested_db_classes_semantic_outers_not_assumed_semantic(self):
        role.configure()
        for name in ('MorningNewRunAdmission','MorningResumeAdmission'):
            self.assertIn(name+'$1',role.OUTERS)
            self.assertIn(name,role.DEBUG)
            self.assertNotIn(name,role.OUTERS)
        self.assertEqual(len(role.selected.EXTRA_CHANGED),48)
        self.assertEqual(len(role.selected.EXTRA_DEBUG),148)


if __name__=='__main__':unittest.main()
