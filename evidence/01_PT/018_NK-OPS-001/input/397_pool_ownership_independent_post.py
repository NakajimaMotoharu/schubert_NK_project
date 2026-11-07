"""Independent fixed-source API/Web memory-source ownership evidence, not real DB readiness."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as E,zipfile
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';U=RUNS/'pg23308-pool-ownership-port-unit-v1';PRE=RUNS/'pg23302-pool-ownership-port-compile-v1';S=RUNS/'pg23304-pool-ownership-port-static-v1';O=B/'evidence/PG23312-pool-ownership-independent-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
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
def recipe(text,maximum,minimum,module):
 t=' '.join(text.split());required=[f'POOL_NAME = "schubert-nk-{module}"',f'assertEquals({maximum}, pool.getMaximumPoolSize());',f'assertEquals({minimum}, pool.getMinimumIdle());','assertEquals(3_000L, pool.getConnectionTimeout());','assertEquals(2_000L, pool.getValidationTimeout());','assertEquals(1L, pool.getInitializationFailTimeout());','source.issued.get() > before','assertSame(source, pool.getDataSource());','assertEquals(0, source.sourceCloses.get()','assertEquals(1, source.sourceCloses.get()','failure.getCause() instanceof SQLTransientConnectionException','if (returnNull) return null;','assertEquals(0, malformed.issued.get());','assertEquals(0, malformed.closed.get());','thread.getName().startsWith(POOL_NAME)','TimeUnit.NANOSECONDS.timedJoin(worker, remaining);']
 return all(x in t for x in required) and 'new Thread' not in t and 'System.setProperty' not in t
assert not O.exists();cfg=load(B/'input/394_pool_ownership_scope.json');m=load(U/'manifest.json');b=m['begin'];assert load(U/'begin.json')==b and (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,2,0,0,0);assert b['source']=='657a03f4317e51d899344122a5c2ebd8bdf9f736' and b['normalSource']=='7aed8eace7c844c2f79f2e39db766faf914890d5';assert b['selected']==list(cfg['testClasses'].values())
for n,h in b['inputHashes'].items():assert sha(R/n)==h==hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+n],cwd=R)).hexdigest()
assert not subprocess.check_output(['git','diff','--name-only',b['normalSource'],b['source'],'--',':(glob)src/**/src/main/java/**/*.java'],cwd=R,text=True).strip()
for p,h in b['dependencies'].items():assert sha(p)==h
for label,stage in m['stages'].items():
 assert stage['actualExit']==0 and not stage['timedOut'] and stage==load(U/(label+'-exit.safe.json'))
 for stream in ['stdout','stderr']:assert sha(U/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==2 and '--scan-classpath' not in cmd and '--select-method' not in cmd and not any('--enable-native-access' in x for x in cmd)
expected=set();neg=0;observations=[]
for n,fqn in cfg['testClasses'].items():
 t=(R/n).read_text();module='api' if '/api/' in n else 'web';maximum,minimum=(8,2) if module=='api' else (2,1);assert recipe(t,maximum,minimum,module);methods=re.findall(r'void\s+(poolOwn\w+)\s*\(',t);assert len(methods)==1 and t.count('@Test')==1 and '@Timeout(45)' in t;expected.add((fqn,methods[0]+'()'))
 for old,new in [(f'assertEquals({maximum}, pool.getMaximumPoolSize());',f'assertEquals({maximum+1}, pool.getMaximumPoolSize());'),('source.issued.get() > before','source.issued.get() >= before'),('TimeUnit.NANOSECONDS.timedJoin(worker, remaining);','worker.join();')]:
  assert old in t and not recipe(t.replace(old,new,1),maximum,minimum,module);neg+=1
 observations.append(dict(caseClass=fqn,poolName='schubert-nk-'+module,successfulGenerations=2,nullResultConstructorFailures=1,failFastCallbackBeforeLoan=True,maximumPoolSize=maximum,minimumIdle=minimum,connectionTimeoutMillis=3000,validationTimeoutMillis=2000,initializationFailTimeoutMillis=1,autoCommit=True,readOnly=False,registerMbeans=False,callerSourceCloseWhilePoolOrFailedConstructor=0,callerFixtureSourceFinalCloses=2,allIssuedMemoryConnectionsClosed=True,absoluteIssuedConnectionCount=None,absoluteClosedConnectionCount=None,absoluteCountNote='Relational count equality was asserted at every terminal; absolute totals were not emitted, so retained as null.',sdkOwnedWorkersAliveAfterEachAttempt=0,noSqlOrDriverCallbacksAccepted=True,scope='VALUES_BOUND_BY_FIXED_SOURCE_ASSERTIONS_AND_TRUE_TERMINAL_XML_NOT_REALDB_OBSERVATION'))
cases=[];environment={};timings=[]
for p in (U/'xml').glob('TEST-*.xml'):
 root=E.parse(p).getroot();assert not any(root.findall('.//'+x) for x in ['failure','error','skipped']);cases += [(x.get('classname'),x.get('name')) for x in root.findall('testcase')];timings += [dict(className=x.get('classname'),seconds=x.get('time')) for x in root.findall('testcase')];environment.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']})
assert len(cases)==2 and set(cases)==expected;stdout=(U/'unit.stdout').read_text()
for t in ['2 tests found','2 tests started','2 tests successful','0 tests aborted','0 tests skipped','0 containers aborted']:assert t in stdout
# Diagnostics must not leak Hikari's generated connection UUIDs into ordinary public logs.
for stream in ['unit.stdout','unit.stderr']:assert not re.search(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',(U/stream).read_text(),re.I)
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)==b['normalManifestSha256'];nm=load(normal);normalBytes={};closure={};sourceFiles={'ApiJdbcPool.java','WebJdbcPool.java'}
for module in ['api','web']:
 jar=Path(nm['jars'][module]['path']);assert sha(jar)==nm['jars'][module]['sha256']
 with zipfile.ZipFile(jar) as z:
  for name in z.namelist():
   if name.endswith('.class'):
    n=name[:-6];assert n not in normalBytes;data=z.read(name);normalBytes[n]=data;meta=metadata(data)
    if meta['sourceFile'] in sourceFiles:closure[n]=meta
assert set(closure)==set(cfg['targetPhysical']) and len(closure)==2 and all(len([x for x in v['methods'] if x['code']])==2 for v in closure.values());physical={n:hashlib.sha256(normalBytes[n]).hexdigest() for n in closure};ids={n:crc64(normalBytes[n]) for n in closure};assert m['physical']==physical
for n,h in physical.items():assert sha(U/'component'/(n+'.class'))==h
info=(U/'classinfo.stdout').read_text();assert {n:i for i,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',info)}==ids;assert all(int(branches)==0 for _,branches,_,_,_,_ in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x[0-9a-f]{16} (\S+)',info,re.M))
ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG23308-POOL-SOURCE-OWNERSHIP"' in ex;probes={n:[i,int(hit),int(total)] for i,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',ex,re.M)};testPrefixes=[n.replace('.','/') for n in b['selected']];isTest=lambda n:any(n.startswith(p) for p in testPrefixes);observed={n for n in probes if n.startswith('dev/codex/schubert/nk/') and not isTest(n)};assert observed==set(closure)
for n in observed:assert probes[n][0]==crc64(normalBytes[n]) and probes[n][1]>0
initlog=(U/'class-init.log').read_text();allInit=set(re.findall(r"Initializing '([^']+)",initlog));prodInit={n for n in allInit if n.startswith('dev/codex/schubert/nk/') and not isTest(n)};assert prodInit==set(closure)
for held in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']:assert held not in initlog
sdkManifest=B/'evidence/PG23278-pool-sdk-static-v1/manifest.json';sdk=load(sdkManifest);allowed={n.replace('.','/') for n in sdk['classesDisassembled']};sdkInit={n for n in allInit if n.startswith('com/zaxxer/hikari/')};assert len(sdkInit)==36;generated={n for n in sdkInit if n not in allowed}
for n in generated:assert '$$Lambda+' in n and n.split('$$Lambda+',1)[0] in allowed
assert not any(x in n for n in sdkInit for x in ['DriverDataSource','JNDI','Javassist']);assert not any(n.startswith(('org/postgresql/','org/apache/activemq/','javax/naming/InitialContext')) for n in allInit)
root=E.parse(U/'coverage.xml').getroot();assert {n.get('name') for n in root.findall('.//class')}==set(closure);counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in root.findall('counter')};assert all(x['missed']==0 for x in counters.values());assert {k:counters[k]['covered'] for k in ['LINE','METHOD','CLASS']}==dict(LINE=28,METHOD=4,CLASS=2);assert 'BRANCH' not in counters
pm=load(PRE/'manifest.json');assert pm['actualExit']==0 and pm['inputHashes']==b['inputHashes'] and b['compileManifestSha256']==sha(PRE/'manifest.json');assert {str(p.relative_to(PRE/'classes')):sha(p) for p in (PRE/'classes').rglob('*.class')}==pm['classHashes'];sp=B/'evidence/PG23310-pool-ownership-source-preflight-v1/manifest.json';st=load(sp);assert st['actualExit']==st['pmdApplicable']==st['checkstyle']==st['unclassified']==0 and st['inputHashes']==b['inputHashes'] and st['staticManifestSha256']==sha(S/'manifest.json');assert st['normalMainStaticUnchanged']=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2';O.mkdir();files={}
for folder,pref in [(U,'original-'),(S,'static-')]:
 for p in [*folder.iterdir(),*sorted((folder/'xml').glob('TEST-*.xml'))]:
  if p.is_file():
   name='jacoco.exec' if p.name=='jacoco.exec' else pref+('class-init.stdout' if p.name=='class-init.log' else p.name);assert name not in files;shutil.copyfile(p,O/name);files[name]=sha(O/name)
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=b['source'],productionCoreMain=b['normalSource'],tests=2,newUniqueTests=2,observations=observations,successfulPoolGenerations=4,expectedNullResultConstructorFailures=2,coverage=counters,wholeTargetCodeCoverage100=True,branchStatus='NATURAL_ZERO_BRANCH',branchCounterPresent=False,branchRatio=None,sourceFilePhysicalClosure=closure,physical=physical,classIds=ids,sourcePhysicalCount=2,normalCodeClasses=2,abstractNoCode=0,normalProductInitializations=sorted(prodInit),normalObservedCrc={n:crc64(normalBytes[n]) for n in observed},sdkHikariInitializations=sorted(sdkInit),sdkHikariInitCount=36,sdkGeneratedLambdaOwners={n:n.split('$$Lambda+',1)[0] for n in generated},sourceRecipeNegativeChecks=neg,staticRaw=10,staticApplicable=0,checkstyle=0,staticPreflight=dict(path=str(sp.relative_to(R)),sha256=sha(sp)),newDirectWholeSourceProof=2,registeredWholeComponentDelta=None,registryDedupRequired=True,originalTestsCompiled=0,manualCoverageExclusions=[],standardCompilerFilters='None required for these two ordinary classes; all four normal Code methods retained.',oldExecCombined=False,actualDatabaseDriverSqlNetworkRoleAdmissionVmRootNativeOperations=0,heldFourInitializations=0,diagnosticUuidFoundInPublicOrdinaryLogs=0,absoluteCallbackCountsNotInvented=True,environment=environment,caseTimings=timings,inputHashes=b['inputHashes'],files=files,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=2,successfulPools=4,nullConstructorFailures=2,coverage=counters,branchStatus='NATURAL_ZERO_BRANCH',normalInit=2,sdkHikariInit=36,negative=neg,registrationDelta=None,manifestSha256=sha(O/'manifest.json'))))
