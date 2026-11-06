"""Read-only source/XML/CRC/SDK binding for original supplied Servlet CSRF unit run."""
from pathlib import Path
import json,hashlib,subprocess,re,zipfile,datetime
import xml.etree.ElementTree as E

r=Path.cwd();runs=r.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
source='dc5fd1d71e286f3e575d62e50840911e5c64f587';core='4217e14083c6ecac116216e08d57f4361eb2f12d'
pub=Path('evidence/01_PT/016_NK-WEB-002/evidence/PG21534-notification-mvc-two-v1');m=load(pub/'manifest.json')
assert sha(pub/'manifest.json')=='7c46ea37522f8a1725a05c3107fa9c6f2d2bb600f087a51a54cc49cc0c66bf7f'
assert m['actualExit']==0 and m['source']==source and m['normalSource']==m['productionCoreMain']==core and m['tests']==m['newMethods']==2 and m['requalifiedExistingInvocations']==0
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
assert len(actual)==len(set(actual))==2 and sorted((c,n+'()') for c,n in actual)==sorted(map(tuple,m['selectedMethods']))
spec=Path('evidence/01_PT/016_NK-WEB-002/122_Notification_MVC参照Bean配線単体仕様.md').read_text();pairs=re.findall(r'\|(PT-SCR-NOTIFICATION-BEAN\d{3})\|(\w+)\|',spec)
assert len(pairs)==2 and {n for _,n in pairs}=={n for _,n in actual}
normal=load(runs/'pg20990-outbox-required-six-main-compile-v1/manifest.safe.json');assert normal['source']==core and normal['actualExit']==0
for n,h in normal['begin']['inputHashes'].items():assert sha(n)==h
for j in normal['jars'].values():assert sha(j['path'])==j['sha256']
with zipfile.ZipFile(normal['jars']['web']['path']) as z:
 for n,h in m['physicalHashes'].items():assert hashlib.sha256(z.read(n+'.class')).hexdigest()==h
coverage={c.get('name'):{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in c.findall('counter')} for c in E.parse(slot/'coverage.xml').getroot().findall('.//package/class')}
assert coverage==m['coverage'] and set(coverage)==set(m['physicalHashes']) and len(coverage)==1 and all(v['missed']==0 for cs in coverage.values() for v in cs.values())
four={k:sum(cs.get(k,{}).get('covered',0) for cs in coverage.values()) for k in ['LINE','METHOD','CLASS','BRANCH']};assert four==m['fourCounters']==dict(LINE=2,METHOD=2,CLASS=1,BRANCH=0)
ex=(slot/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "'+m['session']+'"' in ex
for n,crc in m['classIds'].items():assert re.search(r'^'+crc+r'\s+\d+ of\s+\d+\s+'+re.escape(n)+r'$',ex,re.M)
held=['dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'];assert all(not re.search(r'^\w+\s+[1-9]\d* of\s+\d+\s+'+re.escape(n)+r'$',ex,re.M) for n in held)
init=set(re.findall(r"Initializing '([^']+)",(slot/'class-init.log').read_text()));allowed={'dev/codex/schubert/nk/'+n for n in ['web/config/NotificationMvcConfiguration','web/controller/NotificationController','web/error/WebResultMapper','web/messaging/NotificationWireClient','web/messaging/ProtectedReadWireClient','web/messaging/JmsRequestReplyClient','web/messaging/ReplyCorrelationRegistry','web/security/ApiSessionInvalidHandler','web/session/SessionPayloadCodec','web/session/SessionAttributeCodec','web/session/EncryptedSessionPayload','web/session/EncryptedWebSessionRepository','web/session/JdbcWebSessionStore','web/session/SpringEncryptedSessionRepository','web/logging/WebSecurityAudit','web/logging/WebSecurityAudit$Event','web/logging/WebSecurityAudit$Route']}
prefixes=['dev/codex/schubert/nk/web/config/NotificationMvcBeanPortTest','dev/codex/schubert/nk/web/config/MvcBeanPortFixture','dev/codex/schubert/nk/web/session/SecurityContextOwnerPortFixture']
assert not {n for n in init if n.startswith('dev/codex/schubert/nk/') and n not in allowed and not any(n.startswith(v) for v in prefixes)}
assert not any(n.startswith(('dev/codex/schubert/nk/web/config/WebMvcConfiguration','dev/codex/schubert/nk/web/session/SpringWebSession','dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/bootstrap/','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','org/springframework/security/core/context/SecurityContextHolder','java/net/Socket','sun/nio/ch/SocketChannelImpl')) for n in init)
main=next(n for n in m['inputHashes'] if '/src/main/java/' in n);test=next(n for n in m['inputHashes'] if '/src/test/java/' in n)
assert 'WebCsrfToken.generate(' not in Path(main).read_text()+Path(test).read_text() and 'preserveFatal(' not in Path(main).read_text()+Path(test).read_text()
static=Path('evidence/01_PT/016_NK-WEB-002/evidence/PG21532-notification-mvc-static-v1/manifest.json');s=load(static);assert s['inputHashes']==m['inputHashes'] and s['pmdRaw']==1 and s['applicableViolations']==s['checkstyle']==s['processingErrors']==s['spotbugs']==0 and all(v['classification']=='NOT_APPLICABLE' and v['reason'] for v in s['individualClassifications'])
assert sha(s['staticManifest']['path'])==s['staticManifest']['sha256']
rawStatic=load(s['staticManifest']['path']);assert rawStatic['inputHashes']==m['inputHashes']
for v in rawStatic['reports'].values():assert sha(v['path'])==v['sha256']
sb=load(runs/'pg20992-outbox-required-six-static-reactor-v1/manifest.safe.json');assert sb['actualExit']==0 and sb['source']==core
sdk=load('evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json');cmd=raw['stages']['unit']['command'];console=cmd[cmd.index('-jar')+1]
assert sha(console)==sdk['consoleSha256']==raw['begin']['consoleSha256'] and sha(r.parent/'toolchain/jdk-25.0.4/lib/modules')==sdk['jdkModulesSha256'] and not any(v.startswith('jdbc:') for v in cmd) and '--scan-classpath' not in cmd
providers={}
for p in [Path(v) for v in raw['begin']['dependencies']]+[Path(console)]:
 assert sha(p)==(raw['begin']['consoleSha256'] if p==Path(console) else raw['begin']['dependencies'][str(p)])
 with zipfile.ZipFile(p) as z:providers[str(p)]=[n for n in z.namelist() if n=='META-INF/services/java.sql.Driver' or n.startswith(('org/postgresql/','org/apache/activemq/','com/microsoft/playwright/'))]
assert all(not v for v in providers.values())
seed=load(r.parent/'PMO/hourly-monitor/completion-execution-kit-20261102/evidence/remaining-work-seed.json');row=next(v for v in seed['sourceEvidenceRows'] if v['path']==main);assert row['evidenceStatus']=='NOT_IN_CURRENT_MEASUREMENT_REGISTRY' and row['owner']=='WBS-P016-21'
witness=Path('evidence/01_PT/016_NK-WEB-002/evidence/PG21538-notification-mvc-closed-method-witness-v1/manifest.json');w=load(witness);assert sha(witness)=='d8c02026cd7ed3b1a6f4c4ae2c7086d1840ccc58f29757ab96351533d833e625' and w['actualExit']==0 and w['source']==source and w['originalExecSha256']==sha(slot/'jacoco.exec') and len(w['executedMethods'])==15 and w['extraWholeSourceCredit']==w['productTestsReexecuted']==0
for n,h in w['files'].items():assert sha(witness.parent/n)==h
assert w['normalWebJar']==normal['jars']['web']
with zipfile.ZipFile(w['normalWebJar']['path']) as z:
 for name,h in w['physicalSha256'].items():assert hashlib.sha256(z.read(name+'.class')).hexdigest()==h
actualMethods={x.get('name'):[dict(name=y.get('name'),desc=y.get('desc')) for y in x.findall('method') if any(int(k.get('covered'))>0 for k in y.findall('counter'))] for x in E.parse(witness.parent/'methods.xml').getroot().findall('.//package/class')};assert actualMethods==w['executedMethods']
priorPath=Path(w['priorAdmittedClosure']['path']);prior=load(priorPath);assert sha(priorPath)==w['priorAdmittedClosure']['sha256']=='e2d6a399483d3f6a52ea0d5ca5262afa6a31c05896cf252cc9000da18da3cc73' and prior['actualExit']==0 and prior['normalJars']['web']==normal['jars']['web']
assert w['priorAdmittedClosure']['commonClassCount']==13
common=set(actualMethods)-set(w['newExactConstructors']);assert len(common)==13
for name in common:assert actualMethods[name]==prior['executedMethods'][name] and w['physicalSha256'][name]==prior['physicalSha256'][name]
newExact={'dev/codex/schubert/nk/web/controller/NotificationController':[dict(name='<init>',desc='(Ldev/codex/schubert/nk/web/messaging/NotificationWireClient;Ldev/codex/schubert/nk/web/security/ApiSessionInvalidHandler;)V')],'dev/codex/schubert/nk/web/messaging/NotificationWireClient':[dict(name='<init>',desc='(Ldev/codex/schubert/nk/web/messaging/JmsRequestReplyClient;Ldev/codex/schubert/nk/web/messaging/JmsRequestSender;Ljava/time/Clock;Ljava/util/function/Supplier;Ljava/time/Duration;)V')]};assert w['newExactConstructors']==newExact
for name,methods in newExact.items():assert actualMethods[name]==methods
helper='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/SecurityContextOwnerPortFixture.java';assert sha(helper)==m['inputHashes'][helper]==hashlib.sha256(subprocess.check_output(['git','show','fa8c9337018b933f6616bd99be57f009c94c947e:'+helper])).hexdigest()
out=Path('evidence/01_PT/016_NK-WEB-002/evidence/PG21542-notification-mvc-independent-post-v1');assert not out.exists();out.mkdir()
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=source,productionCoreMain=core,tests=2,newMethods=2,originalPost=dict(path=str(pub/'manifest.json'),sha256=sha(pub/'manifest.json')),sourceTestIds=pairs,fourCounters=four,missed=0,physical=1,staticPost=dict(path=str(static),sha256=sha(static)),environment=environment,initializedProduct=sorted(n for n in init if n.startswith('dev/codex/schubert/nk/')),fixedConsoleJdkReview=dict(path='evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json',sha256=sha('evidence/01_PT/015_NK-WEB-001/input/001_login_failure_sdk_static_review.json')),driverProviderEntries=providers,branchStatus="NATURAL_ZERO_BRANCH",branchRatio=None,dependencyWholeSourceCredit=0,dependencyMethodWitness=dict(path=str(witness),sha256=sha(witness)),productTestsReexecuted=0,actualSessionOrDbOrTokenGeneration=False,actualBrowserOrHttp=False,formalUpdated=False,newAcceptance=0,original282Member=True,effortRate=None,checkerSha256=sha(__file__),checkerSource=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=2,newMethods=2,manifestSha256=sha(out/'manifest.json'))))
