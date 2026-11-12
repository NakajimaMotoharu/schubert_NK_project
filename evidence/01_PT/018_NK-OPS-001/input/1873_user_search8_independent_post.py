"""Independent terminal/source/full191 report and CRC; full source counters and owned public golden file."""
from pathlib import Path
import ast,datetime,hashlib,json,re,shutil,struct,subprocess,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';W=RUNS/'pg27880-user-search8-normal-v1';U=RUNS/'pg27886-user-search8-v1';A=B/'evidence/PG27886-user-search8-v1';O=B/'evidence/PG27888-user-search8-independent-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists()
m=load(A/'manifest.json');b=m['begin'];assert b['source']==sys.argv[1] and b['productionCoreMain']=='016283eb5e98a5e729ca65ac1acf1ff41b367e71'
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,8,0,0,0)
for p,h in b['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
pf=R/b['preflight']['path'];p=load(pf);assert sha(pf)==b['preflight']['sha256'] and p['actualExit']==0 and p['inputHashes']==b['inputHashes']
assert all(p[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
for label,v in m['stages'].items():
 assert v['actualExit']==0 and not v['timedOut'] and v==load(A/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(A/(label+'.'+stream))==v[stream+'Sha256']
cmd=m['stages']['unit']['command'];selected=b['selectedClasses'];assert set(selected)=={v['classname'] for v in b['expectedCases']} and len(selected)==len(set(selected))
assert cmd.count('--select-class')==len(selected) and '--select-method' not in cmd and '--scan-classpath' not in cmd
assert not any(x in str(cmd) for x in ['schubert-nk-web-0.1','schubert-nk-api-0.1','schubert-nk-storage','artemis','postgres','enable-native-access','excludes='])
expected={(x['classname'],x['name']) for x in b['expectedCases']};cases=[];env={}
for xml in (U/'xml').glob('TEST-*.xml'):
 rt=ET.parse(xml).getroot();assert not any(rt.findall('.//'+tag) for tag in ['failure','error','skipped']);cases.extend((x.get('classname'),x.get('name')) for x in rt.findall('testcase'))
 env.update({x.get('name'):x.get('value') for x in rt.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==8 and set(cases)==expected
summary=(A/'unit.stdout').read_text()
for text in ['8 tests found','8 tests started','8 tests successful','0 tests failed','0 tests skipped','0 tests aborted','0 containers aborted']:assert text in summary
prepare=load(R/b['prepare']['path']);assert sha(R/b['prepare']['path'])==b['prepare']['sha256']
physical={str(q.relative_to(W/'component')):sha(q) for q in (W/'component').rglob('*.class')};assert physical==b['physicalClassHashes'] and len(physical)==177
assert prepare['testClassHashes']=={str(q.relative_to(W/'test-classes-v2')):sha(q) for q in (W/'test-classes-v2').rglob('*.class')}
testNames={n.removesuffix('.class') for n in prepare['testClassHashes']}
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(n.endswith('/'+h+'.class') for n in physical for h in held)
# Reuse only two inspected tool functions, never execute an old producer/post or product method.
helper=B/'input/1415_manifest_current_independent_post.py';tree=ast.parse(helper.read_text());nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['crc64','code_count']];assert len(nodes)==2
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),globals())
ids={n.removesuffix('.class'):crc64((W/'component'/n).read_bytes()) for n in physical};methods={n.removesuffix('.class'):code_count((W/'component'/n).read_bytes()) for n in physical};noCode={n for n,k in methods.items() if k==0}
protoPost=load(B/'evidence/PG26312-protocol-unicode-full130-independent-v1/manifest.json');switchmaps=set(protoPost['defaultSyntheticSwitchmaps']);assert len(switchmaps)==4 and all(methods[n]>0 for n in switchmaps)
info={name:dict(crc=crc,instructions=int(inst)) for inst,bran,line,meth,cxty,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(A/'classinfo.stdout').read_text(),re.M)}
ci={n:v['crc'] for n,v in info.items()};analyzed={n for n,v in info.items() if v['instructions']>0};assert analyzed==set(ids)-noCode-switchmaps
missing=set(ids)-set(ci);assert all(n.endswith('/package-info') and n in noCode for n in missing);assert all(ids[n]==crc for n,crc in ci.items());zeroInfo=set(ci)-analyzed;assert zeroInfo==(noCode-missing)|switchmaps
ex=(A/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG27886-USER-SEARCH8"' in ex
probes={n:(c,int(hit),int(total)) for c,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and n not in testNames};assert observed<=analyzed|switchmaps
assert all(probes[n][0]==ids[n] and probes[n][1]>0 for n in observed)
init={n for n in re.findall(r"Initializing '([^']+)'",(U/'class-init.log').read_text()) if n.startswith('dev/codex/schubert/nk/') and not any(n==t or n.startswith(t+'$') for t in testNames)}
assert not any(n.endswith('/'+h) for n in init for h in held)
real=init&set(ids);generated=init-set(ids);assert real-observed<=noCode and observed<=real
def owner(name):
 match=re.fullmatch(r'(dev/codex/schubert/nk/[^+]+)\$\$Lambda\+0x[0-9a-f]+',name)
 return match.group(1) if match and match.group(1) in ids else None
bindings={n:owner(n) for n in generated};assert all(bindings.values())
assert owner('dev/codex/schubert/nk/unknown/Foreign$$Lambda+0x12') is None
rt=ET.parse(U/'coverage.xml').getroot();classes={x.get('name'):x for x in rt.findall('.//class')};assert set(classes)==set(ci)
coverage={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in rt.findall('counter')}
for k,v in coverage.items():
 for metric in ['covered','missed']:assert sum(int(x.get(metric)) for cl in classes.values() for x in cl.findall('counter') if x.get('type')==k)==v[metric]
uncovered={n:{x.get('type'):int(x.get('missed')) for x in cl.findall('counter') if int(x.get('missed'))>0} for n,cl in classes.items() if any(int(x.get('missed'))>0 for x in cl.findall('counter'))}
whole100=not uncovered and all(v['missed']==0 for v in coverage.values())
assert observed<=analyzed|switchmaps
targetNames={'dev/codex/schubert/nk/web/form/UserSearchForm'}
targetCounters={n:{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in classes[n].findall('counter')} for n in targetNames}
targetFour100={n:{'LINE','METHOD','CLASS','BRANCH'}<=set(row) and all(v['missed']==0 for v in row.values()) for n,row in targetCounters.items()}
# Do not require missing branches to disappear; preserve all target misses and independently list them.
# Reject invented positive-CRC or four100 labels, preserving full unexecuted exceptional source scope.
assert not (observed|{'foreign/Unknown'}) <= (analyzed|switchmaps)
assert set(ci)|{'foreign/Unknown'} != set(ids)-missing
assert not whole100 and uncovered
assert m['stages']['unit']['cwd']==str(U)
O.mkdir();files={}
for base,prefix in [(A,'unit-'),(U,'original-')]:
 for q in [x for x in base.iterdir() if x.is_file()]+list((base/'xml').glob('TEST-*.xml')):
  assert q.suffix!='.class';name='jacoco.exec' if q.name=='jacoco.exec' else prefix+('class-init.stdout' if q.name=='class-init.log' else q.name);assert name not in files;shutil.copyfile(q,O/name);files[name]=sha(O/name)
assert all(targetFour100.values())
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['productionCoreMain'],run=b['session'],tests=8,newTestDefinitions=8,physicalClasses=177,positiveMainCrc=len(observed),coverage=coverage,uncoveredFullSourceClasses=uncovered,wholeScopeFour100=whole100,targetFour100=targetFour100,targetCounters=targetCounters,ownNormalMainSources=1,physicalClassHashes=physical,classIds=ids,actualJvmCodeMethodCounts=methods,naturalNoCodeClasses=sorted(noCode),defaultStandardFilteredSwitchMaps=sorted(switchmaps),naturallyOmittedPackageAnnotations=sorted(missing),hiddenJvmAdapters=bindings,manualCoverageExclusions=[],oldExecCombined=False,preflight=ref(pf),inputHashes=b['inputHashes'],dependencies=b['dependencies'],environment=env,staticApplicable=0,processingErrors=0,unclassified=0,actualBackendNativeFsRootOrHeldClassActions=0,heldControllerTestExtractedOrSubstituted=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=8,physical=177,positiveCrc=len(observed),targetFour100=targetFour100,wholeFour100=whole100,manifest=ref(O/'manifest.json'))))
