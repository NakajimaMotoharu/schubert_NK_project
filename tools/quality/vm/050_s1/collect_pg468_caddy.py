"""Explicit fresh selected XML/static/changed-method counters. Not whole/native/formal acceptance."""
import datetime,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG468-caddy-selected-v1'
assert not OUT.exists() and (WORK/'pg468-caddy-selected-v1.exit').read_text().strip()=='0'
OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected={'protocol':{'MessageCodecTest':7},'storage':{'ResourceScopeTest':8},'bootstrap':{'FixedServiceIdentityTest':10},'api':{'QuestionQueryRequestTest':2},'web':{'WebSecurityHeaderTest':4},'batch':{'MorningCompletionChecksTest':4,'MorningCompletionEvidenceTest':3,'MorningStartupLaunchOwnerTest':3,'MorningDatabaseSessionTest':20,'BackupUnitStartClientTest':16,'CaddyAdmissionFenceTest':3,'CaddyParentRemainingBudgetTest':1,'MorningCaddyReadinessTest':12,'MorningParentBudgetTest':3}}
started=(WORK/'pg468-caddy-selected-v1.started').read_text().strip();files={};modules={}
for module,suites in selected.items():
 target=ROOT/'src'/('schubert-nk-'+module)/'target';static=E.parse(target/'spotbugsXml.xml').getroot()
 assert not static.findall('BugInstance') and int(static.find('Errors').get('errors'))==0
 for name,count in suites.items():
  paths=list((target/'surefire-reports').glob('TEST-*.'+name+'.xml'));assert len(paths)==1 and paths[0].stat().st_mtime>=datetime.datetime.fromisoformat(started).timestamp()
  original=E.parse(paths[0]).getroot();assert int(original.get('tests'))==count and len(original.findall('testcase'))==count
  assert all(int(original.get(k))==0 for k in ('failures','errors','skipped'))
  safe=E.Element('testsuite',{k:original.get(k) for k in ('name','tests','failures','errors','skipped','time','timestamp') if original.get(k) is not None})
  for case in original.findall('testcase'):
   assert all(c.tag in ('system-out','system-err') for c in case)
   E.SubElement(safe,'testcase',{k:case.get(k) for k in ('name','classname','time')})
  p=OUT/'junit'/module/paths[0].name;p.parent.mkdir(parents=True,exist_ok=True);E.indent(safe);E.ElementTree(safe).write(p,encoding='utf-8',xml_declaration=True);files[str(p.relative_to(OUT))]=sha(p)
 modules[module]={'tests':sum(suites.values()),'suites':len(suites),'failures':0,'errors':0,'skipped':0,'staticViolations':0}
report=E.parse(ROOT/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
c=next(c for c in report.findall('.//class') if c.get('name')=='dev/codex/schubert/nk/batch/platform/MorningCaddyReadiness')
coverage={m.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))} for v in m.findall('counter')} for m in c.findall('method')}
assert all(v['missed']==0 for v in coverage['cold'].values())
assert sum(m['tests'] for m in modules.values())==96 and sum(m['suites'] for m in modules.values())==14
log=WORK/'pg468-caddy-selected-v1.log';assert 'BUILD SUCCESS' in log.read_text()
names={'MorningCaddyReadiness.java','MorningCaddyReadinessTest.java'}
sources={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').rglob('*.java') if p.name in names};assert len(sources)==2
manifest={'id':OUT.name,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirtyAtCollection':True,'sourceHashesPostRun':sources,'startedAt':started,'completedAt':(WORK/'pg468-caddy-selected-v1.completed').read_text().strip(),'command':'bash tools/quality/vm/050_s1/pg468_caddy_selected_v1.sh','exitCode':0,'tests':96,'suites':14,'modules':modules,'changedColdCoverage':coverage['cold'],'nativeColdInvocationCoverage':coverage['coldInvocation'],'independentOracle':'Independent fixed manager literals: retained strict normal F18 plus both exact unused auxiliary entries; mixed/modified/null/missing/foreign/bad retained states rejected, old invocation rejected by fresh ready. Existing actual owner/DB/kernel/budget controls.','bugs':['BUG-730','BUG-731'],'ssc':['SSC-192'],'ykt':['YKT-517'],'testIds':['CADDY192001','CADDY192002','CADDY192003'],'privateLogSha256':sha(log),'files':files,'formal':False,'coverageQualified':False,'limits':['96 selected only, old XML not counted','cold counters only; coldInvocation/native surface unaccepted','New-source full/native not run; old df9 parent30 and PG464 success separate','No full CHR, QA051 comparator pending, formal run24 unchanged'],'environment':{'jdk':'25.0.4','maven':'3.9.12','node':'24.19.0','jacoco':'0.8.15','hostOS':subprocess.check_output(['uname','-sr'],text=True).strip()},'redaction':'Case identity/timing and hashes only; XML properties/stdout/stderr/private DB/session/credential omitted'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':96,'suites':14,'changedColdAllCountersMiss0':True,'nativeColdInvocationOpen':True,'manifestSha256':sha(OUT/'manifest.json'),'formal':False}))
