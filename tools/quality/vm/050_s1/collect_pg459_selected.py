"""Exact selected XML and byte hashes. No stale suite/native/formal coverage qualification."""
import datetime,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG459-caddy-cold-selected-v2'
assert not OUT.exists();OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected={'protocol':{'MessageCodecTest':7},'storage':{'ResourceScopeTest':8},'bootstrap':{'FixedServiceIdentityTest':10},'api':{'QuestionQueryRequestTest':2},'web':{'PageViewModelTest':8},'batch':{'MorningCaddyReadinessTest':9,'BackupUnitStartClientTest':16,'MorningStartupLaunchOwnerTest':3,'RootFailedStartPairRecoveryTest':11,'StartupPermitFilesTest':15}}
modules={};files={}
for module,suites in selected.items():
 target=WORK/'pg459-selected-v2-frozen'/('schubert-nk-'+module)/'target'
 static=E.parse(target/'spotbugsXml.xml').getroot()
 assert not static.findall('BugInstance') and int(static.find('Errors').get('errors'))==0
 for name,count in suites.items():
  reports=list((target/'surefire-reports').glob('TEST-*.'+name+'.xml'));assert len(reports)==1
  original=E.parse(reports[0]).getroot()
  assert int(original.get('tests'))==count and len(original.findall('testcase'))==count
  assert all(int(original.get(k))==0 for k in ('failures','errors','skipped'))
  safe=E.Element('testsuite',{k:original.get(k) for k in ('name','tests','failures','errors','skipped','time','timestamp') if original.get(k) is not None})
  for case in original.findall('testcase'):
   assert all(c.tag in ('system-out','system-err') for c in case)
   E.SubElement(safe,'testcase',{k:case.get(k) for k in ('name','classname','time')})
  p=OUT/'junit'/module/reports[0].name;p.parent.mkdir(parents=True,exist_ok=True)
  E.indent(safe);E.ElementTree(safe).write(p,encoding='utf-8',xml_declaration=True);files[str(p.relative_to(OUT))]=sha(p)
 inventory={str(p.relative_to(target)):sha(p) for p in sorted(target.rglob('*')) if p.is_file()}
 modules[module]={'tests':sum(suites.values()),'suites':len(suites),'failures':0,'errors':0,'skipped':0,'staticViolations':0,'privateTargetInventorySha256':hashlib.sha256(json.dumps(inventory,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
log=WORK/'pg459-selected-v2.log';text=log.read_text();assert '[INFO] BUILD SUCCESS' in text and '[INFO] BUILD FAILURE' not in text
assert sum(m['tests'] for m in modules.values())==89 and sum(m['suites'] for m in modules.values())==10
names={'MorningCaddyReadiness.java','MorningCaddyReadinessTest.java','BackupUnitStartClient.java','MorningStartupLaunchOwner.java'}
sources={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src/schubert-nk-batch').rglob('*.java') if p.name in names}
manifest={'id':OUT.name,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirtyAtCollection':True,'sourceFilesSha256':sources,'formal':False,'hostExitCode':0,'tests':89,'suites':10,'failures':0,'errors':0,'skipped':0,'modules':modules,'hostLogSha256':sha(log),'privateLog':str(log),'java':'25.0.4','maven':'3.9.12','node':'24.19.0','spotbugs':'4.10.4','jacoco':'0.8.15','nullAwayCompile':'PASS','command':'six reactor spotless:apply test-compile jar:test-jar test exact10classes spotbugs:check jacoco:report (pg459-selected-v2.log)','testIds':['CADDY180001','CADDY180002','CADDY180003'],'expected':'Independent literal initial/normal-history receipt fields; U64/PID limits; malformed/null/unknown/abnormal rejection; prior/new Invocation inequality; existing ownership regression','actual':'All exact89 testcases PASS, no F/E/S; static6 zero','bugs':['BUG-680'],'ykt':['YKT-485'],'ssc':['SSC-180'],'coverage':{'qualified':False,'reason':'Selected no-clean run, JaCoCo append may include older exec. Whole native methods remain unexecuted; no coverage100 claim'},'priorFailure':{'run':'selected-v1','exitCode':1,'batchTestsNotRun':True,'cause':'New mandatory regex group required explicit nonnull contract; static suppression not used','privateLogSha256':sha(WORK/'pg459-selected-v1.log')},'limitations':['Source hash collected after selected run, not fabricated pre-run all-source proof','Native Production is separate ea1/sourcePG458; no result combined into host formal acceptance','Execution global start timestamp not captured; exact per-suite XML timestamps retained; collection is not execution time','Formal run24/1964PT/53scope unchanged'],'redaction':'JUnit properties/stdout/stderr removed. No credentials/session/token/password/private original/dump/key included.','files':files}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':OUT.name,'tests':89,'suites':10,'manifestSha256':sha(OUT/'manifest.json'),'formal':False}))
