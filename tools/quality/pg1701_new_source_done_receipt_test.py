"""Literal new-run independent oracle; reject foreign/failed/expired evidence."""
import ast
import copy
import datetime
import unittest
from pg1701_new_source_done_receipt import payload


class DoneTest(unittest.TestCase):
    def test_literal_receipt_and_each_field_rejection(self):
        tree = ast.parse(payload())
        nodes = [n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))
                 or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in
                 {'BINDING','CURRENT','FIELDS','ORACLE_SOURCE','GC'} for t in n.targets)]
        env = {}; exec(compile(ast.Module(body=nodes,type_ignores=[]),'<literal independent new Root oracle>','exec'),env)
        binding = {'boot':'3d69f5af6bac46b1a5407591c4a79a0d','invocation':'fe43e94b1fbf4886bb4ab3922fd16f9c',
                   'job':'106924','start':66941284515,'run':'02e941b9-1c52-4018-a193-63dd00b269af',
                   'cutoff':'2026-10-12T14:19:28.968927Z','activation':'40da389f-23fc-4ad4-a71b-cf72a6bd5a62'}
        self.assertEqual(binding, env['BINDING'])
        done = b'NKDONE1\n02e941b9-1c52-4018-a193-63dd00b269af\n2026-10-12T14:19:28.968927Z\n40da389f-23fc-4ad4-a71b-cf72a6bd5a62\n2026-10-12T14:29:29.000000Z\n0\n'
        stamp = int(datetime.datetime(2026,10,12,14,29,30,tzinfo=datetime.timezone.utc).timestamp()*1000000)
        common = {'_BOOT_ID':binding['boot'],'_PID':'1','_UID':'0','_COMM':'systemd',
                  'UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':binding['invocation'],
                  '__MONOTONIC_TIMESTAMP':'67541284515','__REALTIME_TIMESTAMP':str(stamp)}
        rows = [dict(common,__CURSOR='new-one',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',
                     JOB_ID='106924',JOB_TYPE='start',JOB_RESULT='done'),
                dict(common,__CURSOR='new-two',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.assertEqual(600, env['qualify'](binding,rows,done)['elapsedSeconds'])
        for key in binding:
            with self.subTest(binding=key), self.assertRaises((ValueError,TypeError)):
                env['qualify'](dict(binding,**{key:None}),rows,done)
        for key in common.keys()|{'__CURSOR','JOB_ID','JOB_TYPE','JOB_RESULT','MESSAGE_ID'}:
            bad = copy.deepcopy(rows); bad[0][key] = 'new-two' if key=='__CURSOR' else 'foreign'
            with self.subTest(row=key), self.assertRaises(ValueError): env['qualify'](binding,bad,done)
        for bad in [None,[],rows+[rows[0]],[dict(r,__MONOTONIC_TIMESTAMP='68741284516')for r in rows]]:
            with self.subTest(rows=bad), self.assertRaises(ValueError): env['qualify'](binding,bad,done)
        for bad in [None,b'',done[:-1],done.replace(b'\n0\n',b'\n1\n'),done.replace(b'40da389f',b'd28eead2')]:
            with self.subTest(done=bad), self.assertRaises((ValueError,UnicodeError)): env['qualify'](binding,rows,bad)


if __name__=='__main__': unittest.main()
