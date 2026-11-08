"""Independent first16 XML, pinned whole SourceFile Code and source/oracle post; no target invocation."""
from pathlib import Path
import json,hashlib,datetime,re,subprocess,zipfile,shutil,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4]; B=R/'evidence/01_PT/007_NK-AUT-001'; RUN=R.parent/'pgpt-runs/PG379'
U=RUN/'pg23800-authentication-memory-port-unit-v1'; P=RUN/'pg23806-authentication-memory-port-compile-v1'; S=RUN/'pg23808-authentication-memory-port-static-v1'
O=B/'evidence/PG23816-authentication-memory-port-independent-v1'
load=lambda p:json.loads(p.read_bytes()); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def crc64(data):
 v=0
 for b in data:
  v^=b
  for _ in range(8):v=(v>>1)^0xd800000000000000 if v&1 else v>>1
 return f'{v:016x}'

def metadata(data):
 assert data[:4]==bytes.fromhex('cafebabe');pool={};p=10;i=1;count=int.from_bytes(data[8:10],'big')
 while i<count:
  t=data[p];p+=1
  if t==1:n=int.from_bytes(data[p:p+2],'big');p+=2;pool[i]=data[p:p+n].decode('utf8','replace');p+=n
  elif t in (7,8,16,19,20):pool[i]=int.from_bytes(data[p:p+2],'big');p+=2
  elif t in (3,4,9,10,11,12,17,18):p+=4
  elif t in (5,6):p+=8;i+=1
  elif t==15:p+=3
  else:raise AssertionError(t)
  i+=1
 access=int.from_bytes(data[p:p+2],'big');name=pool[pool[int.from_bytes(data[p+2:p+4],'big')]];p+=6;n=int.from_bytes(data[p:p+2],'big');p+=2+2*n
 def attrs(p):
  n=int.from_bytes(data[p:p+2],'big');p+=2;out={}
  for _ in range(n):
   k=pool[int.from_bytes(data[p:p+2],'big')];length=int.from_bytes(data[p+2:p+6],'big');p+=6;out[k]=data[p:p+length];p+=length
  return p,out
 methods=[]
 for section in range(2):
  n=int.from_bytes(data[p:p+2],'big');p+=2
  for _ in range(n):
   method_access=int.from_bytes(data[p:p+2],'big');label=pool[int.from_bytes(data[p+2:p+4],'big')];descriptor=pool[int.from_bytes(data[p+4:p+6],'big')];p+=6;p,a=attrs(p)
   if section:methods.append(dict(name=label,descriptor=descriptor,code='Code' in a,access=method_access))
 p,a=attrs(p);assert p==len(data);return dict(name=name,access=access,sourceFile=pool[int.from_bytes(a['SourceFile'],'big')],methods=methods)
assert not O.exists()
m=load(U/'manifest.json'); b=m['begin']; cfg=load(B/'input/017_authentication_memory_port_scope.json')
assert b==load(U/'begin.json') and re.fullmatch('[0-9a-f]{40}',b['source'])
assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,16,0,0,0)
assert b['newMethods']==16 and b['requalifiedExistingMethods']==0 and b['selected']==list(cfg['testClasses'].values())
for n,h in b['inputHashes'].items():
 assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',b['normalSource'],b['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()
for p,h in b['dependencies'].items(): assert sha(Path(p))==h
for label,stage in m['stages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
 for stream in ('stdout','stderr'):assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command']; assert cmd.count('--select-class')==1 and cmd[cmd.index('--select-class')+1]==b['selected'][0]
assert '--scan-classpath' not in cmd and '--select-method' not in cmd and not any('--enable-native-access' in x for x in cmd)
testp=next(iter(cfg['testClasses'])); text=(R/testp).read_text()
expected={(b['selected'][0],n+'()') for n in re.findall(r'void\s+(memory\d{3}\w+)\s*\(',text)}
assert len(expected)==16 and text.count('@Test')==16
cases=[]; timings=[]; env={}
for p in (U/'xml').glob('TEST-*.xml'):
 x=E.parse(p).getroot(); assert not any(x.findall('.//'+tag) for tag in ('failure','error','skipped'))
 cases.extend((c.get('classname'),c.get('name')) for c in x.findall('testcase'))
 timings.extend(dict(name=c.get('name'),seconds=c.get('time')) for c in x.findall('testcase'))
 env.update({c.get('name'):c.get('value') for c in x.findall('./properties/property') if c.get('name') in ('os.name','os.arch','java.version','file.encoding','user.timezone')})
assert len(cases)==16 and set(cases)==expected
for phrase in ('16 tests found','16 tests started','16 tests successful','0 tests aborted','0 tests skipped','0 containers aborted'):
 assert phrase in (U/'unit.stdout').read_text()
normal=RUN/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json'
assert sha(normal)==b['normalManifestSha256']=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27'
nm=load(normal); assert b['normalSource']==nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
pfp=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23798-authentication-memory-port-preflight-v1/manifest.json'
assert sha(pfp)=='c44fdb4abb1a6a131f8b6319afa212cfd47be3e4a690080e8d2a83ed72eec584'
pf=load(pfp); normalBytes={}; closure={}
for row in pf['sourceGraph']:
 n=row['className']; module='api' if '/schubert-nk-api/' in row['source'] else 'protocol'
 jar=Path(nm['jars'][module]['path']); assert sha(jar)==nm['jars'][module]['sha256']
 with zipfile.ZipFile(jar) as z:data=z.read(n+'.class')
 normalBytes[n]=data
 if row['source'].endswith('/AuthenticationService.java'): closure[n]=metadata(data)
assert set(closure)==set(cfg['targetPhysical']) and len(closure)==1
physical={n:hashlib.sha256(normalBytes[n]).hexdigest() for n in closure}; ids={n:crc64(normalBytes[n]) for n in closure}
assert m['physical']==physical and all(sha(U/'component'/(n+'.class'))==h for n,h in physical.items())
info=(U/'classinfo.stdout').read_text(); assert {n:i for i,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',info)}==ids
ex=(U/'execinfo.stdout').read_text(); assert ex.count('Session "')==1 and 'Session "PG23800-AUTHENTICATION-MEMORY-PORT16"' in ex
probes={n:[i,int(hit),int(total)] for i,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)}
prefix=b['selected'][0].replace('.','/'); observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)}
assert set(closure)<=observed<=set(normalBytes)
for n in observed: assert probes[n][0]==crc64(normalBytes[n])
init=(U/'class-init.log').read_text(); initialized={n for n in re.findall(r"Initializing '([^']+)",init) if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)}
generated=initialized-set(normalBytes); assert all('$$Lambda+' in n and n.split('$$Lambda+',1)[0] in normalBytes for n in generated)
for held in ('TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'): assert held not in init
assert not any(s in init for s in ('org/postgresql/','com/zaxxer/hikari/','org/apache/activemq/','io/netty/','java/lang/foreign/','LinuxDirectoryCalls','LinuxProcess','ServiceProcessResources','RootBatch'))
root=E.parse(U/'coverage.xml').getroot(); assert {c.get('name') for c in root.findall('.//class')}==set(closure)
counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')}
assert all(v['missed']==0 for v in counters.values())
assert {k:counters[k]['covered'] for k in ('LINE','METHOD','CLASS','BRANCH')}==dict(LINE=54,METHOD=5,CLASS=1,BRANCH=24)
methodClosure=[]
for c in root.findall('.//class'):
 n=c.get('name'); methods={(v.get('name'),v.get('desc')) for v in c.findall('method')}
 code={(v['name'],v['descriptor']) for v in closure[n]['methods'] if v['code']}
 assert methods==code and len(code)==5 and not closure[n]['access']&4096
 methodClosure.append(dict(className=n,normalCodeMethods=len(code),reportMethods=len(methods),rawProbeCovered=probes[n][1],rawProbeTotal=probes[n][2],rawProbesNotClaimedAllExecuted=True))
cm=load(P/'manifest.json'); sm=load(S/'manifest.json')
assert cm['inputHashes']==sm['inputHashes']==b['inputHashes']==pf['inputHashes']
assert b['compileManifestSha256']==sha(P/'manifest.json') and pf['staticManifestSha256']==sha(S/'manifest.json')
assert {str(p.relative_to(P/'classes')):sha(p) for p in (P/'classes').rglob('*.class')}==cm['classHashes']
assert pf['actualExit']==pf['pmdApplicable']==pf['checkstyle']==pf['unclassified']==0 and pf['pmdRaw']==8
assert pf['styleInverse'] and len(pf['staticClassifications'])==8 and pf['actualJdbcDriverOrDatabaseActions']==0
assert pf['normalMainStaticUnchanged']=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2'
assert pf['defaultMatcherInvoked'] is False and pf['originalRealDatabaseTestOrFixtureCompiledOrRun'] is False
tokens=lambda s:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',s))
required=pf['sourceAssertionRecipes']; valid=lambda candidate:all(tokens(v) in tokens(candidate) for v in required)
assert valid(text)
negatives=[
 ('assertEquals(900, result.retryAfterSeconds());','assertEquals(899, result.retryAfterSeconds());'),
 ('new long[] {1_000_001_000L, 2}','new long[] {1_000_001_000L, 1}'),
 ('assertEquals(3, f.param(Stage.UPDATE_USER, 1));','assertEquals(2, f.param(Stage.UPDATE_USER, 1));'),
 ('assertArrayEquals(new char[16], password);','assertArrayEquals(password, password);'),
 ('assertEquals(1, statement.closed);','assertEquals(0, statement.closed);'),
 ('assertEquals(expectedDisplay, param(Stage.LOGIN_AUDIT, 8));','assertEquals(KEY, param(Stage.LOGIN_AUDIT, 8));'),
 ('assertTrue(oldest.equals(f.param(Stage.SESSION_REPLACE, 2)));','assertTrue(true);'),
 ('assertEquals(8, secondResult.actor().userId());','assertEquals(7, secondResult.actor().userId());')]
for old,new in negatives:
 assert tokens(old) in tokens(text) and not valid(tokens(text).replace(tokens(old),tokens(new)))
assert text.count('f.verifyReleasedAndConsumed();')==22
assert len(cfg['mainPaths'])==28 and len(pf['sourceGraph'])==31 and len(pf['staticClassifications'])==8
O.mkdir(); files={}
for folder,pre in ((U,'original-'),(S,'static-')):
 for p in [*folder.iterdir(),*sorted((folder/'xml').glob('TEST-*.xml'))]:
  if p.is_file():
   name='jacoco.exec' if p.name=='jacoco.exec' else pre+('class-init.stdout' if p.name=='class-init.log' else p.name)
   assert name not in files; shutil.copyfile(p,O/name);files[name]=sha(O/name)
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=16,newUniqueTests=16,requalifiedSemanticContracts=0,newDirectWholeSourceProof=1,registeredWholeComponentDelta=None,coverage=counters,wholeWrittenTargetCodeCoverage100=True,branchStatus='FOUR_COUNTERS_100',sourceFilePhysicalClosure=closure,physical=physical,classIds=ids,normalObservedCrc={n:crc64(normalBytes[n]) for n in observed},normalProductInitializations=sorted(initialized),normalDependencyInitCount=len(initialized),methodClosure=methodClosure,wholeDependencyQualified=False,manualCoverageExclusions=[],oldExecCombined=False,sourceAssertionNegativeChecks=len(negatives),staticRaw=8,staticApplicable=0,checkstyle=0,staticPreflight=dict(path=str(pfp.relative_to(R)),sha256=sha(pfp)),inputHashes=b['inputHashes'],environment=env,caseTimings=timings,files=files,originalRealDatabaseTestsCompiled=0,actualJdbcDriverOrDatabaseActions=0,actualLoginOrSessionAgainstServer=False,actualBackendActions=0,heldFourInitializations=0,ownLocalSyntheticJca=True,defaultMatcherInvoked=False,ownFixedJvmTasks=2,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,bugs=['BUG-2499','BUG-2500'],ykts=['YKT-2237','YKT-2238'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=16,newUnique=16,wholeDirectProof=1,coverage=counters,normalInit=len(initialized),sourceNegatives=len(negatives),manifestSha256=sha(O/'manifest.json'))))
