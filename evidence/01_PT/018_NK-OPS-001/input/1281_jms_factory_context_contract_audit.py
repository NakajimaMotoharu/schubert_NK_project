"""Public source/previous evidence correspondence only; no class materialization or product invocation."""
from pathlib import Path
import datetime,hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';P=R/'evidence/01_PT/005_NK-MSG-001';O=B/'evidence/PG26610-jms-factory-context-contract-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def historical(commit,path):return hashlib.sha256(subprocess.check_output(['git','show',commit+':'+path],cwd=R)).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
def module_of(name):
 parts=name.split('/')
 assert parts[:4]==['dev','codex','schubert','nk'] and parts[4] in ['api','protocol'],name
 return parts[4]
assert module_of('dev/codex/schubert/nk/api/messaging/X')=='api'
assert module_of('dev/codex/schubert/nk/protocol/header/X')=='protocol'
for invalid in ['dev/codex/schubert/nk/messaging/X','foreign/codex/schubert/nk/api/X']:
 try:module_of(invalid)
 except AssertionError:pass
 else:raise AssertionError(invalid)
assert not O.exists()
task=next(x for x in load(R/'documents/400_PGPT/470_PMO/481_PGPT詳細WBS.json')['tasks'] if x['id']=='WBS-P005-04')
assert len(task['ownedArtifacts'])==3
sources={p:sha(R/p) for p in task['ownedArtifacts']};assert all(p.endswith('.java') for p in sources)
a=P/'evidence/PG23074-jms-boundary-independent-v1/manifest.json';e=load(a);assert e['actualExit']==0 and e['tests']==8
s=P/'evidence/provisional/PG18612-reply-stage-unit-v1/manifest.json';t=load(s);assert t['actualExit']==0 and t['tests']==4
normal=load(B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')['normalPhysicalClassHashes']
rows=[]
for label,m,path,old in [('factory8',e,a,e['source']),('sender4',t,s,t['source'])]:
 inputs=e['inputHashes'] if label=='factory8' else {t['inputProvenance']['testInputPath']:t['inputProvenance']['testInputHash'],t['inputProvenance']['mainInputPath']:t['inputProvenance']['mainInputHash']}
 inputs={p:h for p,h in inputs.items() if p.startswith('src/')};assert len(inputs)==2
 for p,h in inputs.items():assert sha(R/p)==h
 observed=list(e['normalObservedCrc']) if label=='factory8' else [n.replace('.','/') for n in t['initializedProductClasses']]
 deps=[]
 for n in observed:
  module=module_of(n);p=f'src/schubert-nk-{module}/src/main/java/{n.split("$")[0]}.java';assert (R/p).exists(),p
  oldhash=historical(old,p);current=sha(R/p);deps.append(dict(path=p,historicalSha256=oldhash,currentSha256=current,unchanged=current==oldhash))
 for n,h in m['physical'].items():
  module=module_of(n);assert normal[module+':'+n+'.class']==h
 files=m['files'];assert isinstance(files,dict)
 verified=[]
 for n,h in files.items():
  p=path.parent/n
  if isinstance(h,str) and len(h)==64:
   assert p.is_file() and sha(p)==h,n;verified.append(n)
 rows.append(dict(label=label,originalEvidence=ref(path),originalSource=old,tests=m['tests'],testAndTargetSourceUnchanged=True,allNamedInitializedDependencySourcesUnchanged=all(x['unchanged'] for x in deps),dependencySourceComparison=deps,normalPhysicalTargetsUnchanged=True,verifiedPublicFileCount=len(verified),originalTargetCoverage=m.get('coverage',m.get('counters')),applicability='RETAIN_ORIGINAL_LIMITED_TARGET_PROOF_NOT_A_NEW_CURRENT_WHOLE_RUN',newProductExecutions=0,newTests=0))
assert all(x['allNamedInitializedDependencySourcesUnchanged'] for x in rows)
design=task['evidencePlan']['designFiles'][0];commit=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();designhash=historical(commit,design)
checks=[dict(id='P00504-PG01',result='REVIEWED',expectation='Loopback literal endpoint only; explicit 1..65535 port; no alternate transport/host/query/fallback.',source='ArtemisConnectionFactoryProvider.java'),dict(id='P00504-PG02',result='REVIEWED',expectation='SS321 SYNC/ASYNC/WEB_LOG windows1048576/0/65536; call2000, failure10000, ttl30000, initial3,reconnect-1,retry1000 multiplier2 cap30000; block durable/preAckfalse/topologyfalse.',source='ArtemisConnectionFactoryProvider.java'),dict(id='P00504-PG03',result='REVIEWED_RUNTIME_HELD',expectation='All dependencies validated before factory acquire; partially acquired factory closes once; close-failure identity/secondary policy and unknown owned resource registration require actual Temporary/ServiceProcessResources, not pure-runtime admission.',source='ArtemisConnectionFactoryProvider.java'),dict(id='P00504-PG04',result='REVIEWED_ORIGINAL8_RETAINED',expectation='Envelope header response kind/exact total length/1m cap before BytesMessage creation; literal wire, metadata order, every write/header failure identity, null/empty/reserved/internal/exact-cap fixtures already original8.',source='JmsMessageFactory.java'),dict(id='P00504-PG05',result='REVIEWED_ORIGINAL4_RETAINED',expectation='Borrowed transacted JMS context only; persistent2/TTL10000/FQQN and exact correlation, no commit/rollback/close owned by sender; independent manual wire and injected provider failure identity.',source='ReplySender.java'),dict(id='P00504-PG06',result='REVIEWED_ABSTRACT_NO_EXECUTABLE_CODE',expectation='TransactedJmsContextProvider is abstract open contract; no fake coverage assertion/test for abstract declaration.',source='TransactedJmsContextProvider.java')]
value=dict(actualExit=0,atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='236ffddc83a08f1ba8f2ac5c3932e381371acd59',workIds=['WBS-P005-04/1','WBS-P005-04/2'],ownedSourceHashes=sources,design=dict(path=design,commit=commit,sha256=designhash),publicSourceReviewChecks=checks,wholeSafeTestSourcesReviewed=['JmsReplyEnvelopeContractTest8','ReplySenderStageContractTest4'],wholeUnsafeTestRuntimeHeld=['ArtemisConnectionFactoryProviderTest4: direct actual TemporaryInfrastructureException and ServiceProcessResources plus actual ActiveMQConnectionFactory'],retainedEvidence=rows,completedOriginalPreparationWorkIds=['WBS-P005-04/1'],originalEndingWorkStatus={'WBS-P005-04/2':'NOT_ACCEPTED_FACTORY_RUNTIME_AND_C04_EXIT_DEPENDENCY_HELD'},productTestsExecuted=0,newDefinitions=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,actualFactoryBrokerVmDbKeyCredentialHeldClassIO=0,manualExclusions=[],oldExecCombined=False,next='Canonical P00601 Inbox public-source and test admissibility audit; keep direct held4/runtime/DB tests held, independent normal pure value checks only after whole-source closure.',verifier=ref(Path(__file__).resolve()))
O.mkdir();(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'),retainedOriginalTests=12,newProductExecutions=0,ownedSources=3,originalPreparationCompleted=1,newAcceptance=0)))
if __name__=='__main__':pass
