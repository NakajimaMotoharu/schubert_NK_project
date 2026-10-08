"""Literal independent normal/foreign/missing/null/duplicate/timeout vectors."""
import copy,unittest
from pg556_parent_receipt import completed


class Test(unittest.TestCase):
    def setUp(self):
        base={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'075ad6644b284056a6cccf7af252519b','__MONOTONIC_TIMESTAMP':'44938901762','__REALTIME_TIMESTAMP':'1791432240714124'}
        self.rows=[dict(base,__CURSOR='literal1',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='59402',JOB_TYPE='start',JOB_RESULT='done'),dict(base,__CURSOR='literal2',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.done=b'NKDONE1\nb7e73994-b951-4696-bdd1-cfbc8a10e734\n2026-10-08T04:03:00.714124Z\n12f1af04-180e-405c-8738-853bbd875443\n2026-10-08T04:03:59.714124Z\n0\n'

    def test_literal_success(self):
        self.assertEqual(completed(self.rows,self.done)['elapsedSeconds'],60)

    def test_foreign_missing_duplicate_null_timeout(self):
        for key in self.rows[0]:
            for value in(None,'' if key=='__CURSOR'else 'foreign'):
                bad=copy.deepcopy(self.rows);bad[0][key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):completed(bad,self.done)
            bad=copy.deepcopy(self.rows);del bad[0][key]
            with self.assertRaises(ValueError):completed(bad,self.done)
        for bad in(None,{},[],self.rows[:1],self.rows+self.rows):
            with self.assertRaises(ValueError):completed(bad,self.done)
        for done in(None,b'',self.done.replace(b'NKDONE1',b'NKBAD01'),self.done.replace(b'\n0\n',b'\n10\n'),self.done.replace(b'b7e73994',b'a7e73994')):
            with self.assertRaises(ValueError):completed(self.rows,done)
        for stamp in('44878901761','46678901763'):
            bad=copy.deepcopy(self.rows);bad[0]['__MONOTONIC_TIMESTAMP']=stamp
            with self.assertRaises(ValueError):completed(bad,self.done)


if __name__=='__main__':unittest.main()
