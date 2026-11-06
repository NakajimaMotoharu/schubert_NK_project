"""Read-only source/XML/CRC/SDK binding for original supplied Servlet CSRF unit run."""
from pathlib import Path
import json,hashlib,subprocess,re,zipfile,datetime
import xml.etree.ElementTree as E

r=Path.cwd();runs=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
source='005cb84da4c67f5dbd92e62d309cd43226970abb';core='4217e14083c6ecac116216e08d57f4361eb2f12d'
pub=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21248-csrf-denied-eight-v1');m=load(pub/'manifest.json')
assert sha(pub/'manifest.json')=='620d2e1cb9943e8195e58bd475b46df9baeb62d8cb013eedfa0781fccaa1fe59'
assert m['actualExit']==0 and m['source']==source and m['normalSource']==m['productionCoreMain']==core and m['tests']==m['newMethods']==8 and m['requalifiedExistingInvocations']==0
assert m['manualCoverageExclusions']==[] and not m['oldExecUnion'] and all(m[k]==0 for k in ['failures','errors','skipped'])
for n,h in m['files'].items():assert '/' not in n and sha(pub/n)==h
for n,h in m['inputHashes'].items():
 assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+n])).hexdigest()==h
 if n==m['producerGitArtifact']['path']:
  v=m['verifierGitArtifact'];assert v['path']==n and sha(n)==v['sha256']==hashlib.sha256(subprocess.check_output(['git','show',v['source']+':'+n])).hexdigest()
 else:assert sha(n)==h
assert m['producerGitArtifact']['source']==source and m['driverSha256']==m['producerGitArtifact']['sha256']
slot=Path(m['originalManifest']['path']).parent;raw=load(slot/'manifest.json');assert sha(slot/'manifest.json')==m['originalManifest']['sha256'] and raw['begin']['source']==source and raw['begin']['inputHashes']==m['inputHashes'] and raw['actualExit']==0
for key,s in raw['stages'].items():assert s['actualExit']==0 and not s['timedOut'] and sha(slot/(key+'.stdout'))==s['stdoutSha256'] and sha(slot/(key+'.stderr'))==s['stderrSha256']
actual=[];environment=[]
for n,h in m['originalXmlPins'].items():
 assert sha(n)==h;tree=E.parse(n).getroot();assert all(int(tree.get(k,'0'))==0 for k in ['failures','errors','skipped'])
 for t in tree.findall('testcase'):
  assert not any(t.findall(k) for k in ['failure','error','skipped']);actual.append((t.get('classname'),t.get('name').removesuffix('()')))
 props={x.get('name'):x.get('value') for x in tree.findall('properties/property')};assert props['java.io.tmpdir']==str(slot/'tmp');environment.append({k:props.get(k) for k in ['os.name','os.arch','os.version','java.version','java.vendor']})
assert len(actual)==len(set(actual))==8 and sorted((c,n+'()') for c,n in actual)==sorted(map(tuple,m['selectedMethods']))
spec=Path('evidence/01_PT/015_NK-WEB-001/068_CSRF拒否403ローカル監査_自己所有thread単体仕様.md').read_text();pairs=re.findall(r'\|(PT-WEB-CSRF403\d{3})\|(\w+)\|',spec)
assert len(pairs)==8 and {n for _,n in pairs}=={n for _,n in actual}
normal=load(runs/'pg20990-outbox-required-six-main-compile-v1/manifest.safe.json');assert normal['source']==core and normal['actualExit']==0
for n,h in normal['begin']['inputHashes'].items():assert sha(n)==h
for j in normal['jars'].values():assert sha(j['path'])==j['sha256']
with zipfile.ZipFile(normal['jars']['web']['path']) as z:
 for n,h in m['physicalHashes'].items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==h
coverage={c.get('name'):{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')}
assert coverage==m['coverage'] and set(coverage)==set(m['physicalHashes']) and len(coverage)==1 and all(v['missed']==0 for cs in coverage.values() for v in cs.values())
four={k:sum(cs.get(k,{}).get('covered',0) for cs in coverage.values()) for k in ['LINE','METHOD','CLASS','BRANCH']};assert four==m['fourCounters']==dict(LINE=15,METHOD=2,CLASS=1,BRANCH=0)
ex=(slot/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+m['session']+'"' in ex
for n,crc in m['classIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(n)+r'$',ex,re.M)
held=['dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'];assert all(not re.search(r'^\w+\s+[1-9]\d* of\s+\d+\s+'+re.escape(n)+r'$',ex,re.M) for n in held)
init=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowed={'dev/codex/schubert/nk/'+n for n in ['protocol/header/AuthenticationContext','protocol/layout/semantic/UserRole','web/security/ClosedWebAuthentication','web/security/WebCsrfDeniedHandler','web/security/WebCsrfToken','web/security/WebDisplayContext','web/security/WebRequestContext','web/security/LoginClientAddress','web/session/SessionPrincipal','web/session/SessionStoreException','web/view/TopBarViewModel','web/logging/WebSecurityAudit','web/logging/WebSecurityAudit$Event','web/logging/WebSecurityAudit$Route']};limits={'dev/codex/schubert/nk/web/logging/WebSecurityAudit$$Lambda':3,'dev/codex/schubert/nk/web/session/SessionPrincipal$$Lambda':1,'dev/codex/schubert/nk/web/security/WebRequestContext$$Lambda':1}
for prefix,maximum in limits.items():assert sum(n.startswith(prefix) for n in init)<=maximum
assert not {n for n in init if n.startswith('dev/codex/schubert/nk/') and n not in allowed and not n.startswith('dev/codex/schubert/nk/web/security/CsrfDeniedHandlerPortTest') and not any(n.startswith(prefix) for prefix in limits)}
assert all(n not in init for n in held)
assert not any(n.startswith(('dev/codex/schubert/nk/web/session/SpringWebSession','dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','java/sql/DriverInfo','java/net/Socket','sun/nio/ch/SocketChannelImpl','org/springframework/security/core/context/GlobalSecurityContextHolderStrategy','org/springframework/security/core/context/InheritableThreadLocalSecurityContextHolderStrategy')) for n in init)
assert 'org/springframework/security/core/context/ThreadLocalSecurityContextHolderStrategy' in init and 'org/springframework/security/core/context/SecurityContextHolder' in init
main=next(n for n in m['inputHashes'] if '/src/main/java/' in n)
assert 'exception.' not in Path(main).read_text()
witnessPath=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21262-csrf-denied-dependency-method-witness-v1/manifest.json');w=load(witnessPath);assert sha(witnessPath)=='1fb581558affdbd63cd0b64dc24e71af4f43b3caddb9aed45028d069456b9ecc' and w['actualExit']==0 and w['source']==source and w['originalRun']=='PG21248' and w['originalExecSha256']==sha(slot/'jacoco.exec') and w['normalWebJarSha256']==normal['jars']['web']['sha256']
assert w['testsReexecuted']==w['additionalWholeSourceCredit']==0 and not w['dependencyCoverageAccepted']
for n,h in w['files'].items():assert sha(witnessPath.parent/n)==h
measured={}
for c in E.parse(witnessPath.parent/'dependency-methods.xml').getroot().findall('.//package/class'):
 name=c.get('name').rsplit('/',1)[1];measured[name]=[dict(name=method.get('name'),desc=method.get('desc')) for method in c.findall('method') if any(v.get('type')=='INSTRUCTION' and int(v.get('covered'))>0 for v in method.findall('counter'))]
expected={'WebCsrfToken':{'<init>','<clinit>','parse'},'WebDisplayContext':{'<init>','<clinit>','captureDenied','capture','existing','topBar','toString'},'WebRequestContext':{'<init>','<clinit>','requestId','clientAddress','require','existing','lambda$require$0'},'SessionStoreException':{'<init>'}}
assert measured==w['executedMethods'] and {k:{v['name'] for v in values} for k,values in measured.items()}==expected
assert [x['desc'] for x in measured['WebDisplayContext'] if x['name']=='capture']==['(Ljakarta/servlet/http/HttpServletRequest;Ldev/codex/schubert/nk/web/session/SessionPrincipal;)V']
with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
 for n,h in w['physicalHashes'].items():assert hashlib.sha256(jar.read(n+'.class')).hexdigest()==h
sdkPath=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21250-csrf-denied-threadlocal-sdk-static-v1/manifest.json');sc=load(sdkPath);assert sha(sdkPath)=='1cfa226682c383b1ce69718d19f38f1eab5a0f7d43376a08500de585ebb94a8b' and sc['actualExit']==0 and sc['decision']=='CHILD_JVM_EXPLICIT_THREADLOCAL_SYNTHETIC_CONTEXT_ONLY' and sc['selectedProperty']=='spring.security.strategy=MODE_THREADLOCAL' and not sc['hostOrServerSettingsChanged'] and not sc['actualUserAuthenticationRead']
for n,h in sc['files'].items():assert sha(sdkPath.parent/n)==h
assert sha(sc['sdkJar']['path'])==sc['sdkJar']['sha256']==raw['begin']['dependencies'][sc['sdkJar']['path']]
cmd=raw['stages']['unit']['command'];assert '-Dspring.security.strategy=MODE_THREADLOCAL' in cmd and sum(v.startswith('-Dspring.security.strategy=') for v in cmd)==1 and m['childSecurityStrategy']=='MODE_THREADLOCAL'
for n in m['originalXmlPins']:
 props={x.get('name'):x.get('value') for x in E.parse(n).getroot().findall('properties/property')};assert props['spring.security.strategy']=='MODE_THREADLOCAL'
assert m['branchStatus']=='NATURAL_ZERO_BRANCH' and m['branchRatio'] is None and all('BRANCH' not in cs for cs in coverage.values())
static=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21256-csrf-denied-final-static-v1/manifest.json');s=load(static);assert s['inputHashes']==m['inputHashes'] and s['pmdRaw']==5 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==s['spotbugs']==0 and all(not v['applicable'] and v['reason'] for v in s['classification'])
for n,h in s['files'].items():assert sha(static.parent/n)==h
sb=load(runs/'pg20992-outbox-required-six-static-reactor-v1/manifest.safe.json');assert sb['actualExit']==0 and sb['source']==core
sdk=load('evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json');cmd=raw['stages']['unit']['command'];console=cmd[cmd.index('-jar')+1]
assert sha(console)==sdk['consoleSha256']==raw['begin']['consoleSha256'] and sha(r.parent/'toolchain/jdk-25.0.4/lib/modules')==sdk['jdkModulesSha256'] and not any(v.startswith('jdbc:') for v in cmd) and '--scan-classpath' not in cmd
providers={}
for p in [Path(v) for v in raw['begin']['dependencies']]+[Path(console)]:
 assert sha(p)==(raw['begin']['consoleSha256'] if p==Path(console) else raw['begin']['dependencies'][str(p)])
 with zipfile.ZipFile(p) as z:providers[str(p)]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver' or n.startswith(('org/postgresql/','org/apache/activemq/','com/microsoft/playwright/'))]
assert all(not v for v in providers.values())
seed=load(r.parent/'PMO/hourly-monitor/completion-execution-kit-20261102/evidence/remaining-work-seed.json');row=next(v for v in seed['sourceEvidenceRows'] if v['path']==main);assert row['evidenceStatus']=='NOT_IN_CURRENT_MEASUREMENT_REGISTRY' and row['owner']=='WBS-P015-02'
out=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG21264-csrf-denied-independent-post-v1');assert not out.exists();out.mkdir()
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=core,tests=8,newMethods=8,originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),sourceTestIds=pairs,fourCounters=four,missed=0,physical=1,staticPost=dict(path=str(static),sha256=sha(static)),environment=environment,initializedProduct=sorted(n for n in init if n.startswith('dev/codex/schubert/nk/')),fixedConsoleJdkReview=dict(path='evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json',sha256=sha('evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json')),driverProviderEntries=providers,productTestsReexecuted=0,branchStatus="NATURAL_ZERO_BRANCH",branchRatio=None,childStrategy="MODE_THREADLOCAL",sdkThreadLocalReview=dict(path=str(sdkPath),sha256=sha(sdkPath)),dependencyMethodWitness=dict(path=str(witnessPath),sha256=sha(witnessPath)),actualSessionOrDbOrTokenGeneration=False,actualBrowserOrHttp=False,formalUpdated=False,newAcceptance=0,original282Member=True,effortRate=None,checkerSha256=sha(__file__),checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=8,newMethods=8,manifestSha256=sha(out/'manifest.json'))))
