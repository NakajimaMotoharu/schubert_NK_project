"""Independent same-run/full-physical CRC and coverage check of pure storage exception scope."""
from pathlib import Path
import ast,datetime,hashlib,json,re,shutil,struct,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27688-storage-public-graph-v1';U=RUNS/'pg27694-storage-public-graph-v1';A=B/'evidence/PG27694-storage-public-graph-v1';O=B/'evidence/PG27696-storage-public-graph-independent-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();m=ld(A/'manifest.json');b=m['begin'];assert b['source']==sys.argv[1] and b['productionCoreMain']=='edaf641333266660ec79a6e070c98b7a79bbccac'
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,4,0,0,0)
for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
pf=R/b['preflight']['path'];p=ld(pf);assert sha(pf)==b['preflight']['sha256'] and p['actualExit']==0 and p['inputHashes']==b['inputHashes']
assert all(p[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
for label,v in m['stages'].items():
 assert v['actualExit']==0 and not v['timedOut'] and v==ld(A/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(A/(label+'.'+stream))==v[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert not any(x in str(cmd) for x in ['schubert-nk-web-0.1','schubert-nk-api-0.1','artemis','postgres','enable-native-access','excludes='])
cases=[];env={}
for xml in (U/'xml').glob('TEST-*.xml'):
 rt=ET.parse(xml).getroot();assert not any(rt.findall('.//'+tag) for tag in ['failure','error','skipped']);cases.extend((x.get('classname'),x.get('name')) for x in rt.findall('testcase'));env.update({x.get('name'):x.get('value') for x in rt.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==4 and set(cases)=={(x['classname'],x['name']) for x in b['expectedCases']}
for text in ['4 tests found','4 tests started','4 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in (A/'unit.stdout').read_text()
prepare=ld(R/b['prepare']['path']);assert sha(R/b['prepare']['path'])==b['prepare']['sha256'];physical={str(q.relative_to(W/'target/classes')):sha(q) for q in (W/'target/classes').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==3
assert prepare['testClassHashes']=={str(q.relative_to(W/'test-classes-v2')):sha(q) for q in (W/'test-classes-v2').rglob('*.class')};testNames={n.removesuffix('.class') for n in prepare['testClassHashes']}
helper=B/'input/1415_manifest_current_independent_post.py';tree=ast.parse(helper.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['crc64','code_count']];assert len(nodes)==2;exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),globals())
ids={n.removesuffix('.class'):crc64((W/'target/classes'/n).read_bytes()) for n in physical};methods={n.removesuffix('.class'):code_count((W/'target/classes'/n).read_bytes()) for n in physical};noCode={n for n,k in methods.items() if k==0}
assert noCode=={'dev/codex/schubert/nk/storage/package-info'}
ci={name:crc for inst,bran,line,meth,cxty,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(A/'classinfo.stdout').read_text(),re.M)};assert set(ci)==set(ids)-noCode and all(ids[n]==crc for n,crc in ci.items())
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG27694-STORAGE-PUBLIC-GRAPH4"' in ex
probes={n:(c,int(hit),int(total)) for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in testNames};assert observed==set(ci) and all(probes[n][0]==ids[n] and probes[n][1]>0 for n in observed)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testNames)};assert init==observed
rt=ET.parse(U/'coverage.xml').getroot();classes={x.get('name'):x for x in rt.findall('.//class')};assert set(classes)==set(ci)
counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')}
for k,v in counters.items():
 for metric in ['covered','missed']:assert sum(int(x.get(metric)) for cl in classes.values() for x in cl.findall('counter') if x.get('type')==k)==v[metric]
assert {'LINE','METHOD','CLASS','BRANCH'}<=set(counters) and all(v['missed']==0 and v['covered']>0 for v in counters.values())
target='dev/codex/schubert/nk/storage/StorageIoException';targetCounters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in classes[target].findall('counter')};assert targetCounters['BRANCH']['covered']==12
assert set(ci)|{'foreign/Unknown'}!=set(ids)-noCode
O.mkdir();files={}
for base,prefix in [(A,'unit-'),(U,'original-')]:
 for q in [x for x in base.iterdir() if x.is_file()]+list((base/'xml').glob('TEST-*.xml')):
  assert q.suffix!='.class';name='jacoco.exec' if q.name=='jacoco.exec' else prefix+('class-init.stdout' if q.name=='class-init.log' else q.name);assert name not in files;shutil.copyfile(q,O/name);files[name]=sha(O/name)
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['productionCoreMain'],run=b['session'],tests=4,newTestDefinitions=4,physicalClasses=3,positiveMainCrc=len(observed),classIds=ids,physicalClassHashes=physical,actualJvmCodeMethodCounts=methods,naturalNoCodeClasses=sorted(noCode),coverage=counters,wholeSelectedHelperScopeFour100=True,wholeProjectFour100=False,targetCounters=targetCounters,inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=env,staticApplicable=0,unclassified=0,processingErrors=0,preflight=ref(pf),manualCoverageExclusions=[],oldExecCombined=False,actualDirectoryNativeFdRootFsDbOrHeldClassActions=0,bug2718DirectoryCallerRuntime='NOT_RUN_HOLD_OPEN',ResourceScopeChangedOrRequalified=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=4,physical=3,positiveCrc=len(observed),coverage=counters,manifest=ref(O/'manifest.json'))))
