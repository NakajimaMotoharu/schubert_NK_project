"""Literal actual current PID1/RootDONE vectors, unknown/null/duplicate rejection."""
import datetime
import json
import unittest
from pg737_sources import receipt,join


class ReceiptTest(unittest.TestCase):
    def namespace(self):
        ns={};exec(compile(receipt(),'<current genuine PID1>', 'exec'),ns)
        raw=join().replace('from pg737_parent_receipt import completed','')
        exec(compile(raw,'<raw journal join>', 'exec'),ns)
        return ns

    def rows(self):
        base={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd',
              'UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'2aff8ecf3b7d4d15b24a8af0f73a8745',
              '__MONOTONIC_TIMESTAMP':'129343844863','__REALTIME_TIMESTAMP':str(int(datetime.datetime.fromisoformat('2026-10-09T03:30:41+00:00').timestamp()*1000000))}
        return [{**base,'__CURSOR':'literal-a','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','JOB_ID':'132812','JOB_TYPE':'start','JOB_RESULT':'done'},
                {**base,'__CURSOR':'literal-b','MESSAGE_ID':'7ad2d189f7e94e70a38c781354912448'}]

    def done(self):
        return b'NKDONE1\n55ac70e7-0180-4c32-8c91-5a379ebedf24\n2026-10-09T03:00:51.014287Z\nab8895ca-4fb1-440d-b174-bc9f1f27505a\n2026-10-09T03:30:40.608594Z\n0\n'

    def test_literal_and_raw_join(self):
        ns=self.namespace();got=ns['completed'](self.rows(),self.done())
        self.assertEqual(1794.547089,got['elapsedSeconds'])
        raw=b'\n'.join(json.dumps(r).encode()for r in self.rows())+b'\n'
        self.assertEqual(got,ns['completed_journal'](raw,self.done())[1])
        for bad in (None,b'',b'[]\n',b'{"x":1,"x":2}\n',raw[:-1]):
            with self.assertRaises(ValueError):ns['completed_journal'](bad,self.done())

    def test_each_unknown_boundary_null_duplicate(self):
        ns=self.namespace()
        for key,bad in {'_PID':'9','_UID':'999','_COMM':'java','INVOCATION_ID':'old','JOB_ID':'old',
                        'JOB_RESULT':'failed','__MONOTONIC_TIMESTAMP':'129349297775','__CURSOR':None}.items():
            rows=self.rows();rows[0][key]=bad
            with self.assertRaises(ValueError):ns['completed'](rows,self.done())
        for rows in (None,[],self.rows()+[self.rows()[0]]):
            with self.assertRaises(ValueError):ns['completed'](rows,self.done())
        for done in (None,self.done().replace(b'55ac70e7',b'oldc70e7'),self.done().replace(b'\n0\n',b'\n1\n')):
            with self.assertRaises(ValueError):ns['completed'](self.rows(),done)


if __name__=='__main__':unittest.main()
