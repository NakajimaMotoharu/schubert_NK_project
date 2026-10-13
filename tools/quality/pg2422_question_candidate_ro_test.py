import unittest
from pyflakes.api import check
from pg2421_question_candidate_ro_compile import compiler
from pg2422_question_candidate_ro_dispatch import source,STAGE
from pg2426_question_candidate_ro_post import payload
from pg2412_question_unused_sources import production


class Readonly(unittest.TestCase):
    def test_full_operational_dependency_and_new_slots(self):
        for raw in [compiler(),source()]:
            compile(raw,'<actual candidateRO source>','exec')
            for v in ['pg2418-question-unused-independent-post-v1','pg2420']:
                self.assertIn(v,raw)
            for v in ['pg2150-normal-unused-independent-post-v1','pg2144-current-normal-unused-tools-v1']:
                self.assertNotIn(v,raw)
        self.assertIn('pg2421-',compiler())
        self.assertIn('pg2428',compiler())
        self.assertIn('0.1.0-PG2126',source())
        self.assertIn('pg2422-',source())
        self.assertIn('pg2422-fixed-stage-v1',STAGE)

    def test_exact_mount_readonly_not_current_and_all_post_globals(self):
        raw=payload({'actualExit':0,'candidateSource':production(),'signatureVerified':True,
                     'manifestSha256':'a'*64,'signatureSha256':'b'*64})
        self.assertEqual(0,check(raw,'<whole RO post>'))
        for v in ['pg2424-question-candidate-host-ro-v1','candidateHostReadonlyVerified',
                  "'--mountpoint','/opt/schubert-nk/releases/0.1.0-PG2428'","'ro'in mounts and 'rw'not in mounts"]:
            self.assertIn(v,raw)
        self.assertNotIn('mount --bind',raw)
        self.assertNotIn('StartUnit(',raw)


if __name__=='__main__':
    unittest.main()
