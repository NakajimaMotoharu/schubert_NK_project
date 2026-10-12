"""Current generated run literals and foreign/timeout/DONE/null negative vectors."""
import ast
import copy
import datetime
import unittest
from pg1601_current_newrun_done_receipt import payload

class NewRunReceiptTest(unittest.TestCase):
    def test_independent_actual_binding_and_every_field_rejection(self):
        tree=ast.parse(payload());nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'BINDING','CURRENT','FIELDS','ORACLE_SOURCE','GC'}for t in n.targets)]
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<current newrun actual oracle>','exec'),env)
        expected={'boot':'3d69f5af6bac46b1a5407591c4a79a0d','invocation':'e4d891c38dde4e16a5c848e23ef3f83c','job':'71184','start':38365395523,'run':'0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','cutoff':'2026-10-12T06:23:13.176261Z','activation':'d28eead2-941c-4b97-9747-1758c0809e29'}
        self.assertEqual(env['BINDING'],expected)
        done=b'NKDONE1\n0be226b1-bbb7-43d3-aa9e-59d0bda70f9a\n2026-10-12T06:23:13.176261Z\nd28eead2-941c-4b97-9747-1758c0809e29\n2026-10-12T06:33:00.000000Z\n0\n'
        stamp=int(datetime.datetime(2026,10,12,6,33,1,tzinfo=datetime.timezone.utc).timestamp()*1000000)
        common={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'e4d891c38dde4e16a5c848e23ef3f83c','__MONOTONIC_TIMESTAMP':'38965395523','__REALTIME_TIMESTAMP':str(stamp)}
        rows=[dict(common,__CURSOR='fixture-new-one',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='71184',JOB_TYPE='start',JOB_RESULT='done'),dict(common,__CURSOR='fixture-new-two',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.assertEqual(env['qualify'](expected,rows,done)['elapsedSeconds'],600)
        for key in expected:
            with self.assertRaises((ValueError,TypeError)):env['qualify'](dict(expected,**{key:None}),rows,done)
        for key in common.keys()|{'__CURSOR','JOB_ID','JOB_TYPE','JOB_RESULT','MESSAGE_ID'}:
            bad=copy.deepcopy(rows);bad[0][key]='fixture-new-two'if key=='__CURSOR'else'foreign'
            with self.assertRaises(ValueError):env['qualify'](expected,bad,done)
        for bad in [None,[],rows+[rows[0]],[dict(r,__MONOTONIC_TIMESTAMP='40165395524')for r in rows],[dict(r,JOB_RESULT='timeout')for r in rows]]:
            with self.assertRaises(ValueError):env['qualify'](expected,bad,done)
        for bad in [None,b'',done[:-1],done.replace(b'\n0\n',b'\n1\n'),done.replace(b'd28eead2',b'9e706936')]:
            with self.assertRaises((ValueError,UnicodeError)):env['qualify'](expected,rows,bad)

if __name__=='__main__':unittest.main()
