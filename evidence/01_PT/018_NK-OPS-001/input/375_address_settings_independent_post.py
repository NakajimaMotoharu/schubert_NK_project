"""Independent fixed-source five-case XML/CRC/physical/source closure and literal oracle verification."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg23224-address-settings-port-unit-v1';PRE=RUNS/'pg23228-address-settings-port-compile-v1';S=RUNS/'pg23230-address-settings-port-static-v1';O=B/'evidence/PG23238-address-settings-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
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
 name=pool[pool[int.from_bytes(data[p+2:p+4],'big')]];p+=6;n=int.from_bytes(data[p:p+2],'big');p+=2+2*n
 def attrs(p):
  n=int.from_bytes(data[p:p+2],'big');p+=2;out={}
  for _ in range(n):
   k=pool[int.from_bytes(data[p:p+2],'big')];length=int.from_bytes(data[p+2:p+6],'big');p+=6;out[k]=data[p:p+length];p+=length
  return p,out
 methods=[]
 for section in range(2):
  n=int.from_bytes(data[p:p+2],'big');p+=2
  for _ in range(n):
   label=pool[int.from_bytes(data[p+2:p+4],'big')];descriptor=pool[int.from_bytes(data[p+4:p+6],'big')];p+=6;p,a=attrs(p)
   if section:methods.append(dict(name=label,descriptor=descriptor,code='Code' in a))
 p,a=attrs(p);assert p==len(data);return dict(name=name,sourceFile=pool[int.from_bytes(a['SourceFile'],'big')],methods=methods)
def recipe(text):
 required=['REQUEST, List.of("33554432", "50", "234881024", "450")','"nk.sync.reply.web", List.of("33554432", "50", "234881024", "450")','"nk.async.work", List.of("134217728", THOUSAND, "939524096", NINE_THOUSAND)','"nk.web.log", List.of("67108864", THOUSAND, "201326592", NINE_THOUSAND)','"nk.dead.letter", List.of("134217728", THOUSAND, "2013265920", NINE_THOUSAND)','"nk.expiry", List.of("67108864", THOUSAND, "1006632960", NINE_THOUSAND)','Map.entry("pageSizeBytes", "8388608")','Map.entry("maxReadPageBytes", "16777216")','Map.entry("maxDeliveryAttempts", "4")','Map.entry("redeliveryMultiplier", "5.0")','private static final int FAILURE_READ = 3;']
 return all(v in ' '.join(text.split()) for v in required)
assert not O.exists();cfg=load(B/'input/373_address_settings_scope.json');m=load(U/'manifest.json');b=m['begin'];assert load(U/'begin.json')==b and (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,5,0,0,0);assert b['source']=='01dbe0a53a245ed43e17c2b81acc12d11c450d29';assert b['selected']==list(cfg['testClasses'].values())
for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',b['normalSource'],b['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()
for p,h in b['dependencies'].items():assert sha(p)==h
for label,stage in m['stages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
test=next(iter(cfg['testClasses']));text=(R/test).read_text();assert recipe(text);prefix=b['selected'][0].replace('.','/');expected={(b['selected'][0],n+'()') for n in re.findall(r'@Test\s+void\s+(\w+)\(',text)};assert len(expected)==5
neg=0
for old,new in [('"234881024"','"234881025"'),('"2013265920"','"2013265921"'),('FAILURE_READ = 3','FAILURE_READ = 4')]:
 assert old in text and not recipe(text.replace(old,new,1));neg+=1
cases=[];environment={}
for p in (U/'xml').glob('TEST-*.xml'):
 root=E.parse(p).getroot();assert not any(root.findall('.//'+x) for x in ['failure','error','skipped']);cases += [(x.get('classname'),x.get('name')) for x in root.findall('testcase')];environment.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==5 and set(cases)==expected
stdout=(U/'unit.stdout').read_text()
for t in ['5 tests found','5 tests started','5 tests successful','0 tests aborted','0 tests skipped','0 containers aborted']:assert t in stdout
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);normalBytes={};target=cfg['targetPhysical'][0];sourceClosure={}
for module in ['batch','protocol','storage','bootstrap']:
 jar=Path(nm['jars'][module]['path']);assert sha(jar)==nm['jars'][module]['sha256']
 with zipfile.ZipFile(jar) as z:
  for name in z.namelist():
   if name.endswith('.class'):
    n=name[:-6];assert n not in normalBytes;normalBytes[n]=z.read(name)
    if module=='batch':
     meta=metadata(normalBytes[n])
     if meta['sourceFile']=='ArtemisAddressSettingsReadinessClient.java':sourceClosure[n]=meta
assert set(sourceClosure)==set(cfg['targetPhysical']) and len(sourceClosure)==3
physical={n:hashlib.sha256(normalBytes[n]).hexdigest() for n in sourceClosure};ids={n:crc64(normalBytes[n]) for n in sourceClosure};assert m['physical']==physical
for n,h in physical.items():assert sha(U/'component'/(n+'.class'))==h
assert {n:i for i,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())}==ids
assert all(not v['code'] for v in sourceClosure[target+'$Reader']['methods']);capacityCode=[v['name'] for v in sourceClosure[target+'$Capacity']['methods'] if v['code']];assert set(capacityCode)=={'<init>','memoryMib','memoryMessages','pageMib','pageMessages','equals','hashCode','toString'}
ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG23224-ADDRESS-SETTINGS-PROJECTION"' in ex;probes={n:[i,int(hit),int(total)] for i,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};assert observed=={target,target+'$Capacity','dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessException'}
for n in observed:assert probes[n][0]==crc64(normalBytes[n]) and probes[n][1]>0
initlog=(U/'class-init.log').read_text();init={n for n in re.findall(r"Initializing '([^']+)",initlog) if n.startswith('dev/codex/schubert/nk/') and not n.startswith(prefix)};real=init&set(normalBytes);generated=init-real;assert real==observed and len(generated)==1;assert all(re.fullmatch(re.escape(target)+r'\$\$Lambda\+0x[0-9a-f]+',n) for n in generated)
for held in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']:assert held not in initlog
rv=load(B/'input/011_acceptor_parser_port_sdk_review.json');sdkInit={n for n in re.findall(r"Initializing '([^']+)",initlog) if n.startswith('org/apache/activemq')};assert len(sdkInit)==72
assert all(n in rv['allowedInitializedClasses'] or any(n.startswith(p) for p in rv['allowedGeneratedLambdaPrefixes']) for n in sdkInit)
root=E.parse(U/'coverage.xml').getroot();assert {n.get('name') for n in root.findall('.//class')}==set(sourceClosure);counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert all(x['missed']==0 for x in counters.values());assert {k:counters[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=68,METHOD=9,CLASS=2,BRANCH=10)
pm=load(PRE/'manifest.json');assert pm['actualExit']==0 and pm['inputHashes']==b['inputHashes'] and b['compileManifestSha256']==sha(PRE/'manifest.json');assert {str(p.relative_to(PRE/'classes')):sha(p) for p in (PRE/'classes').rglob('*.class')}==pm['classHashes'];sp=B/'evidence/PG23232-address-settings-static-preflight-v1/manifest.json';st=load(sp);assert st['actualExit']==st['pmdApplicable']==st['checkstyle']==st['unclassified']==0 and st['inputHashes']==b['inputHashes'] and st['staticManifestSha256']==sha(S/'manifest.json');O.mkdir();files={}
for folder,pref in [(U,'original-'),(S,'static-')]:
 for p in [*folder.iterdir(),*sorted((folder/'xml').glob('TEST-*.xml'))]:
  if p.is_file():
   name='jacoco.exec' if p.name=='jacoco.exec' else pref+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=5,newUniqueTests=5,newDirectWholeSourceProof=1,registeredWholeComponentDelta=None,registryDedupRequired=True,coverage=counters,wholeTargetCodeCoverage100=True,physical=physical,sourceFilePhysicalClosure=sourceClosure,sourcePhysicalCount=3,normalCodeClasses=2,abstractNoCode=1,standardCompilerFilters='JaCoCo0.8.15 standard record-generated accessor/equality/hash/toString filters, all original Capacity bytes retained. These7 generated methods are not manually excluded or claimed independently executed; outer8 user/initializer methods and record ctor1 measured.',manualCoverageExclusions=[],oldExecCombined=False,classIds=ids,normalObservedCrc={n:crc64(normalBytes[n]) for n in sorted(observed)},normalProductInitializations=sorted(real),jvmGeneratedLambdaOwners={n:target for n in generated},sdkInitializationsWithinPriorStaticReview=sorted(sdkInit),sdkInitCount=72,sourceRecipeNegativeChecks=neg,staticRaw=1,staticApplicable=0,checkstyle=0,staticPreflight=dict(path=str(sp.relative_to(R)),sha256=sha(sp)),environment=environment,inputHashes=b['inputHashes'],files=files,actualBrokerConnections=0,sessionOperations=0,actualVMDatabaseRootNativeCredentialOperations=0,heldFourInitializations=0,originalTestsCompiled=0,newFixtureReplacesHeldBackendTest=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,bugs=['BUG-2478'],ykts=['YKT-2216'],verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=5,fourCounters=counters,newDirectWholeSourceProof=1,registrationDelta=None,normalInit=3,sdkInit=72,manifestSha256=sha(O/'manifest.json'))))
