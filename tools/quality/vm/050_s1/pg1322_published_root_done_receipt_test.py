import ast
import datetime
import unittest
from pg1322_published_root_done_receipt import payload


class CurrentPublishedRootReceiptTest(unittest.TestCase):
    def test_actual_oracle_independent_success_and_foreign_timeout_failure(self):
        code=payload();tree=ast.parse(code)
        nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'BINDING','CURRENT','FIELDS','ORACLE_SOURCE','GC'}for t in n.targets)]
        env={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual newsource receipt oracle>','exec'),env)
        done=b'NKDONE1\nd2e3a86f-27a4-4c2a-be21-b512eebf1216\n2026-10-10T23:30:23.481632Z\n841b507c-2713-4ffe-8882-68f5fb3f87f5\n2026-10-10T23:40:00.000000Z\n0\n'
        stamp=int(datetime.datetime(2026,10,10,23,40,1,tzinfo=datetime.timezone.utc).timestamp()*1000000)
        common={'_BOOT_ID':'cbca87383b244090b77cbf029677cdd6','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'400b2e34105149ff8f3a11c21da0be6a','__MONOTONIC_TIMESTAMP':'74254946447','__REALTIME_TIMESTAMP':str(stamp)}
        rows=[dict(common,__CURSOR='a',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='120359',JOB_TYPE='start',JOB_RESULT='done'),dict(common,__CURSOR='b',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.assertEqual(env['qualify'](env['BINDING'],rows,done)['elapsedSeconds'],600)
        for field,value in [('invocation','2914e843f73d48dd93198dbdcae0f735'),('job','100948'),('start',61234139496),('cutoff','2026-10-10T20:03:22.718197Z')]:
            with self.assertRaises(ValueError):env['qualify'](dict(env['BINDING'],**{field:value}),rows,done)
        for broken in [done.replace(b'\n0\n',b'\n1\n'),done.replace(b'841b507c',b'27accac0')]:
            with self.assertRaises(ValueError):env['qualify'](env['BINDING'],rows,broken)
        for broken in [[],[dict(r,__MONOTONIC_TIMESTAMP='75454946448')for r in rows],[dict(r,JOB_RESULT='timeout')for r in rows]]:
            with self.assertRaises(ValueError):env['qualify'](env['BINDING'],broken,done)
        self.assertEqual(env['qualify_current'](env['GC']),'GC_CURRENT_NOT_COMPLETION_PROOF')


if __name__=='__main__':unittest.main()
