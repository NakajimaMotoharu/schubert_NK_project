"""Explicit fresh selected XML/static/changed-method counters. Not whole/native/formal acceptance."""
import datetime,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG464-stopcomp-selected-v3'
assert not OUT.exists() and (WORK/'pg464-stopcomp-selected-v3.exit').read_text().strip()=='0'
OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected={'protocol':{'MessageCodecTest':7},'storage':{'ResourceScopeTest':8},'bootstrap':{'FixedServiceIdentityTest':10},'api':{'QuestionQueryRequestTest':2},'web':{'WebSecurityHeaderTest':4},'batch':{'MorningCompletionChecksTest':4,'MorningCompletionEvidenceTest':3,'StoppedBackupCompletionTest':4,'MorningStartupLaunchOwnerTest':3,'MorningDatabaseSessionTest':20,'BackupUnitReceiptGateTest':11,'MorningBackupUnitCycleTest':10,'MorningParentBudgetTest':3}}
started=(WORK/'pg464-stopcomp-selected-v3.started').read_text().strip();files={};modules={}
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
c=next(c for c in report.findall('.//class') if c.get('name')=='dev/codex/schubert/nk/batch/file/MorningCompletionEvidence')
coverage={m.get('name'):{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))} for v in m.findall('counter')} for m in c.findall('method')}
assert all(v['missed']==0 for v in coverage['verify'].values())
assert sum(m['tests'] for m in modules.values())==89 and sum(m['suites'] for m in modules.values())==13
log=WORK/'pg464-stopcomp-selected-v3.log';assert 'BUILD SUCCESS' in log.read_text()
names={'MorningCompletionEvidence.java','MorningProcessMain.java','MorningCompletionEvidenceTest.java','StoppedBackupCompletionTest.java','StoppedBackupFixture.java'}
sources={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').rglob('*.java') if p.name in names};assert len(sources)==5
manifest={'id':OUT.name,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirtyAtCollection':True,'sourceHashesPostRun':sources,'startedAt':started,'completedAt':(WORK/'pg464-stopcomp-selected-v3.completed').read_text().strip(),'command':'bash tools/quality/vm/050_s1/pg464_stopcomp_selected_v3.sh','exitCode':0,'tests':89,'suites':13,'modules':modules,'changedVerifyCoverage':coverage['verify'],'existingConstructorOpenCoverage':coverage['<init>'],'independentOracle':'Handwritten 18-field bus/kernel literal, fresh0/30 -> explicit stop -> original receipt/cycle; stopped/GC/foreign/partial/null/owner/kernel/30m boundary and exact seven-event order. Full DB row/original reference mismatches reject.','bugs':['BUG-704','BUG-705'],'ssc':['SSC-187'],'ykt':['YKT-506'],'testIds':['PT-OPS-STOPCOMP001','PT-OPS-STOPCOMP002','PT-OPS-STOPCOMP003'],'privateLogSha256':sha(log),'files':files,'formal':False,'coverageQualified':False,'limits':['89 selected only, old XML not counted','Constructor existing15 branch/1 line miss remain explicit; no record/class100 claim','MorningProcessMain assembly changed argument is native-only pending','New-source full/native not run; old11c A01/parent143 separate','No full CHR, QA051 comparator pending, formal run24 unchanged'],'environment':{'jdk':'25.0.4','maven':'3.9.12','node':'24.19.0','jacoco':'0.8.15','hostOS':subprocess.check_output(['uname','-sr'],text=True).strip()},'redaction':'Case identity/timing and hashes only; XML properties/stdout/stderr/private DB/session/credential omitted'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'tests':89,'suites':13,'changedVerifyAllCountersMiss0':True,'constructorOpen':True,'manifestSha256':sha(OUT/'manifest.json'),'formal':False}))
