"""Independent genuine13, fixed source, full physical CRC/init and owned file postcondition."""
from pathlib import Path
import ast,datetime,hashlib,json,re,shutil,struct,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27202-receipt13-profile-v1';U=RUNS/'pg27204-receipt13-v1';A=B/'evidence/PG27204-receipt13-v1';O=B/'evidence/PG27208-receipt13-independent-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists()
m=load(A/'manifest.json');b=m['begin'];assert b['source']==sys.argv[1] and b['productionCoreMain']=='13e6c050db76b202b03b1d7653cc368c178cae76'
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,13,0,0,0)
for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
pf=R/b['preflight']['path'];p=load(pf);assert sha(pf)==b['preflight']['sha256'] and p['actualExit']==0 and p['inputHashes']==b['inputHashes'] and all(p[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
for label,v in m['stages'].items():
 assert v['actualExit']==0 and not v['timedOut'] and v==load(A/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(A/(label+'.'+stream))==v[stream+'Sha256']
cmd=m['stages']['unit']['command'];selected=b['selectedClasses'];assert len(selected)==2 and cmd.count('--select-class')==2 and '--select-method' not in cmd and '--scan-classpath' not in cmd and not any(x in str(cmd) for x in ['schubert-nk-web-0.1','schubert-nk-api-0.1','schubert-nk-storage','artemis','postgres','enable-native-access','excludes='])
expected={(x['classname'],x['name']) for x in b['expectedCases']};cases=[];env={}
for xml in (U/'xml').glob('TEST-*.xml'):
 rt=ET.parse(xml).getroot();assert not any(rt.findall('.//'+tag) for tag in ['failure','error','skipped']);cases.extend((x.get('classname'),x.get('name')) for x in rt.findall('testcase'));env.update({x.get('name'):x.get('value') for x in rt.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==13 and set(cases)==expected
summary=(A/'unit.stdout').read_text()
for t in ['13 tests found','13 tests started','13 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert t in summary
prepare=load(R/b['prepare']['path']);assert sha(R/b['prepare']['path'])==b['prepare']['sha256'];physical={str(p.relative_to(W/'component')):sha(p) for p in (W/'component').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==3
assert prepare['testClassHashes']=={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')};testNames={x[:-6] for x in prepare['testClassHashes']}
helper=B/'input/1415_manifest_current_independent_post.py';tree=ast.parse(helper.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['crc64','code_count']];assert len(nodes)==2;exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),globals())
ids={n[:-6]:crc64((W/'component'/n).read_bytes()) for n in physical};methods={n[:-6]:code_count((W/'component'/n).read_bytes()) for n in physical};noCode={n for n,k in methods.items() if k==0};assert len(noCode)==1 and next(iter(noCode)).endswith('/package-info')
info={name:dict(crc=crc,instructions=int(inst)) for inst,bran,line,meth,cxty,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(A/'classinfo.stdout').read_text(),re.M)};ci={n:v['crc'] for n,v in info.items()};analyzed={n for n,v in info.items() if v['instructions']>0};assert analyzed==set(ids)-noCode and set(ids)-set(ci)==noCode and all(ids[n]==h for n,h in ci.items())
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG27204-RECEIPT13"' in ex;probes={n:(crc,int(hit),int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in testNames};assert observed==analyzed and all(probes[n][0]==ids[n] and probes[n][1]>0 for n in observed)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testNames)};held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(n.endswith('/'+h) for n in init for h in held);assert init&set(ids)==observed
bindings={}
for name in init-set(ids):
 mat=re.fullmatch(r'(dev/codex/schubert/nk/[^+]+)\$\$Lambda\+0x[0-9a-f]+',name);assert mat and mat.group(1) in ids;bindings[name]=mat.group(1)
rt=ET.parse(U/'coverage.xml').getroot();classes={x.get('name'):x for x in rt.findall('.//class')};assert set(classes)==set(ci)
coverage={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')};assert all(v['missed']==0 for v in coverage.values())
for k,v in coverage.items():
 for metric in ['covered','missed']:assert sum(int(x.get(metric)) for cl in classes.values() for x in cl.findall('counter') if x.get('type')==k)==v[metric]
assert {'LINE','METHOD','CLASS','BRANCH'}<=set(coverage)
assert not (observed|{'foreign/Unknown'})<=analyzed and set(ci)|{'foreign/Unknown'}!=analyzed
golden=U/'target/question-receipt-traces/PT-QST-RID008.txt';expectedGolden='forward=0123456789ABCDEFGHJKMNPQRS\nreverse=ZYXWVTSRQPNMKJHGFEDCBA9876\nlength=26\nalphabetSize=32\nrandomDrawsPerId=26\nownerOrTimeInput=false\n';assert golden.read_text()==expectedGolden and m['stages']['unit']['cwd']==str(U)
O.mkdir();files={};shutil.copyfile(golden,O/'receipt-public-golden.txt');files['receipt-public-golden.txt']=sha(O/'receipt-public-golden.txt')
for base,prefix in [(A,'unit-'),(U,'original-')]:
 for q in [x for x in base.iterdir() if x.is_file()]+list((base/'xml').glob('TEST-*.xml')):
  assert q.suffix!='.class';name='jacoco.exec' if q.name=='jacoco.exec' else prefix+('class-init.stdout' if q.name=='class-init.log' else q.name);assert name not in files;shutil.copyfile(q,O/name);files[name]=sha(O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=b['source'],productionCoreMain=b['productionCoreMain'],run=b['session'],tests=13,existingRecovery4=True,requiredExistingReceipt9=True,newTestDefinitions=0,wholeSafeFixtures=2,physicalClasses=3,positiveMainCrc=len(observed),executableClasses=len(analyzed),coverage=coverage,wholeScopeFour100=True,physicalClassHashes=physical,classIds=ids,actualJvmCodeMethodCounts=methods,naturalNoCodeClasses=sorted(noCode),hiddenJvmAdapters=bindings,manualCoverageExclusions=[],oldExecCombined=False,preflight=ref(pf),inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=env,staticApplicable=0,processingErrors=0,unclassified=0,wholeApiJarOrHeldEntryPayloadReadOrHashed=False,actualJdbcBackendConnected=False,actualDeployedKeysOrBackendOrFourClassAccess=0,originalWholeKeyRingFixtureAccepted=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=13,physical=3,positiveCrc=len(observed),wholeFour100=True,coverage=coverage,manifest=ref(O/'manifest.json'))))
