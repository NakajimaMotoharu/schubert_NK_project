"""Independent exact21 terminal and normal whole SourceFile Code proof, no Product replay."""
from pathlib import Path
import json,hashlib,datetime,re,subprocess,zipfile,shutil,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUN=R.parent/'pgpt-runs/PG379';U=RUN/'pg23394-web-service-metric21-unit-v1';P=RUN/'pg23404-web-service-metric21-compile-v1';S=RUN/'pg23406-web-service-metric21-static-v1';O=B/'evidence/PG23396-web-service-metric21-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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
assert not O.exists();m=load(U/'manifest.json');b=m['begin'];assert load(U/'begin.json')==b and b['source']=='5eebf3a86fbba3e6b74edda93ba20612d3eda4f5' and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,21,0,0,0) and (b['newMethods'],b['requalifiedExistingMethods'])==(0,21)
cfg=load(B/'input/419_web_service_metric_scope.json');assert b['selected']==list(cfg['testClasses'].values()) and b['selectedMethods']==cfg['selectedMethods'] and b['heldMethods']==cfg['heldMethods'];assert len(b['selectedMethods'])==21 and len(b['heldMethods'])==1
for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',b['normalSource'],b['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()
for p,h in b['dependencies'].items():assert sha(Path(p))==h
for label,stage in m['stages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-method')==21 and '--scan-classpath' not in cmd and '--select-class' not in cmd and not any('--enable-native-access' in x for x in cmd);assert {cmd[i+1] for i,x in enumerate(cmd[:-1]) if x=='--select-method'}=={b['selected'][0]+'#'+n+'()' for n in cfg['selectedMethods']};assert not any('webservice009' in x for x in cmd)
for p,h in b['emptyConfigHashes'].items():assert h=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' and sha(Path(p))==h
assert '-Dprometheus.config='+str(U/'empty-prometheus.properties') in cmd;cp=cmd[cmd.index('--class-path')+1].split(':');assert cp==[str(P/'classes'),*b['dependencies']];assert (P/'classes/prometheus.properties').read_bytes()==b''
caseSet=set();caseTimes=[];env={}
for p in (U/'xml').glob('TEST-*.xml'):
 root=E.parse(p).getroot();assert not any(root.findall('.//'+tag) for tag in ['failure','error','skipped'])
 for t in root.findall('testcase'):
  case=(t.get('classname'),t.get('name'));assert case not in caseSet;caseSet.add(case);caseTimes.append(dict(className=case[0],name=case[1],seconds=t.get('time')))
 env.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(caseSet)==21 and caseSet=={(b['selected'][0],n+'()') for n in cfg['selectedMethods']};assert not any('webservice009' in n for _,n in caseSet)
for text in ['21 tests found','21 tests started','21 tests successful','0 tests aborted','0 tests skipped','0 containers aborted']:assert text in (U/'unit.stdout').read_text()
normal=RUN/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);normalBytes={};closure={};physical={};targetFile='WebServiceMetricBinding.java'
for module in ['web','protocol','storage','bootstrap']:
 jar=Path(nm['jars'][module]['path']);assert sha(jar)==nm['jars'][module]['sha256']
 with zipfile.ZipFile(jar) as z:
  for name in z.namelist():
   if name.endswith('.class'):
    data=z.read(name);n=name[:-6];assert n not in normalBytes;normalBytes[n]=data;meta=metadata(data)
    if meta['sourceFile']==targetFile:closure[n]=meta;physical[n]=hashlib.sha256(data).hexdigest()
assert set(closure)==set(cfg['targetPhysical']) and len(closure)==1 and m['physical']==physical
for n,h in physical.items():assert sha(U/'component'/(n+'.class'))==h
ids={n:crc64(normalBytes[n]) for n in closure};assert {n:i for i,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())}==ids
ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG23394-WEB-SERVICE-METRIC21"' in ex;probes={n:[i,int(hit),int(total)] for i,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};testPrefixes=[n.replace('.','/') for n in [*b['selected'],'dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricObservationTest']];isTest=lambda n:any(n.startswith(p) for p in testPrefixes);observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not isTest(n)};assert set(closure)<=observed<=set(normalBytes)
for n in observed:assert probes[n][0]==crc64(normalBytes[n]) and probes[n][1]>0
initlog=(U/'class-init.log').read_text();allInit=set(re.findall(r"Initializing '([^']+)",initlog));prodInit={n for n in allInit if n.startswith('dev/codex/schubert/nk/') and not isTest(n)};generated={n for n in prodInit if n not in normalBytes}
for n in generated:assert '$$Lambda+' in n and n.split('$$Lambda+',1)[0] in normalBytes
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(h in n for n in prodInit|observed for h in held);assert not any(n.startswith(('org/postgresql/','org/apache/activemq/','io/opentelemetry/','org/apache/tomcat/jni/','org/apache/tomcat/util/net/openssl/')) for n in allInit);assert not any(n.startswith('dev/codex/schubert/nk/storage/Linux') for n in prodInit);assert not any(n.startswith(('com/zaxxer/hikari/pool/','com/zaxxer/hikari/HikariDataSource')) for n in allInit)
root=E.parse(U/'coverage.xml').getroot();assert {c.get('name') for c in root.findall('.//class')}==set(closure);counter={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert all(x['missed']==0 for x in counter.values());assert {k:counter[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH']}==dict(LINE=30,METHOD=6,CLASS=1,BRANCH=8)
for c in root.findall('.//class'):
 n=c.get('name');methods={(x.get('name'),x.get('desc')) for x in c.findall('method')};code={(x['name'],x['descriptor']) for x in closure[n]['methods'] if x['code']};assert len(code)==6 and methods==code
cm=load(P/'manifest.json');sm=load(S/'manifest.json');assert cm['actualExit']==0 and cm['inputHashes']==sm['inputHashes']==b['inputHashes'] and b['compileManifestSha256']==sha(P/'manifest.json');assert {str(p.relative_to(P/'classes')):sha(p) for p in (P/'classes').rglob('*.class')}==cm['classHashes'];preflight=B/'evidence/PG23390-web-service-metric21-source-preflight-v1/manifest.json';pre=load(preflight);assert pre['actualExit']==pre['pmdApplicable']==pre['unclassified']==pre['checkstyle']==0 and pre['pmdRaw']==9 and pre['staticManifestSha256']==sha(S/'manifest.json') and pre['inputHashes']==b['inputHashes'];assert pre['normalMainStaticUnchanged']=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2'
# Independent literal-contract and selective-scope negatives mutate metadata/strings only.
def selected_ok(names):return len(names)==21 and len(set(names))==21 and set(names)==set(cfg['selectedMethods']) and not any(n.startswith('webservice009') for n in names)
assert selected_ok(cfg['selectedMethods']);assert not selected_ok(cfg['selectedMethods'][:-1]+[cfg['heldMethods'][0]['name']]);assert not selected_ok(cfg['selectedMethods']+ [cfg['heldMethods'][0]['name']]);tp=next(iter(cfg['testClasses']));text=(R/tp).read_text();required=['status_class=\\"2xx\\"} 1.0','assertSame(primary, assertThrows(AssertionError.class, () -> valve.log(null, null, 1)));','assertEquals(2, duplicate.entrySet().size());','assertNotSame(first, second);'];flat=' '.join(text.split());assert all(s in flat for s in required)
O.mkdir();files={}
for folder,pref in [(U,'original-'),(S,'static-')]:
 for p in [*folder.iterdir(),*sorted((folder/'xml').glob('TEST-*.xml'))]:
  if p.is_file():
   name='jacoco.exec' if p.name=='jacoco.exec' else pref+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=21,newUniqueTests=0,requalifiedExistingMethods=21,declaredOriginalMethods=22,notRunDeclaredMethods=cfg['heldMethods'],wholeOriginal22Accepted=False,coverage=counter,wholeTargetCodeCoverage100=True,currentDirectWholeSourceProof=1,registeredWholeComponentDelta=None,sourceFilePhysicalClosure=closure,physical=physical,classIds=ids,normalObservedCrc={n:crc64(normalBytes[n]) for n in observed},normalObservedCodeClasses=len(observed),normalProductInitializations=sorted(prodInit),normalProductInitCount=len(prodInit),generatedLambdaOwners={n:n.split('$$Lambda+',1)[0] for n in generated},staticRaw=9,staticApplicable=0,checkstyle=0,staticPreflight=dict(path=str(preflight.relative_to(R)),sha256=sha(preflight)),styleRemedy=pre['styleRemedy'],manualCoverageExclusions=[],standardCompilerFilters='None required for this normal ordinary class; all six Code methods retained.',oldExecCombined=False,fixtureMethodsExecuted=0,methodSelectionMetadataNegativeChecks=2,sourceOracleRecipes=required,emptyConfigHashes=b['emptyConfigHashes'],actualWrapperTimeoutSeconds=120,declaredToolUpperBoundSeconds=180,ownSdkJdkActivity=pre['requiredRuntimeConditions'],independentGcListenerCardinality=None,sdkCloseEvidence='Original TWR/finally assertions plus pinned vendor removeNotificationListener cleanup byte contract; listener cardinality is not independently measured.',actualTargetBackendRootVmNativeOperations=0,heldFourInitializations=0,environment=env,caseTimings=caseTimes,inputHashes=b['inputHashes'],files=files,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=21,notRunHeld=1,coverage=counter,normalObserved=len(observed),normalInit=len(prodInit),newUnique=0,registrationDelta=None,manifestSha256=sha(O/'manifest.json'))))
