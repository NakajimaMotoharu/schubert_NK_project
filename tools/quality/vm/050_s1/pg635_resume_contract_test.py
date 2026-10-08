"""Independent declared bytes and full-field mutation matrix; no Root operations."""
import copy
import hashlib
from pathlib import Path
import unittest
from pg635_resume_contract import fixed_dropin,changed_only,unit_sources
from pg604_unit_sources_test import GOLDEN

BASE=b'[Service]\nExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED -cp fixed dev.codex.schubert.nk.batch.file.MorningProcessMain\n'
ARGV='/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false --enable-native-access=ALL-UNNAMED -cp fixed dev.codex.schubert.nk.batch.file.MorningProcessMain'
NATIVE=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+ARGV.encode()+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
RUN='e49243d5-de84-4714-8612-6912ddc17e9e'
TARGET='/run/systemd/system/schubert-nk-morning-controller.service.d/pg635-once-resume.conf'
EXPECTED=b'# SSC228: fixed one-run same-cutoff resume; retire only after genuine terminal.\n[Service]\nExecStart=\nExecStart='+ARGV.encode()+b' --resume '+RUN.encode()+b'\n'


def record(path,argv,ran=False):
    return ('{ path='+path+' ; argv[]='+argv+' ; ignore_errors=no ; start_time=['+('Thu 2026-10-08 15:00:00 UTC'if ran else'n/a')+'] ; stop_time=['+('Thu 2026-10-08 15:00:01 UTC'if ran else'n/a')+'] ; pid='+('88'if ran else'0')+' ; code='+('exited'if ran else'(null)')+' ; status='+('0'if ran else'0/0')+' }')


def pair():
    before={key:{'literal':[True,None,'retain']}for key in 'backup bootstrapOldProofs bootstrapTools credentials dependencies native oldProofs originals parentPid1 pid1Stop rows startup current approval'.split()}
    before['units']={'caddy.service':{'Result':'success','ExecMainCode':'1','ExecMainStatus':'0'}}
    before['runtime']=None
    before['configuration']={
        'schubert-nk-morning-controller.service':{'ExecStart':record('/usr/bin/java',ARGV,True),'DropInPaths':'/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf','User':'root','TimeoutStartUSec':'30min'},
        'caddy.service':{'ExecStart':record('/usr/bin/caddy','/usr/bin/caddy run --config /etc/caddy/Caddyfile',True),'DropInPaths':'fixed','User':'caddy','TimeoutStartUSec':'30s'}}
    before['caddyPre']=record('/usr/bin/caddy','/usr/bin/caddy validate --config /etc/caddy/Caddyfile',True)
    before['unitFiles']={'/etc/sealed':{'metadata':[1,2,0,0,33188,1,4,5,6],'sha256':'old'}}
    after=copy.deepcopy(before);after['configuration']['schubert-nk-morning-controller.service']['ExecStart']=record('/usr/bin/java',ARGV+' --resume '+RUN)
    after['configuration']['schubert-nk-morning-controller.service']['DropInPaths']+=' '+TARGET
    after['runtime']={'metadata':[28,99,0,0,33188,1,len(EXPECTED),7,7],'sha256':hashlib.sha256(EXPECTED).hexdigest()}
    after['unitFiles'][TARGET]=copy.deepcopy(after['runtime'])
    return before,after


class Resume(unittest.TestCase):
    def test_fixed_seven_history_reset_only_ssc229(self):
        for unit in ('schubert-nk-backup.service','schubert-nk-api.service','schubert-nk-web.service','artemis.service',
                     'schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-bootstrap-admin.service'):
            b,a=pair();b['configuration'][unit]={'ExecStart':record('/usr/bin/fixed','/usr/bin/fixed same',True),'User':'fixed'}
            a['configuration'][unit]={'ExecStart':record('/usr/bin/fixed','/usr/bin/fixed same'),'User':'fixed'}
            if unit in ('schubert-nk-inbox-inspector.service','schubert-nk-bootstrap-admin.service'):
                with self.subTest(unit=unit),self.assertRaises(ValueError):changed_only(b,a,EXPECTED)
            else:
                with self.subTest(unit=unit):self.assertTrue(changed_only(b,a,EXPECTED))
                a['configuration'][unit]['ExecStart']=a['configuration'][unit]['ExecStart'].replace('pid=0','pid=77')
                with self.assertRaises(ValueError):changed_only(b,a,EXPECTED)

    def test_exact_bytes_and_rejected_base_native(self):
        self.assertEqual(fixed_dropin(BASE,NATIVE),EXPECTED)
        for bad in (None,'',b'',BASE+BASE,BASE.replace(b'/usr/bin/java',b'/bin/foreign'),BASE.replace(b' -cp',b' --resume other -cp'),BASE.replace(b' -cp',b' -javaagent:other -cp')):
            with self.assertRaises(ValueError):fixed_dropin(bad,NATIVE)
        for bad in (None,'',b'',NATIVE+b'User=other\n',NATIVE.replace(b'append=false',b'append=true'),NATIVE.replace(b'parent.exec',b'other.exec')):
            with self.assertRaises(ValueError):fixed_dropin(BASE,bad)

    def test_full_protected_join_and_effective_declaration(self):
        b,a=pair();self.assertTrue(changed_only(b,a,EXPECTED))
        for key in b.keys()-{'configuration','runtime','unitFiles','caddyPre'}:
            b,a=pair();a[key]={'changed':1}
            with self.subTest(key=key),self.assertRaises(ValueError):changed_only(b,a,EXPECTED)
        for unit in pair()[0]['configuration']:
            for key in pair()[0]['configuration'][unit]:
                b,a=pair();a['configuration'][unit][key]='foreign'
                with self.assertRaises(ValueError):changed_only(b,a,EXPECTED)
        b,a=pair();a['unitFiles']['/etc/sealed']['sha256']='changed'
        with self.assertRaises(ValueError):changed_only(b,a,EXPECTED)
        for index,value in [(2,1),(3,1),(4,33152),(5,2),(6,1)]:
            b,a=pair();a['runtime']['metadata'][index]=value;a['unitFiles'][TARGET]=copy.deepcopy(a['runtime'])
            with self.assertRaises(ValueError):changed_only(b,a,EXPECTED)

    def test_caddy_reload_pair_only_not_mixed(self):
        b,a=pair();a['configuration']['caddy.service']['ExecStart']=record('/usr/bin/caddy','/usr/bin/caddy run --config /etc/caddy/Caddyfile')
        with self.assertRaises(ValueError):changed_only(b,a,EXPECTED)
        a['caddyPre']=record('/usr/bin/caddy','/usr/bin/caddy validate --config /etc/caddy/Caddyfile')
        self.assertTrue(changed_only(b,a,EXPECTED))
        b,a=pair();a['caddyPre']=record('/usr/bin/caddy','/usr/bin/caddy validate --config /etc/caddy/Caddyfile')
        with self.assertRaises(ValueError):changed_only(b,a,EXPECTED)

    def test_source_paths_and_actual_wiring(self):
        rows=copy.deepcopy(GOLDEN);old=unit_sources(rows,False);self.assertEqual(len(old),18)
        rows['schubert-nk-morning-controller.service']['DropInPaths']+=' '+TARGET
        self.assertEqual(set(unit_sources(rows,True)),set(old)|{TARGET})
        rows['schubert-nk-morning-controller.service']['DropInPaths']+=' '+TARGET
        with self.assertRaises(ValueError):unit_sources(rows,True)
        r=Path(__file__).resolve().parent;java=(r/'Pg635ResumePreparation.java').read_text();refs=(r/'pg635_resume_refs.py').read_text()
        self.assertIn('TOOLS.resolve("pg635_resume_refs.py").toString(),mode,Integer.toString(pid)',java)
        self.assertIn("set_config('application_name','PG635-fixed-resume',false)",java)
        self.assertIn("a.application_name='PG635-fixed-resume'",refs)
        self.assertIn("baseline['parentPid1']",refs);self.assertNotIn("baseline['pid1']",refs)
        self.assertIn("if not changed:require(same_value(value['configuration'],baseline['configuration']))",refs)
        self.assertIn("require(same_value(before,baseline))",refs)
        self.assertEqual(refs.count("command(['/usr/bin/systemctl','daemon-reload']"),1)
        self.assertNotIn('repair_empty_runtime',refs)
        self.assertIn('dir_fd=fds[3]',refs);self.assertIn("'system.posix_acl_default'",refs)


if __name__=='__main__':unittest.main()
