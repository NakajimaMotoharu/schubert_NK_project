"""Exact selected XML and byte hashes. No stale suite/native/formal coverage qualification."""
import datetime,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as E
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG461-caddy-policy-selected-v4'
assert not OUT.exists();OUT.mkdir(mode=0o750)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
selected={'protocol':{'MessageCodecTest':7},'storage':{'ResourceScopeTest':8},'bootstrap':{'FixedServiceIdentityTest':10},'api':{'QuestionQueryRequestTest':2},'web':{'WebSecurityHeaderTest':4,'EmbeddedWebSecurityTest':4},'batch':{'MorningCaddyReadinessTest':9,'CaddyPublicConfigurationTest':3,'CaddyPublicCaMetadataTest':3}}
modules={};files={}
for module,suites in selected.items():
 target=WORK/'pg461-selected-v4-frozen'/('schubert-nk-'+module)/'target'
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
log=WORK/'pg461-policy-selected-v4.log';text=log.read_text();assert '[INFO] BUILD SUCCESS' in text and '[INFO] BUILD FAILURE' not in text
assert sum(m['tests'] for m in modules.values())==50 and sum(m['suites'] for m in modules.values())==9
names={'CaddyPublicConfiguration.java','CaddyPublicCaMetadataTest.java','WebSecurityHeaderWriter.java','WebSecurityHeaderTest.java','EmbeddedWebSecurityTest.java'}
sources={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').rglob('*.java') if p.name in names}
manifest={'id':OUT.name,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':'dev-foundation','headAtCollection':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceDirtyAtCollection':True,'sourceFilesSha256':sources,'formal':False,'hostExitCode':0,'tests':50,'suites':9,'failures':0,'errors':0,'skipped':0,'modules':modules,'hostLogSha256':sha(log),'privateLog':str(log),'java':'25.0.4','maven':'3.9.12','node':'24.19.0','spotbugs':'4.10.4','jacoco':'0.8.15','nullAwayCompile':'PASS','command':'six reactor spotless:check test-compile test exact9classes spotbugs:check (pg461-policy-selected-v4.log)','testIds':['CA461001','CA461002','CA461003','WEB091','WEB092','WEB093','WEB094','CHR-A01'],'expected':'Independent Current CSP literal and all-response duplicates/concurrency/security checks; fixed public CA modes0600/0640/0644 only, config0640 only; owner/link/size/null/unknown boundaries rejected; unchanged readiness regression','actual':'All exact50 testcases PASS, F/E/S0; static6zero. Real A01 pending patched source.','bugs':['BUG-688','BUG-689'],'ykt':['YKT-493','YKT-494'],'ssc':['SSC-182','SSC-183'],'coverage':{'qualified':False,'reason':'Selected no-clean append and native paths unexecuted; no coverage100 claim'},'priorFailures':[{'run':'v1','exitCode':1,'cause':'No selected protocol tests; test bodies not run'},{'run':'v2','exitCode':1,'cause':'Hard POM failIfNoTests correctly retained; no selected protocol tests'},{'run':'v3','exitCode':1,'cause':'Batch method format check failed; batch tests not run'}],'limitations':['Source hashes collected after selected run, no fabricated pre-run all-source proof','Targets include old main Jars; selected test-compile classes are current, no deployable Jar or full gate claimed','Native PG460/source8e97 failed30/A01CSP mismatch preserved separately','Formal run24/1964PT/53scope remains unchanged','Global start time not captured; collection time is not execution time'],'redaction':'JUnit properties/stdout/stderr omitted. No credentials/session/token/password/private original/dump/key.','files':files}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'id':OUT.name,'tests':50,'suites':9,'manifestSha256':sha(OUT/'manifest.json'),'formal':False}))
