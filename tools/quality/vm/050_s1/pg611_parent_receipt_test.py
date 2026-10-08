"""Current cohort PID1/DONE independent literal identity/time/job negatives."""
import copy
import unittest
from pg611_parent_receipt import completed


class ReceiptTest(unittest.TestCase):
    def setUp(self):
        base={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'5a1acaa0c35e484c979401e3b6dfb36a','__MONOTONIC_TIMESTAMP':'87761979588','__REALTIME_TIMESTAMP':'1791475059000000'}
        self.rows=[dict(base,__CURSOR='literal1',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='87863',JOB_TYPE='start',JOB_RESULT='done'),dict(base,__CURSOR='literal2',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.done=b'NKDONE1\n3a53b979-fa01-47dd-92a6-7b26affcfb5c\n2026-10-08T15:32:46.368375Z\n970bbce1-6bba-4db0-ace1-680ee7dfde92\n2026-10-08T15:57:38.735146Z\n0\n'

    def test_success_and_every_identity_job_time_mismatch(self):
        self.assertEqual(completed(self.rows,self.done)['endMonotonicUs'],87761979588)
        for key in self.rows[0]:
            for value in (None,'' if key=='__CURSOR'else 'foreign'):
                bad=copy.deepcopy(self.rows);bad[0][key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):completed(bad,self.done)
            bad=copy.deepcopy(self.rows);del bad[0][key]
            with self.assertRaises(ValueError):completed(bad,self.done)
        for bad in (None,{},[],self.rows[:1],self.rows+self.rows):
            with self.assertRaises(ValueError):completed(bad,self.done)
        for done in (None,b'',self.done.replace(b'NKDONE1',b'NKBAD01'),self.done.replace(b'\n0\n',b'\n10\n'),self.done.replace(b'3a53b979',b'4a53b979')):
            with self.assertRaises(ValueError):completed(self.rows,done)
        for stamp in ('86264628080','88064628082'):
            bad=copy.deepcopy(self.rows);bad[0]['__MONOTONIC_TIMESTAMP']=stamp
            with self.assertRaises(ValueError):completed(bad,self.done)


if __name__=='__main__':unittest.main()
