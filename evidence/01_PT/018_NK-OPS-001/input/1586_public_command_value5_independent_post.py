"""Independent genuine13, fixed source, full physical CRC/init and owned file postcondition."""
from pathlib import Path
import ast,datetime,hashlib,json,re,shutil,struct,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27326-public-command-value5-profile-v1';U=RUNS/'pg27332-public-command-value5-v1';A=B/'evidence/PG27332-public-command-value5-v1';O=B/'evidence/PG27334-public-command-value5-independent-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists()
m=load(A/'manifest.json');b=m['begin'];assert b['source']==sys.argv[1] and b['productionCoreMain']=='b23ddcfab9566b96f182562ae011f1b4ba401c72'
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,5,0,0,0)
for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
pf=R/b['preflight']['path'];p=load(pf);assert sha(pf)==b['preflight']['sha256'] and p['actualExit']==0 and p['inputHashes']==b['inputHashes'] and all(p[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
for label,v in m['stages'].items():
 assert v['actualExit']==0 and not v['timedOut'] and v==load(A/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(A/(label+'.'+stream))==v[stream+'Sha256']
cmd=m['stages']['unit']['command'];selected=b['selectedClasses'];assert len(selected)==1 and cmd.count('--select-class')==1 and '--select-method' not in cmd and '--scan-classpath' not in cmd and not any(x in str(cmd) for x in ['schubert-nk-web-0.1','schubert-nk-api-0.1','schubert-nk-storage','artemis','postgres','enable-native-access','excludes='])
expected={(x['classname'],x['name']) for x in b['expectedCases']};cases=[];env={}
for xml in (U/'xml').glob('TEST-*.xml'):
 rt=ET.parse(xml).getroot();assert not any(rt.findall('.//'+tag) for tag in ['failure','error','skipped']);cases.extend((x.get('classname'),x.get('name')) for x in rt.findall('testcase'));env.update({x.get('name'):x.get('value') for x in rt.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==5 and set(cases)==expected
summary=(A/'unit.stdout').read_text()
for t in ['5 tests found','5 tests started','5 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert t in summary
prepare=load(R/b['prepare']['path']);assert sha(R/b['prepare']['path'])==b['prepare']['sha256'];physical={str(p.relative_to(W/'component')):sha(p) for p in (W/'component').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==17
assert prepare['testClassHashes']=={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')};testNames={x[:-6] for x in prepare['testClassHashes']}
helper=B/'input/1415_manifest_current_independent_post.py';tree=ast.parse(helper.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['crc64','code_count']];assert len(nodes)==2;exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),globals())
ids={n[:-6]:crc64((W/'component'/n).read_bytes()) for n in physical};methods={n[:-6]:code_count((W/'component'/n).read_bytes()) for n in physical};noCode={n for n,k in methods.items() if k==0};assert len(noCode)==7 and sum(x.endswith('/package-info') for x in noCode)==6
info={name:dict(crc=crc,instructions=int(inst)) for inst,bran,line,meth,cxty,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(A/'classinfo.stdout').read_text(),re.M)};ci={n:v['crc'] for n,v in info.items()};analyzed={n for n,v in info.items() if v['instructions']>0};assert analyzed==set(ids)-noCode and all(x.endswith('/package-info') and x in noCode for x in set(ids)-set(ci)) and all(ids[n]==h for n,h in ci.items())
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG27332-PUBLIC-COMMAND-VALUE5"' in ex;probes={n:(crc,int(hit),int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in testNames};assert observed<=analyzed and all(probes[n][0]==ids[n] and probes[n][1]>0 for n in observed)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testNames)};held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(n.endswith('/'+h) for n in init for h in held);assert (init&set(ids))-observed<=noCode and observed<=init
bindings={}
for name in init-set(ids):
 mat=re.fullmatch(r'(dev/codex/schubert/nk/[^+]+)\$\$Lambda\+0x[0-9a-f]+',name);assert mat and mat.group(1) in ids;bindings[name]=mat.group(1)
rt=ET.parse(U/'coverage.xml').getroot();classes={x.get('name'):x for x in rt.findall('.//class')};assert set(classes)==set(ci)
coverage={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')};whole100=all(v['missed']==0 for v in coverage.values())
for k,v in coverage.items():
 for metric in ['covered','missed']:assert sum(int(x.get(metric)) for cl in classes.values() for x in cl.findall('counter') if x.get('type')==k)==v[metric]
assert {'LINE','METHOD','CLASS','BRANCH'}<=set(coverage)
assert not (observed|{'foreign/Unknown'})<=analyzed and set(ci)|{'foreign/Unknown'}!=analyzed
targetNames=['dev/codex/schubert/nk/api/application/question/QuestionCommandService$CancelResult','dev/codex/schubert/nk/api/application/question/QuestionCommandService$DeleteResult']
targetCounters={n:{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in classes[n].findall('counter')} for n in targetNames}
assert all({'LINE','METHOD','CLASS','BRANCH'}<=set(cs) and all(v['missed']==0 for v in cs.values()) for cs in targetCounters.values())
assert b['producerSha256']==sha(B/'input/1583_public_command_value5_profile.py')
assert m['stages']['unit']['cwd']==str(U)
O.mkdir();files={}
for base,prefix in [(A,'unit-'),(U,'original-')]:
 for q in [x for x in base.iterdir() if x.is_file()]+list((base/'xml').glob('TEST-*.xml')):
  assert q.suffix!='.class';name='jacoco.exec' if q.name=='jacoco.exec' else prefix+('class-init.stdout' if q.name=='class-init.log' else q.name);assert name not in files;shutil.copyfile(q,O/name);files[name]=sha(O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=b['source'],productionCoreMain=b['productionCoreMain'],run=b['session'],tests=5,newPublicDtoFive=True,newTestDefinitions=5,wholeSafeFixtures=2,physicalClasses=17,positiveMainCrc=len(observed),executableClasses=len(analyzed),coverage=coverage,uncoveredFullSourceClasses={n:{x.get('type'):int(x.get('missed')) for x in cl.findall('counter') if int(x.get('missed'))>0} for n,cl in classes.items() if any(int(x.get('missed'))>0 for x in cl.findall('counter'))},wholeScopeFour100=whole100,targetPublicDtoFour100=True,targetCounters=targetCounters,privateOpaqueResultOrSnapshotConstructed=False,publicDtoOnlyNormalPtNotHeldPtReplacement=True,physicalClassHashes=physical,classIds=ids,actualJvmCodeMethodCounts=methods,naturalNoCodeClasses=sorted(noCode),hiddenJvmAdapters=bindings,manualCoverageExclusions=[],oldExecCombined=False,preflight=ref(pf),inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=env,staticApplicable=0,processingErrors=0,unclassified=0,wholeApiJarOrHeldEntryPayloadReadOrHashed=False,actualJdbcBackendConnected=False,actualDeployedKeysOrBackendOrFourClassAccess=0,originalWholeKeyRingFixtureAccepted=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=5,physical=17,positiveCrc=len(observed),targetPublicDtoFour100=True,wholeFour100=whole100,targetCounters=targetCounters,coverage=coverage,manifest=ref(O/'manifest.json'))))
