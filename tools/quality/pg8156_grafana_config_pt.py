"""Offline Grafana public profile data; no daemon, network, account or secret operations."""
import configparser
import copy
import datetime
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest
import pg8140_prometheus_config_pt as strict
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
DIRECTORY='src/deployment/monitoring/grafana/'
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8156-grafana-config-pt-v1'
BASELINE='0ad037e111dc88ec4661e6ea76b10e5794045b1e'
FILES=('grafana.ini.template','datasources-debug.yml.template','datasources-standard.yml.template')
SPEC='evidence/01_PT/018_NK-OPS-001/1735_Grafana配布設定_単体テスト仕様書.md'
PROM='src/deployment/monitoring/prometheus/debug-arguments.json.template'
# Entire independent oracle from1735/official key semantics, not from production methods.
INI={
    'paths':{'data':'/var/lib/schubert-nk/monitoring/grafana',
             'provisioning':'/etc/schubert-nk/monitoring/grafana/provisioning'},
    'server':{'protocol':'http','http_addr':'127.0.0.1','http_port':'3000'},
    'security':{'disable_initial_admin_creation':'true'},
    'users':{'allow_sign_up':'false','allow_org_create':'false',
             'auto_assign_org':'true','auto_assign_org_role':'Viewer'},
    'auth.anonymous':{'enabled':'false'},
    'analytics':{'reporting_enabled':'false','check_for_updates':'false','check_for_plugin_updates':'false'},
    'log':{'mode':'console','level':'info'}}
DEBUG={'apiVersion':1,'prune':False,'deleteDatasources':[],'datasources':[
    {'name':'Schubert NK Prometheus','uid':'schubert-nk-prometheus','type':'prometheus',
     'access':'proxy','orgId':1,'url':'http://127.0.0.1:9090','isDefault':True,'version':1,
     'editable':False,'jsonData':{'httpMethod':'GET','timeInterval':'15s'}}]}
STANDARD={'apiVersion':1,'prune':False,'deleteDatasources':[],'datasources':[]}


def ini(text):
    if not isinstance(text,str):
        raise ValueError('public INI text required')
    p=configparser.ConfigParser(interpolation=None,strict=True,empty_lines_in_values=False)
    p.optionxform=str
    p.read_string(text)
    if p.defaults():
        raise ValueError('no inherited defaults in declared closed profile')
    return {name:dict(p[name]) for name in p.sections()}


def read(index):
    return (ROOT/DIRECTORY/FILES[index]).read_text()


class ProfileTest(unittest.TestCase):
    mutations=0

    def reject(self,value,expected):
        with self.assertRaises((ValueError,TypeError)):
            strict.exact(value,expected)
        type(self).mutations+=1

    def test_GRAFCFG001_complete_ini(self):
        strict.exact(ini(read(0)),INI)
        self.assertEqual(7,len(ini(read(0))))
        self.assertEqual(16,sum(map(len,ini(read(0)).values())))

    def test_GRAFCFG002_complete_debug_datasource(self):
        strict.exact(strict.parse(read(1)),DEBUG)
        self.assertEqual(1,len(strict.parse(read(1))['datasources']))

    def test_GRAFCFG003_standard_nondestructive_profile(self):
        strict.exact(strict.parse(read(2)),STANDARD)
        self.assertEqual([],strict.parse(read(2))['datasources'])
        self.assertIs(False,strict.parse(read(2))['prune'])
        self.assertEqual([],strict.parse(read(2))['deleteDatasources'])

    def test_GRAFCFG004_all_ini_key_omissions_values_and_inheritance(self):
        for section,values in INI.items():
            for key in values:
                changed=copy.deepcopy(INI)
                del changed[section][key]
                self.reject(changed,INI)
                changed=copy.deepcopy(INI)
                changed[section][key]='unexpected'
                self.reject(changed,INI)
        for section,key,value in (
            ('server','http_addr',''),('server','http_addr','0.0.0.0'),
            ('server','http_addr','::'),('server','http_addr','example.invalid'),
            ('security','disable_initial_admin_creation','false'),
            ('auth.anonymous','enabled','true'),('users','auto_assign_org','false'),
            ('users','auto_assign_org_role','Admin'),('security','admin_password','PUBLIC_NOT_A_SECRET'),
            ('security','secret_key','PUBLIC_NOT_A_SECRET'),('server','http_port','$'+'{UNUSED_PUBLIC_VALUE}')):
            changed=copy.deepcopy(INI)
            changed[section][key]=value
            self.reject(changed,INI)
        for raw in ('[server]\nhttp_addr=a\nhttp_addr=b',
                    '[server]\nhttp_addr=a\n[server]\nhttp_addr=b',
                    '[DEFAULT]\nhttp_addr=127.0.0.1\n[server]\nprotocol=http'):
            with self.assertRaises((configparser.Error,ValueError)):
                ini(raw)
            type(self).mutations+=1
        self.reject(ini(read(0)+'\n[extra]\nkey=value\n'),INI)

    def test_GRAFCFG005_datasource_fields_and_unknown_insertions(self):
        original=strict.parse(read(1))
        for key,value in (
            ('url','http://example.invalid:9090'),('url','http://0.0.0.0:9090'),
            ('url','http://localhost:9090'),('url','http://127.0.0.1:9091'),
            ('access','direct'),('type','postgres'),('uid','unregistered'),
            ('orgId',2),('orgId',True),('version',True),('editable',True),
            ('editable',0),('isDefault',1),('basicAuth',True),
            ('secureJsonData',{}),('jsonData',{'httpMethod':'POST','timeInterval':'15s'})):
            changed=copy.deepcopy(original)
            changed['datasources'][0][key]=value
            self.reject(changed,DEBUG)
        for key in original['datasources'][0]:
            changed=copy.deepcopy(original)
            del changed['datasources'][0][key]
            self.reject(changed,DEBUG)
        changed=copy.deepcopy(original)
        changed['datasources']*=2
        self.reject(changed,DEBUG)
        strict.exact(strict.parse(read(1)),DEBUG)

    def test_GRAFCFG006_types_json_and_standard_faults(self):
        for value in (None,[],{},False,0,''):
            self.reject(value,DEBUG)
        for raw in ('{"apiVersion":1,"apiVersion":2}','{"x":NaN}','{"x":Infinity}','{} {}',''):
            with self.assertRaises(ValueError):
                strict.parse(raw)
            type(self).mutations+=1
        for key,value in (('apiVersion',True),('prune',True),('prune',0),
                          ('deleteDatasources',[{'name':'existing'}]),('datasources',[None]),
                          ('unknown',[])):
            changed=copy.deepcopy(STANDARD)
            changed[key]=value
            self.reject(changed,STANDARD)
        self.reject(strict.parse(read(1)),STANDARD)
        self.reject(strict.parse(read(2)),DEBUG)
        for value in (None,False,0):
            with self.assertRaises(ValueError):
                ini(value)
            type(self).mutations+=1

    def test_GRAFCFG007_independent_prometheus_candidate_binding(self):
        actual=strict.parse((ROOT/PROM).read_text())
        self.assertEqual('--web.listen-address=127.0.0.1:9090',actual[0])
        self.assertEqual('http://127.0.0.1:9090',strict.parse(read(1))['datasources'][0]['url'])
        prom=strict.parse((ROOT/'src/deployment/monitoring/prometheus/debug.yml.template').read_text())
        self.assertEqual('15s',prom['global']['scrape_interval'])
        self.assertEqual('15s',strict.parse(read(1))['datasources'][0]['jsonData']['timeInterval'])

    def test_GRAFCFG008_source_scope_and_retained_runtime_holds(self):
        expected={DIRECTORY+n for n in (*FILES,'README.md')}
        changed=set(subprocess.check_output(['git','diff','--name-only',BASELINE,'HEAD','--','src'],
                                             cwd=ROOT,text=True).splitlines())
        self.assertEqual(expected,changed)
        self.assertEqual('',subprocess.check_output(['git','status','--porcelain','--untracked-files=normal','--','src'],
                                                    cwd=ROOT,text=True))
        for name in expected:
            file=ROOT/name
            self.assertTrue(file.is_file() and not file.is_symlink())
            self.assertFalse(os.access(file,os.X_OK))
        readme=(ROOT/DIRECTORY/'README.md').read_text()
        for value in ('GRAFCFG001..008','UNRUN/HOLD','prune=false','secret key','BOM','total5GB'):
            self.assertIn(value,readme)


def main():
    invocation=capture(Path(__file__))
    if OUT.exists():
        raise ValueError('new-only data semantic proof, never success replay')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    files=[DIRECTORY+n for n in (*FILES,'README.md')]+[SPEC,PROM,
        'src/deployment/monitoring/prometheus/debug.yml.template']
    inputs={p:strict.sha(ROOT/p) for p in files}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProfileTest))
    static=subprocess.run([sys.executable,'-B','-m','pyflakes',str(Path(__file__))],
                          cwd=ROOT,text=True,capture_output=True,check=False)
    actual=0 if result.wasSuccessful() and result.testsRun==8 and not result.skipped and static.returncode==0 else 1
    if inputs!={p:strict.sha(ROOT/p) for p in files}:
        raise ValueError('exact configuration inputs unchanged during own PT')
    verify(invocation)
    value=dict(actualExit=actual,source=source,invocation=invocation,
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        startUTC=started,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        environment=dict(os=platform.platform(),python=sys.version,executable=sys.executable,
                         parser='stdlib strict ConfigParser/strict JSON subset, not actual Grafana'),
        testsRun=result.testsRun,failed=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
        mutationChecks=ProfileTest.mutations,inputHashes=inputs,log=log.getvalue(),
        cases=[dict(testId=f'GRAFCFG{n:03d}',result='PASS' if result.wasSuccessful() else 'NOT_QUALIFIED',
                    oracle='1735 independently fixed whole data or mutation expectations',
                    actual='all assertions passed' if result.wasSuccessful() else 'see own public log') for n in range(1,9)],
        static=dict(actualExit=static.returncode,command=static.args,stdout=static.stdout,stderr=static.stderr),
        productDataArtifacts=3,javaProductTestsExecuted=0,actualGrafanaParserExecuted=False,daemonExecuted=False,
        actualAccountOrCredentialOperations=0,actualDatabaseActions=0,actualVmActions=0,actualNetworkActions=0,
        previousDatasourceDeletionRequested=False,existingDatasourceDisableProven=False,
        signedBomInclusionQualified=False,actualStorageCapacityQualified=False,
        statementCoverage=None,methodCoverage=None,classCoverage=None,branchCoverage=None,
        coverageApplicability='NONEXECUTING_CONFIG_DATA_NOT_JAVA_EXCLUSION',
        whole451Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,bugs=[])
    os.umask(0o077)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as handle:
        json.dump(value,handle,ensure_ascii=False,sort_keys=True,indent=2)
        handle.write('\n')
    print(json.dumps(dict(actualExit=actual,source=source,tests=result.testsRun,failed=len(result.failures),
                         errors=len(result.errors),mutations=ProfileTest.mutations,
                         manifestSha256=strict.sha(OUT/'manifest.json'))))
    raise SystemExit(actual)

if __name__=='__main__':
    main()
