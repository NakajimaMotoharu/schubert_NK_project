"""Independent literal matrices; management test0 ProductionPT."""
import copy
from pathlib import Path
import unittest
from pg543_retirement_contract import UNITS, FIELDS, CONFIG, MORNING, CADDY, NATIVE, RUNTIME, validate_snapshot, configurations, phase_action, release_metadata, table_names, same_units


def execution(argv, supplement=('Wed 2026-10-07 20:08:51 UTC','Wed 2026-10-07 20:08:52 UTC','320189','exited','0')):
    a,b,c,d,e = supplement
    return '{ path=/usr/bin/java ; argv[]='+argv+' ; ignore_errors=no ; start_time=['+a+'] ; stop_time=['+b+'] ; pid='+c+' ; code='+d+' ; status='+e+' }'


def fixture():
    units={u:{k:'' for k in FIELDS} for u in UNITS}
    for u,row in units.items():row.update(Id=u,LoadState='loaded',ActiveState='inactive',MainPID='0',ControlPID='0',Job='')
    conf={u:{k:'fixed-'+k for k in CONFIG} for u in UNITS}
    for row in conf.values():row['ExecStart']=execution('/usr/bin/java fixed'); row['DropInPaths']=''
    conf[MORNING].update(ExecStart=execution('/usr/bin/java native --resume 91a748b4-1abe-484c-9682-44f46429b324'),DropInPaths=NATIVE+' '+RUNTIME)
    result={k:{} for k in ('backup','bootstrapOldProofs','bootstrapTools','configuration','credentials','dependencies','native','oldProofs','originals','parentPid1','pid1Stop','rows','runtime','startup','units')}
    result.update(units=units,configuration=conf)
    return result


class Contract(unittest.TestCase):
    def test_all_major_fields_remain_exact(self):
        old=fixture()['units'];self.assertTrue(same_units(old,copy.deepcopy(old)))
        for u in UNITS:
            for k in FIELDS:
                for fault in ('foreign',None,True):
                    bad=copy.deepcopy(old);bad[u][k]=fault
                    with self.assertRaises(ValueError):same_units(old,bad)
    def test_both_independent_schema_catalogs(self):
        names=['answers','app_logs','app_users','async_jobs','audio_files','auth_sessions','batch_runs','entry_audio_links','games','inbox_inspection_progress','log_cleanup_progress','login_ip_attempts','media_assets','mq_outbox','notifications','questions','request_inbox','script_entries','script_files','speakers']
        web=['pending_context_revocations','web_http_sessions','web_log_outbox','web_receipt_references']
        good={**{'schubert.'+n:[] for n in names},**{'schubert_web_session.'+n:[] for n in web}}
        self.assertTrue(table_names(good))
        for key in good:
            bad=copy.deepcopy(good);del bad[key]
            with self.assertRaises(ValueError):table_names(bad)
            bad=copy.deepcopy(good);bad[key]=None
            with self.assertRaises(ValueError):table_names(bad)
        for name in ('public.web_http_sessions','schubert_web_session.foreign','schubert.answers;drop table x','unknown'):
            with self.assertRaises(ValueError):table_names({**good,name:[]})
        with self.assertRaises(ValueError):table_names(None)

    def test_release_role_not_effective_unit(self):
        good=[1,2,0,986,0o100640,1,1836,1,2];self.assertTrue(release_metadata(good))
        for index,value in ((2,999),(3,0),(3,981),(4,0o100644),(4,0o040640),(5,2),(6,0),(6,16385),(1,None)):
            bad=good.copy();bad[index]=value
            with self.assertRaises(ValueError):release_metadata(bad)
        for bad in (None,good[:-1],good+[0]):
            with self.assertRaises(ValueError):release_metadata(bad)

    def test_closed_schema(self):
        good=fixture(); self.assertTrue(validate_snapshot(good))
        for group in ('configuration','units'):
            for name in UNITS:
                bad=copy.deepcopy(good); del bad[group][name]
                with self.assertRaises((ValueError,KeyError)):validate_snapshot(bad)
            for name in ('foreign.service','schubert-nk-expiry.service','schubert-nk-bootstrap.service'):
                bad=copy.deepcopy(good); bad[group][name]=copy.deepcopy(next(iter(bad[group].values())))
                with self.assertRaises(ValueError):validate_snapshot(bad)
        for u in UNITS:
            for field in FIELDS:
                for value in (None,False,1,[]):
                    bad=copy.deepcopy(good);bad['units'][u][field]=value
                    with self.assertRaises(ValueError):validate_snapshot(bad)
            for field in CONFIG:
                bad=copy.deepcopy(good);bad['configuration'][u][field]=None
                with self.assertRaises(ValueError):validate_snapshot(bad)
        for key in good:
            bad=copy.deepcopy(good);bad[key]=None
            with self.assertRaises(ValueError):validate_snapshot(bad)

    def test_finite_reload_delta(self):
        old=fixture()['configuration'];new=copy.deepcopy(old)
        new[MORNING].update(ExecStart=execution('/usr/bin/java native'),DropInPaths=NATIVE)
        pre=execution('/usr/bin/java validate');expected=('/usr/bin/java','/usr/bin/java native','no')
        self.assertTrue(configurations(old,new,expected,pre,pre))
        empty=('n/a','n/a','0','(null)','0/0')
        new[CADDY]['ExecStart']=execution('/usr/bin/java fixed',empty)
        self.assertTrue(configurations(old,new,expected,pre,execution('/usr/bin/java validate',empty)))
        with self.assertRaises(ValueError):configurations(old,new,expected,pre,pre)
        for u in UNITS:
            new[u]['ExecStart']=execution('/usr/bin/java native'if u==MORNING else'/usr/bin/java fixed',empty)
        self.assertTrue(configurations(old,new,expected,pre,execution('/usr/bin/java validate',empty)))
        new=copy.deepcopy(old);new[MORNING].update(ExecStart=execution('/usr/bin/java native'),DropInPaths=NATIVE)
        for u in UNITS:
            for field in CONFIG:
                bad=copy.deepcopy(new);bad[u][field]='foreign'
                with self.assertRaises(ValueError):configurations(old,bad,expected,pre,pre)
        for u in UNITS:
            for index,value in enumerate(('foreign','foreign','99','killed','9')):
                supplement=['Wed 2026-10-07 20:08:51 UTC','Wed 2026-10-07 20:08:52 UTC','320189','exited','0'];supplement[index]=value
                bad=copy.deepcopy(new);argv='/usr/bin/java native' if u==MORNING else '/usr/bin/java fixed'
                bad[u]['ExecStart']=execution(argv,tuple(supplement))
                with self.assertRaises(ValueError):configurations(old,bad,expected,pre,pre)
        for group in (old,new):
            bad=copy.deepcopy(group);bad['foreign.service']=copy.deepcopy(group[CADDY])
            with self.assertRaises(ValueError):configurations(bad,new,expected,pre,pre) if group is old else configurations(old,bad,expected,pre,pre)

    def test_phase_and_held_entry(self):
        self.assertEqual(phase_action('READY','before'),'READY')
        self.assertEqual(phase_action('READY','removed'),'VALIDATED')
        self.assertEqual(phase_action('VALIDATED','release'),'CLOSED')
        self.assertEqual(phase_action('READY','release',True),'CLOSED')
        for state,action in (('READY','release'),('VALIDATED','before'),('VALIDATED','removed'),('CLOSED','release'),('UNKNOWN','removed')):
            with self.assertRaises(ValueError):phase_action(state,action)
        with self.assertRaises(ValueError):phase_action('READY','removed',True)
        java=(Path(__file__).parent/'Pg543RuntimeRetirement.java').read_text()
        self.assertEqual(java.count('runtime.unlinkEntry('),1)
        self.assertEqual(java.count('"daemon-reload"'),1)
        held=java.index('runtime.atExistingEntryHandle(');unlink=java.index('runtime.unlinkEntry(')
        self.assertLess(held,unlink);self.assertLess(unlink,java.index('return Boolean.TRUE;',held))
        self.assertLess(java.index('db.rollback();db.close();'),java.index('refs.release();'))
        self.assertNotIn('Pg387TrustedDeployment.sync(Path.of("/run/',java)


if __name__=='__main__':unittest.main()
