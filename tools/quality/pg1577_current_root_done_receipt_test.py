"""Independent journal/DONE literal; actual new binding and old/timeout rejection."""
import ast
import copy
import datetime
import unittest
from pg1577_current_root_done_receipt import payload

class ReceiptTest(unittest.TestCase):
    def test_actual_oracle_literal_and_all_fields_foreign(self):
        tree=ast.parse(payload());nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'BINDING','CURRENT','FIELDS','ORACLE_SOURCE','GC'}for t in n.targets)]
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<new captured root receipt oracle>','exec'),env)
        done=b'NKDONE1\n15700a87-9117-4f63-a0ff-768dd604d0f1\n2026-10-11T21:18:59.040097Z\n9e706936-a3c9-4a09-bb66-e2b1e8bbef66\n2026-10-12T04:45:00.000000Z\n0\n'
        stamp=int(datetime.datetime(2026,10,12,4,45,1,tzinfo=datetime.timezone.utc).timestamp()*1000000)
        common={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'c52c914a72804a89b0fd5f252f6ac0fc','__MONOTONIC_TIMESTAMP':'32643431270','__REALTIME_TIMESTAMP':str(stamp)}
        rows=[dict(common,__CURSOR='independent-a',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='50856',JOB_TYPE='start',JOB_RESULT='done'),dict(common,__CURSOR='independent-b',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.assertEqual(env['qualify'](env['BINDING'],rows,done)['elapsedSeconds'],600)
        self.assertEqual(env['qualify_current'](env['GC']),'GC_CURRENT_NOT_COMPLETION_PROOF')
        for key in env['BINDING']:
            with self.assertRaises((ValueError,TypeError)):env['qualify'](dict(env['BINDING'],**{key:None}),rows,done)
        for key in common.keys()|{'__CURSOR','JOB_ID','JOB_TYPE','JOB_RESULT','MESSAGE_ID'}:
            bad=copy.deepcopy(rows);bad[0][key]='foreign'
            with self.assertRaises(ValueError):env['qualify'](env['BINDING'],bad,done)
        for bad in [None,[],rows+[rows[0]],[dict(r,__MONOTONIC_TIMESTAMP='33843431271')for r in rows],[dict(r,JOB_RESULT='timeout')for r in rows]]:
            with self.assertRaises(ValueError):env['qualify'](env['BINDING'],bad,done)
        for bad in [None,b'',done[:-1],done.replace(b'\n0\n',b'\n1\n'),done.replace(b'9e706936',b'841b507c')]:
            with self.assertRaises((ValueError,UnicodeError)):env['qualify'](env['BINDING'],rows,bad)

if __name__=='__main__':unittest.main()
