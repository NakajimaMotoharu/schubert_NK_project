import ast
import unittest
from pg1242_fresh_ordinary_done_receipt import payload

class ActualParentOracleTest(unittest.TestCase):
    def test_actual_generated_oracle_accepts_only_new_binding_and_done(self):
        s = payload()
        tree = ast.parse(s)
        nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef)) or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {'BINDING','CURRENT','FIELDS','ORACLE_SOURCE','GC'} for t in n.targets)]
        env = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual new-day oracle>', 'exec'), env)
        binding = env['BINDING']
        done = ('NKDONE1\n9f651096-aef9-4fba-90b0-a653e99f035a\n2026-10-10T20:03:22.718197Z\n27accac0-c118-4c98-9244-02625a2d88a7\n2026-10-10T20:25:00.000000Z\n0\n').encode()
        common = {'_BOOT_ID':'cbca87383b244090b77cbf029677cdd6','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'2914e843f73d48dd93198dbdcae0f735','__MONOTONIC_TIMESTAMP':'62534139496','__REALTIME_TIMESTAMP':'1791663901000000'}
        rows = [dict(common, __CURSOR='a',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='100948',JOB_TYPE='start',JOB_RESULT='done'), dict(common,__CURSOR='b',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.assertEqual(env['qualify'](binding, rows, done)['elapsedSeconds'], 1300)
        for key,value in [('invocation','a14cc600a4fd4f2e9d8c4731ad9d754b'),('job','81093'),('start',51172132518),('cutoff','2026-10-10T12:40:27.396847Z')]:
            with self.assertRaises(ValueError):env['qualify'](dict(binding,**{key:value}),rows,done)
        for broken in [done.replace(b'\n0\n',b'\n1\n'), done.replace(b'27accac0',b'ada3f7ff')]:
            with self.assertRaises(ValueError):env['qualify'](binding,rows,broken)
        with self.assertRaises(ValueError):env['qualify'](binding,[],done)
        self.assertEqual(env['qualify_current'](env['GC']),'GC_CURRENT_NOT_COMPLETION_PROOF')

if __name__ == '__main__':unittest.main()
