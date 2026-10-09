"""Literal actual current PID1/RootDONE vectors, unknown/null/duplicate rejection."""
import datetime
import json
import unittest
from pg768_sources import assemble
from pg768_sources_test import fixture

def receipt():return assemble(*fixture())['receipt']
def join():return assemble(*fixture())['join']


class ReceiptTest(unittest.TestCase):
    def namespace(self):
        ns={};exec(compile(receipt(),'<current genuine PID1>', 'exec'),ns)
        raw=join().replace('from pg768_parent_receipt import completed','')
        exec(compile(raw,'<raw journal join>', 'exec'),ns)
        return ns

    def rows(self):
        base={'_BOOT_ID':'cc9ed8747f4f450ea1888de1e42c8441','_PID':'1','_UID':'0','_COMM':'systemd',
              'UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'e4093109ab234700b61dd45711126e4e',
              '__MONOTONIC_TIMESTAMP':'138900000000','__REALTIME_TIMESTAMP':str(int(datetime.datetime.fromisoformat('2026-10-09T06:10:01+00:00').timestamp()*1000000))}
        return [{**base,'__CURSOR':'literal-a','MESSAGE_ID':'39f53479d3a045ac8e11786248231fbf','JOB_ID':'142602','JOB_TYPE':'start','JOB_RESULT':'done'},
                {**base,'__CURSOR':'literal-b','MESSAGE_ID':'7ad2d189f7e94e70a38c781354912448'}]

    def done(self):
        return b'NKDONE1\n9de2d03c-28c7-4647-97d9-c66ace06048c\n2026-10-09T05:42:22.532331Z\n021111b4-6de5-4733-917d-5ac176240ffc\n2026-10-09T06:10:00.000000Z\n0\n'

    def test_literal_and_raw_join(self):
        ns=self.namespace();got=ns['completed'](self.rows(),self.done())
        self.assertEqual(1659.214115,got['elapsedSeconds'])
        raw=b'\n'.join(json.dumps(r).encode()for r in self.rows())+b'\n'
        self.assertEqual(got,ns['completed_journal'](raw,self.done())[1])
        for bad in (None,b'',b'[]\n',b'{"x":1,"x":2}\n',raw[:-1]):
            with self.assertRaises(ValueError):ns['completed_journal'](bad,self.done())

    def test_each_unknown_boundary_null_duplicate(self):
        ns=self.namespace()
        for key,bad in {'_PID':'9','_UID':'999','_COMM':'java','INVOCATION_ID':'old','JOB_ID':'old',
                        'JOB_RESULT':'failed','__MONOTONIC_TIMESTAMP':'139040785886','__CURSOR':None}.items():
            rows=self.rows();rows[0][key]=bad
            with self.assertRaises(ValueError):ns['completed'](rows,self.done())
        for rows in (None,[],self.rows()+[self.rows()[0]]):
            with self.assertRaises(ValueError):ns['completed'](rows,self.done())
        for done in (None,self.done().replace(b'9de2d03c',b'old2d03c'),self.done().replace(b'\n0\n',b'\n1\n')):
            with self.assertRaises(ValueError):ns['completed'](self.rows(),done)


if __name__=='__main__':unittest.main()
