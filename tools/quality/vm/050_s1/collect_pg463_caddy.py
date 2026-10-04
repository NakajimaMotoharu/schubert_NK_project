"""Fixed selected XML + real A01 independent exact comparison. Never formal/full acceptance."""
import datetime,hashlib,json,pathlib,shutil,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
# Explicit absolute sibling workspace path; no credential/private content copied.
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG463-caddy-selected-v1'
assert not OUT.exists();OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert (WORK/'pg463-caddy-selected-v1.exit').read_text().strip()=='0'
selected={'protocol':{'MessageCodecTest':7},'storage':{'ResourceScopeTest':8},'bootstrap':{'FixedServiceIdentityTest':10},'api':{'QuestionQueryRequestTest':2},'web':{'WebSecurityHeaderTest':4},'batch':{'MorningCompletionChecksTest':4,'MorningCompletionEvidenceTest':3,'MorningStartupLaunchOwnerTest':3,'MorningDatabaseSessionTest':20,'BackupUnitStartClientTest':16,'CaddyAdmissionFenceTest':3,'CaddyParentRemainingBudgetTest':1,'MorningCaddyReadinessTest':9,'MorningParentBudgetTest':3}}
files={};modules={}
for module,suites in selected.items():
 target=ROOT/'src'/('schubert-nk-'+module)/'target';static=E.parse(target/'spotbugsXml.xml').getroot()
 assert not static.findall('BugInstance') and int(static.find('Errors').get('errors'))==0
 for name,count in suites.items():
  paths=list((target/'surefire-reports').glob('TEST-*.'+name+'.xml'));assert len(paths)==1
  original=E.parse(paths[0]).getroot();assert paths[0].stat().st_mtime >= datetime.datetime.fromisoformat((WORK/'pg463-caddy-selected-v1.started').read_text().strip()).timestamp()
  assert int(original.get('tests'))==count and len(original.findall('testcase'))==count
  assert all(int(original.get(k))==0 for k in ('failures','errors','skipped'))
  safe=E.Element('testsuite',{k:original.get(k) for k in ('name','tests','failures','errors','skipped','time','timestamp') if original.get(k) is not None})
  for case in original.findall('testcase'):
   assert all(c.tag in ('system-out','system-err') for c in case)
   E.SubElement(safe,'testcase',{k:case.get(k) for k in ('name','classname','time')})
  p=OUT/'junit'/module/paths[0].name;p.parent.mkdir(parents=True,exist_ok=True);E.indent(safe);E.ElementTree(safe).write(p,encoding='utf-8',xml_declaration=True);files[str(p.relative_to(OUT))]=sha(p)
 modules[module]={'tests':sum(suites.values()),'suites':len(suites),'failures':0,'errors':0,'skipped':0,'staticViolations':0}

report=E.parse(ROOT/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
wanted={'dev/codex/schubert/nk/batch/file/MorningStartupLaunchOwner':{'caddyRemainingFloor'},'dev/codex/schubert/nk/batch/platform/BackupUnitStartClient':{'caddyAdmissionFence','lambda$caddyAdmissionFence$4'}}
coverage={}
for c in report.findall('.//class'):
 if c.get('name') not in wanted:continue
 for m in c.findall('method'):
  if m.get('name')=='caddyRemainingFloor' or m.get('name')=='caddyAdmissionFence' or m.get('name').startswith('lambda$caddyAdmissionFence$'):
   counters={v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))} for v in m.findall('counter')}
   assert all(v['missed']==0 for v in counters.values())
   coverage[c.get('name')+'.'+m.get('name')]=counters
assert len(coverage)==3
total=sum(m['tests'] for m in modules.values());assert total==93 and sum(m['suites'] for m in modules.values())==14
log=WORK/'pg463-caddy-selected-v1.log';assert 'BUILD SUCCESS' in log.read_text()
sources={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').rglob('*.java') if p.name in ('BackupUnitStartClient.java','MorningStartupLaunchOwner.java','CaddyAdmissionFenceTest.java','CaddyParentRemainingBudgetTest.java')}
manifest={'id':OUT.name,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirtyAtCollection':True,'sourceHashesPostRun':sources,'startedAt':(WORK/'pg463-caddy-selected-v1.started').read_text().strip(),'completedAt':(WORK/'pg463-caddy-selected-v1.completed').read_text().strip(),'command':'bash tools/quality/vm/050_s1/pg463_caddy_selected_v1.sh','exitCode':0,'modules':modules,'tests':total,'suites':14,'changedMethodsCoverage':coverage,'independentOracle':'Literal 12-event order, full fence twice, pure owner four times; 12 failure points x IO/Runtime/Error preserve primary identity; null/roles/retired intent; fixed parent remaining 30s exact boundary without origin mixing/renewal.','coverageQualified':False,'formal':False,'ssc':['SSC-186'],'bugs':['BUG-697'],'ykt':['YKT-501'],'limits':['Selected exec appended, whole-source/native coverage not accepted','Full regression for this dirty source not run','PG462 source ca332 separate A01 PASS and parent normal30 retained','Formal run24/1964PT/53scope unchanged'],'environment':{'os':subprocess.check_output(['uname','-sr'],text=True).strip(),'jdk':'25.0.4','maven':'3.9.12','node':'24.19.0','jacoco':'0.8.15'},'privateLogSha256':sha(log),'files':files,'redaction':'Summary/testcase only; XML properties/stdout/stderr/private DB/session/credentials not copied'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':OUT.name,'tests':total,'suites':14,'manifestSha256':sha(OUT/'manifest.json'),'formal':False}))
