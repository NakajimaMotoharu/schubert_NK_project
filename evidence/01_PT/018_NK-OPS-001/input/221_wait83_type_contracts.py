"""Source/owned AST metadata only; type contract is not a whole-Test liveness certificate."""
from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22502-test-wait85-source-inventory-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22568-wait83-type-contracts-v1';SLOT=R.parent/'pgpt-runs/PG379/pg22568-wait83-type-contracts-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def witness(path,text):
 p=R/path;s=p.read_text();assert text in s,(path,text);line=s[:s.index(text)].count('\n')+1;return dict(path=path,sha256=sha(p),line=line,text=text)
def main():
 assert not OUT.exists() and not SLOT.exists();pm=load(P/'manifest.json');assert sha(P/'manifest.json')=='ce3214560a0cbed2fba8779833356144c565bf6492c4a8463a80b61609be2cab';post=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22546-seven-future-independent-v1/manifest.json';assert sha(post)=='c83dc755afa467842001f033eb35c5e54fae55bdd42cacf85bbbadae5b093d72';qm=load(post);assert qm['actualExit']==0 and qm['finiteWaitAdditions']==8
 names=sorted(pm['inputHashes']);assert len(names)==85 and all(not any(x in n for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) for n in names);inputs={n:sha(R/n) for n in names};changed=[n for n in names if inputs[n]!=pm['inputHashes'][n]];cfg=load(R/'evidence/01_PT/015_NK-WEB-001/input/040_seven_security_port_future_requalification.json');assert set(changed)=={x['path'] for x in cfg['testClasses']};assert all(inputs[n]==qm['inputHashes'][n] for n in changed)
 assert sha(P/'sites.json')==pm['files']['sites.json'] and sha(P/'parse.stdout')==pm['files']['parse.stdout'];sites=[s for s in load(P/'sites.json') if s['kind']=='REF' or s['arity']==0];assert len(sites)==83;vars=[s.split('\t') for s in (P/'parse.stdout').read_text().splitlines() if s.startswith('VAR\t')];rows=[]
 api='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationSource.java';deferred='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/EncryptedSessionSecurityContextRepository.java';question='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/QuestionControllerTest.java'
 for s in sites:
  p=s['path'];name=Path(p).name;recv=s['receiver'];ev=[];kind='NON_FUTURE_TYPE_ONLY';typ=None;local=[v for v in vars if v[1]==p and v[4]==recv and v[2]==s['owner'] and v[3]==s['method']]
  if recv=='job' or recv=='EXPR' and name in ['EncryptedSecurityContextPortTest.java','EncryptedSessionCsrfPortTest.java']:
   typ='java.util.concurrent.Future';kind='FUTURE_FIXED_AND_WHOLE58_REQUALIFIED';ev=[witness(p,'java.util.concurrent.Future<'),dict(path=str(post.relative_to(R)),sha256=sha(post),finiteWaitAdditions=8,tests=58)]
  elif local:
   assert len(local)==1;v=local[0];line=(R/p).read_text().splitlines()[int(v[7])-1];ev=[witness(p,line.strip())];decl=v[5];hint=v[6]
   if hint.startswith('NEW:AtomicInteger') or decl=='AtomicInteger':typ='java.util.concurrent.atomic.AtomicInteger'
   elif decl.startswith('AtomicReference<'):typ='java.util.concurrent.atomic.AtomicReference'
   elif hint=='CALL:ThreadLocal.withInitial':typ='java.lang.ThreadLocal'
   elif decl=='Optional<String>':typ='java.util.Optional'
   elif hint=='CALL:source' and name=='ApiOutboxPublicationPortTest.java':
    typ='dev.codex.schubert.nk.api.monitoring.ApiOutboxObservationSource';ev +=[witness(p,'private static ApiOutboxObservationSource source(String mode)'),witness(api,'public final class ApiOutboxObservationSource implements Supplier<Optional<Snapshot>>'),witness(api,'public Optional<Snapshot> get()'),witness(api,'return current.get().observation;')]
   elif hint=='CALL:repository.loadDeferredContext' and name=='EncryptedSecurityContextPortTest.java':
    typ='org.springframework.security.core.context.DeferredSecurityContext';ev +=[witness(p,'import org.springframework.security.core.context.DeferredSecurityContext;') if 'import org.springframework.security.core.context.DeferredSecurityContext;' in (R/p).read_text() else witness(deferred,'import org.springframework.security.core.context.DeferredSecurityContext;'),witness(deferred,'public DeferredSecurityContext loadDeferredContext(HttpServletRequest request)'),witness(deferred,'private final class Deferred implements DeferredSecurityContext')];kind='DEFERRED_LOCKING_GET_NOT_FUTURE_LIVENESS_NOT_INFERRED'
  elif name=='MediaAuditContractTest.java' and recv=='logger.callCount':
   typ='java.util.concurrent.atomic.AtomicInteger';ev=[witness(p,'java.util.concurrent.atomic.AtomicInteger callCount'),witness(p,'new CapturingLogger()')]
  elif name=='WebSecurityAuditPortTest.java' and recv=='sink.attempts':
   typ='java.util.concurrent.atomic.AtomicInteger';ev=[witness(p,'AtomicInteger attempts = new AtomicInteger()'),witness(p,'new Sink()')]
  elif name=='ReceiptReferencePortTest.java' and recv in ['fixture.connectAttempts','constructor.connectAttempts']:
   typ='java.util.concurrent.atomic.AtomicInteger';ev=[witness(p,'AtomicInteger connectAttempts = new AtomicInteger()'),witness(p,'new Fixture()')]
  elif name=='QuestionControllerTest.java':
   if recv=='f.tokenIds':typ='java.util.concurrent.atomic.AtomicLong';ev=[witness(p,'final AtomicLong tokenIds = new AtomicLong()'),witness(p,'new Fixture()')]
   elif recv=='ownedConnections':typ='java.lang.ThreadLocal';ev=[witness(p,'final ThreadLocal<AtomicInteger> ownedConnections = ThreadLocal.withInitial(AtomicInteger::new)')]
   elif recv=='EXPR':typ='java.util.concurrent.atomic.AtomicInteger';ev=[witness(p,'ownedConnections.get().get()'),witness(p,'final ThreadLocal<AtomicInteger> ownedConnections = ThreadLocal.withInitial(AtomicInteger::new)')]
   elif recv=='f.security.f.live':
    typ='java.util.concurrent.atomic.AtomicInteger';base='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/';ev=[witness(p,'final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db)'),witness(base+'ApiSessionInvalidTest.java','final Fixture f;'),witness(base+'ApiSessionInvalidTest.java','import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;'),witness(base+'EncryptedWebSessionRepositoryTest.java','final AtomicInteger live = new AtomicInteger()')]
  if typ is None:kind='UNKNOWN';typ='UNKNOWN'
  # Resolve qualified Atomic/Optional names through explicit import or fully qualified declaration.
  if typ.startswith('java.util.') and typ!='java.util.concurrent.Future':
   text=(R/p).read_text();simple=typ.rsplit('.',1)[-1];assert 'import '+typ+';' in text or typ in text,(p,typ)
  rows.append(dict(site=s,type=typ,classification=kind,witnesses=ev,futureBlockingWait=kind=='FUTURE_FIXED_AND_WHOLE58_REQUALIFIED',nonblockingGuarantee=False,wholeTestAccepted=False,currentSourceSha256=inputs[p]))
 # javap reads public JDK/SDK signatures only, never initializes Product classes or compiles Tests.
 SLOT.mkdir();c.SLOT=SLOT;tc=R.parent/'toolchain';sdk=next(Path(p) for p in qm['dependencies'] if '/spring-security-core/' in p);stage=c.step('jdk-sdk-signatures',[str(tc/'jdk-25.0.4/bin/javap'),'-classpath',str(sdk),'java.util.concurrent.atomic.AtomicInteger','java.util.concurrent.atomic.AtomicLong','java.util.concurrent.atomic.AtomicReference','java.lang.ThreadLocal','java.util.Optional','java.util.function.Supplier','org.springframework.security.core.context.DeferredSecurityContext'],R);assert stage['actualExit']==0 and not stage['timedOut'];signatures=(SLOT/'jdk-sdk-signatures.stdout').read_text();assert 'DeferredSecurityContext extends java.util.function.Supplier<org.springframework.security.core.context.SecurityContext>' in signatures
 OUT.mkdir();write(OUT/'sites.json',rows);files={'sites.json':sha(OUT/'sites.json')}
 for n in ['jdk-sdk-signatures.stdout','jdk-sdk-signatures.stderr','jdk-sdk-signatures-exit.safe.json']:(OUT/n).write_bytes((SLOT/n).read_bytes());files[n]=sha(OUT/n)
 result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain=qm['productionCoreMain'],originalInventory=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),futureRequalification=dict(path=str(post.relative_to(R)),sha256=sha(post)),inputHashes=inputs,sourceWitnessHashes={w['path']:w['sha256'] for row in rows for w in row['witnesses']},candidateCount=83,classificationCounts=dict(collections.Counter(x['classification'] for x in rows)),receiverTypeCounts=dict(collections.Counter(x['type'] for x in rows)),unknownCount=sum(x['type']=='UNKNOWN' for x in rows),futureSites=8,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,ykt2177Closed=False,questionDynamicHold=True,signatures=stage,files=files,producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)));write(OUT/'manifest.json',result);print(json.dumps(dict(actualExit=0,counts=result['classificationCounts'],unknown=result['unknownCount'])))
if __name__=='__main__':main()
