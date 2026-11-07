"""Independent fifteen memory-JDBC cases/source/CRC/all written Code/normal synthetic filter proof."""
from pathlib import Path
import json,hashlib,datetime,re,subprocess,zipfile,shutil,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUN=R.parent/'pgpt-runs/PG379';U=RUN/'pg23654-service-db-admission-unit-v1';P=RUN/'pg23670-service-db-admission-compile-v1';S=RUN/'pg23672-service-db-admission-static-v1';O=B/'evidence/PG23656-service-db-admission-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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
assert not O.exists();m=load(U/'manifest.json');b=m['begin'];assert b==load(U/'begin.json') and re.fullmatch('[0-9a-f]{40}',b['source']) and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,15,0,0,0) and (b['newMethods'],b['requalifiedExistingMethods'])==(15,0);cfg=load(B/'input/500_service_db_admission_scope.json');assert b['selected']==list(cfg['testClasses'].values())
for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',b['normalSource'],b['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
for label,stage in m['stages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and '--scan-classpath' not in cmd and '--select-method' not in cmd and not any('--enable-native-access' in s for s in cmd);assert cmd[cmd.index('--select-class')+1]==b['selected'][0];testp=next(iter(cfg['testClasses']));text=(R/testp).read_text();expected={(b['selected'][0],n+'()') for n in re.findall(r'void\s+(dbAdmission\d{3}\w+)\s*\(',text)};assert len(expected)==15 and text.count('@Test')==15 and '@Timeout(10)' in text;cases=[];env={};timings=[]
for p in (U/'xml').glob('TEST-*.xml'):
 x=E.parse(p).getroot();assert not any(x.findall('.//'+tag) for tag in ['failure','error','skipped']);cases += [(c.get('classname'),c.get('name')) for c in x.findall('testcase')];timings += [dict(className=c.get('classname'),name=c.get('name'),seconds=c.get('time')) for c in x.findall('testcase')];env.update({c.get('name'):c.get('value') for c in x.findall('./properties/property') if c.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==15 and set(cases)==expected
for s in ['15 tests found','15 tests started','15 tests successful','0 tests aborted','0 tests skipped','0 containers aborted']:assert s in (U/'unit.stdout').read_text()
normal=RUN/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256']=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);normalBytes={};closure={};dependencyPhysical={};preflight=B/'evidence/PG23652-service-db-admission-preflight-v1/manifest.json';assert sha(preflight)=='3f18a00ff151a9fb14d9f92a04efb8ea3c71061cd80116cf62c293ee512ec873';pf=load(preflight);names={'ServiceDatabaseAdmission.java'};graph={Path(n).name for n in pf['dependencySourceHashes']}
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
info=(U/'classinfo.stdout').read_text();assert {n:i for i,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',info)}==ids;ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG23654-SERVICE-DB-ADMISSION-PORT15"' in ex;probes={n:[i,int(hit),int(total)] for i,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};prefix=b['selected'][0].replace('.','/');observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};assert set(closure)<=observed<=set(dependencyPhysical)
for n in observed:assert probes[n][0]==crc64(normalBytes[n])
for n in closure:assert probes[n][1]>0
init=(U/'class-init.log').read_text();productInit={n for n in re.findall(r"Initializing '([^']+)",init) if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};assert productInit<=set(dependencyPhysical);assert 'dev/codex/schubert/nk/storage/ServiceConfigFiles' not in productInit
for held in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']:assert held not in init
assert not any(s in init for s in ['org/postgresql/','com/zaxxer/hikari/','org/apache/activemq/','io/netty/','java/lang/foreign/','LinuxDirectoryCalls','LinuxProcess','ServiceProcessResources','RootBatch'])
root=E.parse(U/'coverage.xml').getroot();assert {c.get('name') for c in root.findall('.//class')}==set(closure);counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert all(v['missed']==0 for v in counters.values());assert {k:v['covered'] for k,v in counters.items() if k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=48,METHOD=5,CLASS=1,BRANCH=32)
# Compiler class is in the physical report, CRC and session; only pinned standard filtering applies.
metaSlot=RUN/'pg23688-jacoco-enum-filter-metadata-v1';fm=load(metaSlot/'manifest.json');assert sha(metaSlot/'manifest.json')=='e46fa84478c0a164f0bb4d923dbf8e926592a7778d6f668d2de1b043ff9c8f2e';assert fm['actualExit']==0 and fm['defaultSyntheticClassFilterVerified'];cli=R.parent/'toolchain/org.jacoco.cli-0.8.15-nodeps.jar';assert sha(cli)==fm['toolJarSha256']
for label,stage in fm['standardSyntheticClassFilterStages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(metaSlot/(label+'-exit.safe.json'));assert sha(metaSlot/(label+'.stdout'))==stage['stdoutSha256']
ftext=(metaSlot/'synthetic-class-filter.stdout').read_text();registry=(metaSlot/'default-filters.stdout').read_text();assert 'getClassAccess' in ftext and '4096' in ftext and 'IFilterOutput.ignore' in ftext and 'SyntheticClassFilter' in registry;methodClosure=[];filtered=[];writtenCode=0
for c in root.findall('.//class'):
 n=c.get('name');methods={(x.get('name'),x.get('desc')) for x in c.findall('method')};code={(x['name'],x['descriptor']) for x in closure[n]['methods'] if x['code']};assert methods<=code;omitted=code-methods
 if omitted:
  assert n.endswith('/ServiceDatabaseAdmission$1') and closure[n]['access']&4096 and code==omitted=={('<clinit>','()V')} and not methods and not c.findall('counter');filtered.append(dict(className=n,sourceFile=closure[n]['sourceFile'],classAccess=closure[n]['access'],methodNames=[dict(name=a,descriptor=z) for a,z in sorted(omitted)],reason='JAVAC_COMPILER_ENUM_SWITCH_TABLE_ACC_SYNTHETIC_CLASS_PINNED_STANDARD_SYNTHETIC_CLASS_FILTER',eligibleCounterDenominator=0,ratio=None,actualNormalClassId=ids[n],rawProbeCovered=probes[n][1],rawProbeTotal=probes[n][2],physicalClassRetained=True))
 else:
  assert not closure[n]['access']&4096 and len(code)==5;writtenCode+=len(code)
 methodClosure.append(dict(className=n,normalCodeMethods=len(code),reportMethods=len(methods),compilerFilteredCodeMethods=len(omitted),rawProbeCovered=probes[n][1],rawProbeTotal=probes[n][2],rawProbesNotClaimedAllExecuted=True))
assert len(filtered)==1 and writtenCode==counters['METHOD']['covered']==5;cm=load(P/'manifest.json');sm=load(S/'manifest.json');assert cm['inputHashes']==sm['inputHashes']==b['inputHashes'] and b['compileManifestSha256']==sha(P/'manifest.json');assert {str(p.relative_to(P/'classes')):sha(p) for p in (P/'classes').rglob('*.class')}==cm['classHashes'];assert pf['actualExit']==pf['pmdApplicable']==pf['checkstyle']==pf['unclassified']==0 and pf['pmdRaw']==6 and pf['inputHashes']==b['inputHashes'] and pf['staticManifestSha256']==sha(S/'manifest.json');assert pf['normalMainStaticUnchanged']=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2';assert pf['styleInverse'] and len(pf['staticClassifications'])==6 and pf['actualJdbcDriverOrDatabaseActions']==0 and pf['originalRealDatabaseTestOrFixtureCompiledOrRun'] is False
required=pf['sourceAssertionRecipes'];tokens=lambda s:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',s));valid=lambda candidate:all(tokens(v) in tokens(candidate) for v in required);assert valid(text);negatives=[('"08001"','"08002"'),('"schubert_app"','"arbitrary_role"'),('assertEquals(SQL, args[0]);','assertEquals(SQL, SQL);'),('assertEquals(SUCCESS, fixture.calls);','assertEquals(List.of(), fixture.calls);'),('fixture.assertCloses(1, 1);','fixture.assertCloses(0, 0);'),('assertSame(expected, assertThrows(AssertionError.class, () -> api().verify(fixture.connection)));','assertThrows(AssertionError.class, () -> api().verify(fixture.connection));')]
for old,new in negatives:assert tokens(old) in tokens(text) and not valid(tokens(text).replace(tokens(old),tokens(new)))
O.mkdir();files={}
for folder,pre in [(U,'original-'),(S,'static-'),(metaSlot,'sdk-')]:
 for p in [*folder.iterdir(),*sorted((folder/'xml').glob('TEST-*.xml'))]:
  if p.is_file():
   name='jacoco.exec' if p.name=='jacoco.exec' else pre+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=15,newUniqueTests=15,requalifiedSemanticContracts=0,newDirectWholeSourceProof=1,registeredWholeComponentDelta=None,coverage=counters,wholeWrittenTargetCodeCoverage100=True,branchStatus='FOUR_COUNTERS_100',sourceFilePhysicalClosure=closure,physical=physical,classIds=ids,normalObservedCrc={n:crc64(normalBytes[n]) for n in observed},normalProductInitializations=sorted(productInit),normalDependencyInitCount=len(productInit),methodClosure=methodClosure,automaticCompilerGeneratedFiltering=filtered,pinnedDefaultFilterMetadataManifestSha256=sha(metaSlot/'manifest.json'),wholeDependencyQualified=False,manualCoverageExclusions=[],oldExecCombined=False,sourceAssertionNegativeChecks=6,staticRaw=6,staticApplicable=0,checkstyle=0,staticPreflight=dict(path=str(preflight.relative_to(R)),sha256=sha(preflight)),inputHashes=b['inputHashes'],environment=env,caseTimings=timings,files=files,originalRealDatabaseTestsCompiled=0,actualJdbcDriverOrDatabaseActions=0,actualFilesystemOrDescriptorActions=0,actualBackendActions=0,heldFourInitializations=0,ownVirtualThreadTasks=8,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,bug='BUG-2491',ykt='YKT-2229',verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=15,newUnique=15,wholeDirectProof=1,coverage=counters,normalInit=len(productInit),sourceNegatives=6,compilerFilteredClasses=1,manifestSha256=sha(O/'manifest.json'))))
