"""PG465 scoped evidence: explicit XML/static/independent source hashes; never formal/native credit."""
import datetime,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG465-bootstrap-selected-v7-safe-v2'
assert not OUT.exists()
log=WORK/'pg465-bootstrap-selected-v7.log'
assert 'BUILD SUCCESS' in log.read_text() and 'BUILD FAILURE' not in log.read_text()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected={'protocol':['MessageCodecTest'],'storage':['ResourceScopeTest'],'bootstrap':['FixedServiceIdentityTest','InspectorCredentialLoaderTest','ServiceCredentialReaderTest','BootstrapCredentialLoaderTest'],'api':['BootstrapAdminServiceTest','BootstrapAdminMainTest','PasswordHasherTest','PasswordPolicyTest','UserCommandServiceTest'],'web':['WebSecurityHeaderTest'],'batch':['StoppedBackupCompletionTest']}
OUT.mkdir(mode=0o750); files={};modules={};coverage={}
for module,suites in selected.items():
 target=ROOT/'src'/('schubert-nk-'+module)/'target'; static=E.parse(target/'spotbugsXml.xml').getroot()
 assert not static.findall('BugInstance') and int(static.find('Errors').get('errors'))==0
 total=0
 for name in suites:
  paths=list((target/'surefire-reports').glob('TEST-*.'+name+'.xml'));assert len(paths)==1
  root=E.parse(paths[0]).getroot();n=int(root.get('tests'));assert n>0 and len(root.findall('testcase'))==n
  assert all(int(root.get(k))==0 for k in ('failures','errors','skipped'))
  # BUG715: Surefire timestamp is optional; actual file time separates fresh v7 from old v6.
  assert paths[0].stat().st_mtime >= datetime.datetime.fromisoformat('2026-10-05T10:56:00+09:00').timestamp()
  clean=E.Element('testsuite',{k:root.get(k) for k in ('name','tests','failures','errors','skipped','time','timestamp') if root.get(k) is not None})
  for case in root.findall('testcase'):
   assert all(c.tag in ('system-out','system-err') for c in case)
   E.SubElement(clean,'testcase',{k:case.get(k) for k in ('name','classname','time')})
  p=OUT/'junit'/module/paths[0].name;p.parent.mkdir(parents=True,exist_ok=True);E.indent(clean);E.ElementTree(clean).write(p,encoding='utf-8',xml_declaration=True);files[str(p.relative_to(OUT))]=sha(p);total+=n
 modules[module]={'tests':total,'suites':len(suites),'FES':[0,0,0],'staticViolations':0}
 if module in ('api','bootstrap'):
  report=E.parse(target/'site/jacoco/jacoco.xml').getroot()
  for c in report.findall('.//class'):
   if c.get('name','').endswith(('BootstrapAdminService','BootstrapAdminService$Outcome','BootstrapAdminMain','InspectorCredentialLoader')):
    counters={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))} for v in c.findall('counter')}
    methods={m.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))} for v in m.findall('counter')} for m in c.findall('method')}
    coverage[c.get('name')]={'counters':counters,'methods':methods}
for name in ('BootstrapAdminService','BootstrapAdminService$Outcome'):
 assert all(v['missed']==0 for c,data in coverage.items() if c.endswith('/'+name) for v in data['counters'].values())
for data in [d for n,d in coverage.items() if n.endswith('/InspectorCredentialLoader')]:
 for name in ('readBootstrapUsername','readBootstrapPassword','consumeBootstrap'):
  assert all(v['missed']==0 for v in data['methods'][name].values())
names={'BootstrapAdminService.java','BootstrapAdminMain.java','BootstrapAdminServiceTest.java','BootstrapAdminMainTest.java','BootstrapCredentialLoaderTest.java','InspectorCredentialLoader.java','schubert-nk-bootstrap-admin.service.template'}
source={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').rglob('*') if p.is_file() and p.name in names and '/target/' not in str(p)};assert len(source)==7
manifest={'status':'SELECTED_PASS_NOT_NATIVE_OR_FORMAL','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'dirtySource':True,'sourceHashes':source,'command':'six-module Maven selected command documented in 341; PG465 v7 log','actualExit':0,'tests':sum(v['tests'] for v in modules.values()),'suites':sum(v['suites'] for v in modules.values()),'modules':modules,'coverage':coverage,'files':files,'privateLogSha256':sha(log),'ssc':['SSC-188','SSC-189'],'bugs':['BUG-713','BUG-714'],'oracle':'Handwritten SQL rows/audit and JCA PBKDF2; 100 parallel transactions; noncooperating table lock; real maintenance exclusive/shared lock; audit rollback; commit-before/after unknown; fixed actor field/credential IO negatives','testIds':['PT-ADM-BOOT001','PT-ADM-BOOT002','PT-ADM-BOOT003','PT-ADM-BOOT004','PT-ADM-BOOT005','PT-ADM-BOOT006','PT-ADM-BOOT007'],'environment':{'jdk':'25.0.4','maven':'3.9.12','node':'24.19.0','postgresqlFixture':'18','jacoco':'0.8.15'},'formal':False,'wholeCoverage100':False,'nativeUnitAccepted':False,'fullRegressionAccepted':False,'redaction':'No properties/stdout/stderr/DB row/credential/session values in safe XML; hashes/counts only'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':manifest['tests'],'suites':manifest['suites'],'manifestSha256':sha(OUT/'manifest.json'),'nativePending':True,'formal':False}))
