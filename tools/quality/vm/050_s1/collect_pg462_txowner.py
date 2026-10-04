"""Fixed selected XML + real A01 independent exact comparison. Never formal/full acceptance."""
import datetime,hashlib,json,pathlib,shutil,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
# Explicit absolute sibling workspace path; no credential/private content copied.
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG462-txowner-selected-v4'
assert not OUT.exists();OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert (WORK/'pg462-txowner-selected-v3.exit').read_text().strip()=='0'
selected={'protocol':{'MessageCodecTest':7},'storage':{'ResourceScopeTest':8},'bootstrap':{'FixedServiceIdentityTest':10},'api':{'QuestionQueryRequestTest':2},'web':{'WebSecurityHeaderTest':4},'batch':{'MorningCompletionChecksTest':4,'MorningCompletionEvidenceTest':3,'MorningStartupLaunchOwnerTest':3,'MorningDatabaseSessionTest':20}}
files={};modules={}
for module,suites in selected.items():
 target=ROOT/'src'/('schubert-nk-'+module)/'target';static=E.parse(target/'spotbugsXml.xml').getroot()
 assert not static.findall('BugInstance') and int(static.find('Errors').get('errors'))==0
 for name,count in suites.items():
  paths=list((target/'surefire-reports').glob('TEST-*.'+name+'.xml'));assert len(paths)==1
  original=E.parse(paths[0]).getroot();assert int(original.get('tests'))==count and len(original.findall('testcase'))==count
  assert all(int(original.get(k))==0 for k in ('failures','errors','skipped'))
  safe=E.Element('testsuite',{k:original.get(k) for k in ('name','tests','failures','errors','skipped','time','timestamp') if original.get(k) is not None})
  for case in original.findall('testcase'):
   assert all(c.tag in ('system-out','system-err') for c in case)
   E.SubElement(safe,'testcase',{k:case.get(k) for k in ('name','classname','time')})
  p=OUT/'junit'/module/paths[0].name;p.parent.mkdir(parents=True,exist_ok=True);E.indent(safe);E.ElementTree(safe).write(p,encoding='utf-8',xml_declaration=True);files[str(p.relative_to(OUT))]=sha(p)
 modules[module]={'tests':sum(suites.values()),'suites':len(suites),'failures':0,'errors':0,'skipped':0,'staticViolations':0}
report=E.parse(ROOT/'src/schubert-nk-batch/target/site/jacoco/jacoco.xml').getroot()
classes=[c for c in report.findall('.//class') if c.get('name')=='dev/codex/schubert/nk/batch/file/MorningCompletionChecks'];assert len(classes)==1
coverage={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))} for c in classes[0].findall('counter')}
if 'BRANCH' not in coverage:
 assert not classes[0].findall(".//counter[@type='BRANCH']")
 coverage['BRANCH']={'missed':0,'covered':0,'basis':'Class and all methods have no instrumented branch instructions; linear helper, not global coverage100'}
assert all(coverage[k]['missed']==0 for k in ('LINE','METHOD','CLASS','BRANCH'))
actual=ROOT/'program/characterization/reports/nk/PG462-native-a01-v1/artifacts/CHR-A01.json';baseline=ROOT/'program/characterization/baseline/current/artifacts/CHR-A01.json'
assert sha(baseline)=='df68edfbd59d60fc0d87fcce818401788740153c8b630f790d785f6414001993'
expected=json.loads(baseline.read_bytes());assert expected['title']=='schubert - ログイン';expected['title']='schubert NK - ログイン'
assert json.loads(actual.read_bytes())==expected
p=OUT/'native/CHR-A01.json';p.parent.mkdir();shutil.copyfile(actual,p);files[str(p.relative_to(OUT))]=sha(p)
log=WORK/'pg462-txowner-selected-v3.log';assert 'BUILD SUCCESS' in log.read_text()
sources={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').rglob('*.java') if p.name in ('MorningCompletionChecks.java','MorningCompletionChecksTest.java','MorningStartupLaunchOwner.java')}
manifest={'id':OUT.name,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirtyAtCollection':True,'sourceHashesPostRun':sources,'startedAt':(WORK/'pg462-txowner-selected-v3.started').read_text().strip(),'completedAt':(WORK/'pg462-txowner-selected-v3.completed').read_text().strip(),'command':'bash tools/quality/vm/050_s1/pg462_txowner_selected_v3.sh','exitCode':0,'modules':modules,'tests':61,'suites':9,'independentOracle':'Stateful TX autoCommit=false rejects former combined guard; pure owner leaves TX untouched; literal peer-DB-peer ordering and fail/null guards. A01 all baseline fields exact except approved DIF001/QA045 title.','coverageNewHelper':coverage,'coverageQualified':False,'formal':False,'nativeA01':{'productionSource':'00785cf0698aecf1ace1e60b87e8849639e85b97','run':'PG462-native-a01-v1','exitCode':0,'casePass':True,'baselineSha256':sha(baseline),'wholeParentAccepted':False,'otherCasesNotRun':True,'logSha256':sha(WORK/'pg462-chr-a01-native-v1.log')},'ssc':['SSC-185'],'bugs':['BUG-693','BUG-692'],'ykt':['YKT-497','YKT-496'],'previousFailures':[{'v1':1,'cause':'Batch-only stale installed dependencies; no tests run'},{'v2':1,'cause':'Compile Guard.check void contract; batch tests not run'}],'limits':['Selected targets append existing exec; no whole-source coverage100','No fabricated pre-run all-source proof','Parent source00785 timeout143 retained; patched native completion not run','Formal run24/1964PT/53scope unchanged'],'environment':{'os':subprocess.check_output(['uname','-sr'],text=True).strip(),'jdk':'25.0.4','maven':'3.9.12','jacoco':'0.8.15'},'privateLogSha256':sha(log),'redaction':'Only JUnit testcase/summary and already-redacted A01; no properties, stdout, heap, DB dump, tokens, credentials','files':files}
assert sum(m['tests'] for m in modules.values())==61
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':OUT.name,'tests':61,'suites':9,'manifestSha256':sha(OUT/'manifest.json'),'formal':False,'nativeA01Pass':True}))
