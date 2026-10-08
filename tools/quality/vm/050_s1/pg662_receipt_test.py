"""BOOT662002 literal current PID1/DONE oracle; raw/foreign/null/duplicate negatives."""
import datetime
import json
import unittest
from pg662_sources import receipt, join

ns={};exec(compile(receipt(),'<current receipt>','exec'),ns)
joined={};exec(compile(join().replace('from pg662_parent_receipt import completed',''),'<raw join>','exec'),{**ns,'json':json},joined)


class Test(unittest.TestCase):
    def rows(self):
        base={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd',
              'UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'095f6d1d7f8442b7b2b44ae59a4314f5',
              '__MONOTONIC_TIMESTAMP':'109694780700','__REALTIME_TIMESTAMP':str(int(datetime.datetime.fromisoformat('2026-10-08T22:03:11+00:00').timestamp()*1000000))}
        return [{**base,'__CURSOR':'literal-a','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','JOB_ID':'111752','JOB_TYPE':'start','JOB_RESULT':'done'},
                {**base,'__CURSOR':'literal-b','MESSAGE_ID':'7ad2d189f7e94e70a38c781354912448'}]

    def done(self):
        return b'NKDONE1\n601297d0-a8ba-47da-852b-0ffeae409965\n2026-10-08T21:33:23.332578Z\nad15ac4a-8d8e-4970-bcb3-2e000050ce77\n2026-10-08T22:03:10.738020Z\n0\n'

    def test_literal_and_raw_join(self):
        got=ns['completed'](self.rows(),self.done())
        self.assertEqual(got['elapsedSeconds'],1793.235293)
        raw=b'\n'.join(json.dumps(r).encode()for r in self.rows())+b'\n'
        # Execute module with one shared global namespace: functions resolve unique/completed there.
        env=dict(ns);exec(compile(join().replace('from pg662_parent_receipt import completed',''),'<join>','exec'),env)
        self.assertEqual(env['completed_journal'](raw,self.done())[1],got)
        for bad in(None,b'',b'[]\n',b'{"x":1,"x":2}\n',raw[:-1]):
            with self.assertRaises(ValueError):env['completed_journal'](bad,self.done())

    def test_foreign_missing_duplicate_boundary(self):
        for key,bad in({'_PID':'9','_UID':'999','_COMM':'java','INVOCATION_ID':'old','JOB_ID':'old',
                         'JOB_RESULT':'failed','__MONOTONIC_TIMESTAMP':'109701545408','__CURSOR':None}).items():
            rows=self.rows();rows[0][key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):ns['completed'](rows,self.done())
        for rows in(None,[],self.rows()+[self.rows()[0]]):
            with self.assertRaises(ValueError):ns['completed'](rows,self.done())
        for done in(None,self.done().replace(b'601297d0',b'old297d0'),self.done().replace(b'\n0\n',b'\n1\n')):
            with self.assertRaises(ValueError):ns['completed'](self.rows(),done)


if __name__=='__main__':unittest.main()
