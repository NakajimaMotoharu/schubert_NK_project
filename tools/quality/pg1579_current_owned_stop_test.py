"""Independent literals and hostile generations for the actual current stop ABI."""
import ast
import copy
import datetime
import unittest
from pg1579_current_owned_stop_sources import sources
from pg1580_current_owned_stop_compile import compiler_source
from pg1581_current_owned_stop_dispatch import STAGE,source
from pg1582_current_stop_preflight import payload

class CurrentStopTest(unittest.TestCase):
    def test_current_literals_and_closed_dispatch(self):
        values=sources();self.assertEqual(len(values),14)
        java=values['Pg1579NativeStop.java']
        self.assertIn('Pg387TrustedDeployment.LABEL="PG1544"',java)
        self.assertIn('Pg387TrustedDeployment.SOURCE="4d6bcbddb417b76d27e52d5d9640752c300edccf"',java)
        self.assertIn('Path.of("/opt/schubert-nk/releases/0.1.0-PG1544")',java)
        self.assertIn('db.setReadOnly(true)',java)
        self.assertIn('db.rollback();db.close();lease.confirmClosed()',java)
        for name in ['pg1579_native_refs.py','pg1579_native_owned_stop.py']:
            self.assertIn('/proc/108847',values[name]);self.assertNotIn('702983',values[name])
        compiled=compiler_source();self.assertIn("release=W/'pg1544-release-v1'",compiled)
        self.assertIn('Pg1579OriginalTupleTest',compiled)
        dispatch=source();self.assertIn("'.requested'",dispatch)
        self.assertIn("'pg1580-frozen-v1.safe.json'",dispatch)
        self.assertIn("'pg1582-current-stop-preflight-v1.safe.json'",dispatch)
        self.assertIn("'Pg1579OriginalTupleTest','Pg1579StopLabelTest','Pg1579NativeArgumentTest','Pg1579NativeStop stop'",dispatch)
        self.assertNotIn('PG1292',dispatch+STAGE)
        self.assertIn('3d69f5af-6bac-46b1-a540-7591c4a79a0d',STAGE)
        self.assertIn('0.1.0-PG1544',STAGE)
        self.assertIn('pg1582-current-stop-preflight-v1',payload())

    def test_independent_root_receipt_every_binding(self):
        env={};exec(sources()['pg1579_parent_receipt.py'],env)
        done=b'NKDONE1\n15700a87-9117-4f63-a0ff-768dd604d0f1\n2026-10-11T21:18:59.040097Z\n9e706936-a3c9-4a09-bb66-e2b1e8bbef66\n2026-10-12T04:45:00.000000Z\n0\n'
        stamp=int(datetime.datetime(2026,10,12,4,45,1,tzinfo=datetime.timezone.utc).timestamp()*1000000)
        common={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'c52c914a72804a89b0fd5f252f6ac0fc','__MONOTONIC_TIMESTAMP':'32643431270','__REALTIME_TIMESTAMP':str(stamp)}
        rows=[dict(common,__CURSOR='fixture-one',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='50856',JOB_TYPE='start',JOB_RESULT='done'),dict(common,__CURSOR='fixture-two',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        self.assertEqual(env['completed'](rows,done)['elapsedSeconds'],600)
        for key in common.keys()|{'__CURSOR','JOB_ID','JOB_TYPE','JOB_RESULT','MESSAGE_ID'}:
            bad=copy.deepcopy(rows);bad[0][key]='fixture-two'if key=='__CURSOR'else'foreign'
            with self.assertRaises(ValueError):env['completed'](bad,done)
        for bad in [None,[],rows+[rows[0]],[dict(r,__MONOTONIC_TIMESTAMP='33843431271')for r in rows],[dict(r,JOB_RESULT='timeout')for r in rows]]:
            with self.assertRaises(ValueError):env['completed'](bad,done)
        for bad in [None,b'',done[:-1],done.replace(b'\n0\n',b'\n1\n'),done.replace(b'9e706936',b'841b507c')]:
            with self.assertRaises((ValueError,UnicodeError)):env['completed'](rows,bad)

    def test_four_generation_validation_before_any_stop(self):
        # Import declarations only: no privileged main, command, journal or stop.
        tree=ast.parse(sources()['pg1579_native_owned_stop.py'])
        names={'require','validate_live'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'EXPECTED','ORDER'}for t in n.targets)]
        from pg526_term_witness import FIELDS
        env={'FIELDS':FIELDS};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<current data-only generation guard>','exec'),env)
        owned={'caddy.service':('161708','b62723b53ece4420b783a627e3548012'),'schubert-nk-web.service':('159826','fb683eeb6d3b4e90b66c1576f9108a0c'),'schubert-nk-api.service':('158794','2111873a431743359c0627a8f5e394c8'),'artemis.service':('118964','6e745372ba4e4c7683cda767c607b93c')}
        order=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service']
        self.assertEqual(env['ORDER'],order);self.assertEqual(env['EXPECTED'],owned)
        captures={u:{}for u in order}
        for unit,(pid,inv)in owned.items():
            captures[unit]={k:'0'for k in FIELDS}
            captures[unit].update(MainPID=pid,InvocationID=inv,ActiveState='active',SubState='running',Job='',ControlPID='0',Result='success',Id=unit,LoadState='loaded')
        env['validate_live'](captures)
        for unit in owned:
            for key in ['MainPID','InvocationID','ActiveState','SubState','ControlPID','Job','Result','Id','LoadState','ExecMainCode','ExecMainStatus','ExecMainExitTimestampMonotonic']:
                bad=copy.deepcopy(captures);bad[unit][key]='foreign'
                with self.assertRaises(ValueError):env['validate_live'](bad)
            bad=copy.deepcopy(captures);bad[unit]['MainPID']=None
            with self.assertRaises(ValueError):env['validate_live'](bad)
        for bad in [None,{},dict(captures,**{'foreign.service':{}})]:
            with self.assertRaises(ValueError):env['validate_live'](bad)

if __name__=='__main__':unittest.main()
