"""Independent fourteen memory-Connector cases/source/CRC/all written Code/abstract interface proof."""
from pathlib import Path
import json,hashlib,datetime,re,subprocess,zipfile,shutil,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUN=R.parent/'pgpt-runs/PG379';U=RUN/'pg23702-service-database-source-unit-v1';P=RUN/'pg23728-service-database-source-compile-v1';S=RUN/'pg23730-service-database-source-static-v1';O=B/'evidence/PG23704-service-database-source-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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
assert not O.exists();m=load(U/'manifest.json');b=m['begin'];assert b==load(U/'begin.json') and re.fullmatch('[0-9a-f]{40}',b['source']) and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,14,0,0,0) and (b['newMethods'],b['requalifiedExistingMethods'])==(14,0);cfg=load(B/'input/506_service_database_source_scope.json');assert b['selected']==list(cfg['testClasses'].values())
for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',b['normalSource'],b['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
for label,stage in m['stages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and '--scan-classpath' not in cmd and '--select-method' not in cmd and not any('--enable-native-access' in s for s in cmd);assert cmd[cmd.index('--select-class')+1]==b['selected'][0];testp=next(iter(cfg['testClasses']));text=(R/testp).read_text();expected={(b['selected'][0],n+'()') for n in re.findall(r'void\s+(dbSource\d{3}\w+)\s*\(',text)};assert len(expected)==14 and text.count('@Test')==14 and '@Timeout(10)' in text;cases=[];env={};timings=[]
for p in (U/'xml').glob('TEST-*.xml'):
 x=E.parse(p).getroot();assert not any(x.findall('.//'+tag) for tag in ['failure','error','skipped']);cases += [(c.get('classname'),c.get('name')) for c in x.findall('testcase')];timings += [dict(className=c.get('classname'),name=c.get('name'),seconds=c.get('time')) for c in x.findall('testcase')];env.update({c.get('name'):c.get('value') for c in x.findall('./properties/property') if c.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==14 and set(cases)==expected
for s in ['14 tests found','14 tests started','14 tests successful','0 tests aborted','0 tests skipped','0 containers aborted']:assert s in (U/'unit.stdout').read_text()
normal=RUN/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256']=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);normalBytes={};closure={};dependencyPhysical={};preflight=B/'evidence/PG23700-service-database-source-preflight-v1/manifest.json';assert sha(preflight)=='3638c2bb81209c86c19ed4dead4e1deb74098efc013ce5ecab8ac81ffbdd1659';pf=load(preflight);names={'ServiceDatabaseSource.java'};graph={Path(n).name for n in pf['dependencySourceHashes']}
for module in cfg['modules']:
 jar=Path(nm['jars'][module]['path']);assert sha(jar)==nm['jars'][module]['sha256']
 with zipfile.ZipFile(jar) as z:
  for name in z.namelist():
   if name.endswith('.class'):
    data=z.read(name);meta=metadata(data);n=name[:-6];assert n not in normalBytes;normalBytes[n]=data
    if meta['sourceFile'] in names:closure[n]=meta
    if meta['sourceFile'] in graph:dependencyPhysical[n]=meta
assert set(closure)==set(cfg['targetPhysical']) and len(closure)==2;physical={n:hashlib.sha256(normalBytes[n]).hexdigest() for n in closure};ids={n:crc64(normalBytes[n]) for n in closure};assert m['physical']==physical
for n,h in physical.items():assert sha(U/'component'/(n+'.class'))==h
info=(U/'classinfo.stdout').read_text();assert {n:i for i,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',info)}==ids;ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG23702-SERVICE-DATABASE-SOURCE-PORT14"' in ex;probes={n:[i,int(hit),int(total)] for i,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};prefix=b['selected'][0].replace('.','/');observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};codeClasses={n for n,v in closure.items() if any(m['code'] for m in v['methods'])};noCodeClasses=set(closure)-codeClasses;assert len(codeClasses)==len(noCodeClasses)==1 and codeClasses<=observed<=set(dependencyPhysical)
for n in observed:assert probes[n][0]==crc64(normalBytes[n])
for n in codeClasses:assert probes[n][1]>0
for n in noCodeClasses:assert n not in probes or probes[n][2]==0
init=(U/'class-init.log').read_text();productInit={n for n in re.findall(r"Initializing '([^']+)",init) if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};generated={n for n in productInit if n not in dependencyPhysical};assert all('$$Lambda+' in n and n.split('$$Lambda+',1)[0] in dependencyPhysical for n in generated);assert 'dev/codex/schubert/nk/storage/ServiceConfigFiles' not in productInit
for held in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']:assert held not in init
assert not any(s in init for s in ['org/postgresql/','com/zaxxer/hikari/','org/apache/activemq/','io/netty/','java/lang/foreign/','LinuxDirectoryCalls','LinuxProcess','ServiceProcessResources','RootBatch'])
root=E.parse(U/'coverage.xml').getroot();assert {c.get('name') for c in root.findall('.//class')}==set(closure);counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert all(v['missed']==0 for v in counters.values());assert {k:v['covered'] for k,v in counters.items() if k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=66,METHOD=16,CLASS=1,BRANCH=24)
# Abstract Connector is retained physically and in the report; it has no executable Code.
methodClosure=[];noCode=[];writtenCode=0
for c in root.findall('.//class'):
 n=c.get('name');methods={(x.get('name'),x.get('desc')) for x in c.findall('method')};code={(x['name'],x['descriptor']) for x in closure[n]['methods'] if x['code']};assert methods==code
 if not code:
  assert n.endswith('/ServiceDatabaseSource$Connector') and closure[n]['access']&512 and all(x['access']&1024 for x in closure[n]['methods']) and not c.findall('counter');noCode.append(dict(className=n,sourceFile=closure[n]['sourceFile'],classAccess=closure[n]['access'],abstractMethodsWithoutCode=len(closure[n]['methods']),eligibleCounterDenominator=0,ratio=None,physicalClassRetained=True,normalClassId=ids[n]))
 else:assert not closure[n]['access']&4096 and len(code)==16;writtenCode+=len(code)
 methodClosure.append(dict(className=n,normalCodeMethods=len(code),reportMethods=len(methods),rawProbeCovered=probes[n][1] if n in probes else None,rawProbeTotal=probes[n][2] if n in probes else None,rawProbesNotClaimedAllExecuted=True))
assert len(noCode)==1 and writtenCode==counters['METHOD']['covered']==16;
cm=load(P/'manifest.json');sm=load(S/'manifest.json');assert cm['inputHashes']==sm['inputHashes']==b['inputHashes'] and b['compileManifestSha256']==sha(P/'manifest.json');assert {str(p.relative_to(P/'classes')):sha(p) for p in (P/'classes').rglob('*.class')}==cm['classHashes'];assert pf['actualExit']==pf['pmdApplicable']==pf['checkstyle']==pf['unclassified']==0 and pf['pmdRaw']==10 and pf['inputHashes']==b['inputHashes'] and pf['staticManifestSha256']==sha(S/'manifest.json');assert pf['normalMainStaticUnchanged']=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2';assert pf['styleInverse'] and len(pf['staticClassifications'])==10 and pf['actualJdbcDriverOrDatabaseActions']==0 and pf['originalRealDatabaseTestOrFixtureCompiledOrRun'] is False
required=pf['sourceAssertionRecipes'];tokens=lambda s:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',s));valid=lambda candidate:all(tokens(v) in tokens(candidate) for v in required);assert valid(text);negatives=[('"08001"','"08002"'),('"0A000"','"0A001"'),('assertEquals(SQL, args[0]);','assertEquals(SQL, SQL);'),('assertEquals(4, properties.size());','assertEquals(0, properties.size());'),('assertEquals(role, properties.getProperty(USER));','assertEquals(USER, properties.getProperty(USER));'),('assertTrue(captured.get().isEmpty());','assertFalse(captured.get().isEmpty());'),('assertEquals(0, fixture.connectionCloses);','assertEquals(1, fixture.connectionCloses);'),('fixedSecondary(expected);','fixedSecondary(new SQLException());')]
for old,new in negatives:assert tokens(old) in tokens(text) and not valid(tokens(text).replace(tokens(old),tokens(new)))
assert pf['compileAndLifetimePatchesInverse'] and pf['beforeManifestPreserved'] and pf['driverManagerDefaultConnectorInvoked'] is False and pf['ownDriverRegistration'] is False and pf['newSchemaTests']==0
O.mkdir();files={}
for folder,pre in [(U,'original-'),(S,'static-')]:
 for p in [*folder.iterdir(),*sorted((folder/'xml').glob('TEST-*.xml'))]:
  if p.is_file():
   name='jacoco.exec' if p.name=='jacoco.exec' else pre+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=14,newUniqueTests=14,requalifiedSemanticContracts=0,newDirectWholeSourceProof=1,registeredWholeComponentDelta=None,coverage=counters,wholeWrittenTargetCodeCoverage100=True,branchStatus='FOUR_COUNTERS_100',sourceFilePhysicalClosure=closure,physical=physical,classIds=ids,normalObservedCrc={n:crc64(normalBytes[n]) for n in observed},normalProductInitializations=sorted(productInit),normalDependencyInitCount=len(productInit),methodClosure=methodClosure,abstractNoCodeInterfaces=noCode,wholeDependencyQualified=False,manualCoverageExclusions=[],oldExecCombined=False,sourceAssertionNegativeChecks=8,staticRaw=10,staticApplicable=0,checkstyle=0,staticPreflight=dict(path=str(preflight.relative_to(R)),sha256=sha(preflight)),inputHashes=b['inputHashes'],environment=env,caseTimings=timings,files=files,originalRealDatabaseTestsCompiled=0,actualJdbcDriverOrDatabaseActions=0,actualFilesystemOrDescriptorActions=0,actualBackendActions=0,heldFourInitializations=0,ownVirtualThreadTasks=10,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,bugs=['BUG-2492','BUG-2493','BUG-2494','BUG-2495'],ykts=['YKT-2230','YKT-2231','YKT-2232','YKT-2233'],driverManagerDefaultConnectorInvoked=False,defaultNonInvocationEvidence=pf['defaultNonInvocationEvidence'],ownDriverRegistration=False,existingSchemaProofReused=pf['existingSchemaProofReused'],newSchemaTests=0,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=14,newUnique=14,wholeDirectProof=1,coverage=counters,normalInit=len(productInit),sourceNegatives=8,abstractNoCodeInterfaces=1,manifestSha256=sha(O/'manifest.json'))))
