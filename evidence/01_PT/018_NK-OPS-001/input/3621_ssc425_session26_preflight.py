"""Concrete source/exception-path adjudication, no static suppression or backend execution."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34032-ssc425-session26-prepare-v1/manifest.json';sp=b/'evidence/PG34034-ssc425-session26-static-v1/manifest.json';m=ld(pp);st=ld(sp);out=b/'evidence/PG34036-ssc425-session26-preflight-v1';assert not out.exists();assert m['actualExit']==st['actualExit']==0 and m['expectedTests']==26 and len(m['apiMainSources'])==15 and len(m['apiTestSources'])==3 and m['MainSafeClosureRebuilt'];assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==({'pmd':4,'spotbugs':1}.get(label,0)) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and st['spotbugs']['bugs']==1 and st['spotbugs']['missing']==st['spotbugs']['errors']==0
expected={'JdbcResourceCleanup.java':{'AvoidCatchingGenericException':[30,30,42,42,54,54]},'AuthContextCodec.java':{'UseConcurrentHashMap':[82]},'AuthSessionService.java':{'CloseResource':[85,89,119,145,150,168],'AvoidCatchingGenericException':[95,95,101,101,135,135,155,155,161,161,176,176]},'ContextHash.java':{'AvoidSynchronizedStatement':[55]},'SessionAuditWriter.java':{'CloseResource':[41],'AvoidCatchingGenericException':[59,59]},'JdbcResourceCleanupTest.java':{'UseProperClassLoader':[124],'CompareObjectsWithEquals':[137]},'SessionAuditPortTest.java':{'CloseResource':[189],'DoNotUseThreads':[189,192,199,208,209],'UseConcurrentHashMap':[275],'UseProperClassLoader':[326]},'SessionIssueJdbcPortTest.java':{'UseProperClassLoader':[84],'UseConcurrentHashMap':[183],'NullAssignment':[409],'CloseResource':[529],'DoNotUseThreads':[529,535,551,552]}}
wanted=sorted((n,k,str(x)) for n,v in expected.items() for k,lines in v.items() for x in lines);assert sorted((Path(v['path']).name,v['rule'],v['line']) for v in st['rawFindings'])==wanted and len(wanted)==47
classified=[]
for v in st['rawFindings']:
 p=Path(v['path']);s=p.read_text();rule=v['rule'];name=p.name;line=s.splitlines()[int(v['line'])-1]
 if rule=='AvoidCatchingGenericException':
  assert 'SQLException | RuntimeException | Error failure' in line
  reason='Explicit owned-resource finally reproduces the full Java TWR primary graph; caught SQL/runtime/fatal are immediately rethrown unchanged by body or suppressed on identical original primary by cleanup. No generic Exception catch or normal-result conversion. Separate direct Error/RTE/alias oracle cases exercise the exact contract.'
 elif rule=='CloseResource' and name in ['AuthSessionService.java','SessionAuditWriter.java']:
  assert 'JdbcResourceCleanup.closeStatement(' in s
  reason='Every nonnull owned local is covered by explicit try/catch/finally and typed closeStatement/closeRows with declared WillClose; borrowed Connection never closed. Null returns create no resource. Independent old17 plus new resource-null2 and adapter2 assert actual close counts, buffer wipe and transaction nonownership. PMD only recognizes lexical TWR, not this helper contract.'
 elif name=='AuthContextCodec.java':
  assert 'keys = Map.copyOf(copies);' in s
  reason='Constructor-confined copied HashMap becomes immutable Map.copyOf; no map mutation shared between workers, private stateLock protects key-array ownership. Existing source unchanged.'
 elif name=='ContextHash.java':
  assert 'synchronized (stateLock)' in s and 'private final Object stateLock' in s
  reason='Private unexposed lock is required for atomic shared MessageDigest operations and prevents caller-monitor interference. Existing same source qualified Hash6, no map/thread architecture change.'
 elif rule=='UseProperClassLoader':
  assert 'type.getClassLoader()' in s
  reason='JDK JDBC proxy uses only hardcoded java.sql Statement/ResultSet/Connection interfaces and their defining loader. No dynamic class-name discovery, private reflection, backend loading or forbidden production type substitute.'
 elif rule=='CompareObjectsWithEquals':
  assert 'primary == failure' in line
  reason='Intentional Throwable identity comparison detects precisely JDK forbidden self-suppression; equality would change the required identity contract. Alias test asserts the original cause and zero suppressed entries.'
 elif rule=='NullAssignment':
  assert line.strip()=='f.status = null;'
  reason='Deliberate persisted SQL NULL negative fixture, required fixed infrastructure failure and cleanup. Empty string would change the tested database invariant.'
 elif rule=='UseConcurrentHashMap':
  assert name in ['SessionAuditPortTest.java','SessionIssueJdbcPortTest.java']
  reason='Each individual fake statement owns its binding map on a single invocation worker. Distinct parallel fixtures own distinct maps; parent reads after bounded Future completion. No shared concurrently mutated map.'
 else:
  assert name in ['SessionAuditPortTest.java','SessionIssueJdbcPortTest.java'] and rule in ['CloseResource','DoNotUseThreads'];assert 'workers.shutdownNow();' in s and 'assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));' in s
  reason='Standalone unit fixture, not a J2EE container. Owned worker pool has Future.get5, finally shutdownNow/await10 asserted and classTimeout30. Resource codecs close inside their owning worker. Failure to stop cannot pass.'
 classified.append(dict(**v,sourceLine=line,sourceSha256=sha(p),disposition='NOT_APPLICABLE_WITH_CONCRETE_SOURCE_CONTRACT',reason=reason))
sb=ET.parse(sp.parent/'spotbugs.xml').findall('.//BugInstance');assert len(sb)==1;bug=sb[0];assert bug.get('type')=='OBL_UNSATISFIED_OBLIGATION_EXCEPTION_EDGE' and bug.find('Method').get('name')=='write';assert bug.find('SourceLine').get('start')=='43'
required=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/RequiredColumn.java';text=required.read_text();assert 'if (value == null)' in text and 'throw new SQLDataException' in text and 'return value;' in text
parent=r/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/SessionAuditWriter.java';s=parent.read_text();assert s.index('requireValue(')<s.index('@Nullable Throwable primary')<s.index('    try {')<s.index('    } finally {')<s.index('JdbcResourceCleanup.closeStatement(primary, statement);')
sbproof=dict(type=bug.get('type'),sourceLine=43,requiredGuard=ref(required),parent=ref(parent),disposition='FALSE_POSITIVE_CHECKED_EXCEPTION_EDGE_IN_NONNULL_GUARD',reason='Only checked throw between successful prepareStatement and protected body is requireValue SQLDataException. Exact helper can throw only if value is null, in which case no Statement exists; every nonnull value returns identically without checked throw and reaches finally typed WillClose. Catch-all checked edge treats guard as arbitrary throwing callee. No acquired resource exists on actual throwing guard path. Do not suppress XML; new resource-null test verifies AUDIT null path and old17 verify failures/close. Runtime/Error close graph separately tested.',actualLeakDemonstrated=False,rawWarningRetained=True)
work=r.parent/'pgpt-runs/PG379/pg34032-ssc425-session26-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
assert len(m['physicalClassHashes'])==196 and len(m['mainClassHashes'])==20 and {v.replace('.','/')+'.class' for v in st['spotbugs']['classStats']}==set(m['mainClassHashes'])
c=ld(b/'evidence/PG34030-ssc425-source-binding-v1/manifest.json');v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=26,newDefinitions=9,necessaryPriorDefinitions=17,physicalClasses=196,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,spotbugsRaw=1,spotbugsConcreteAdjudication=sbproof,rootNullAwayFresh=True,original17FunctionalAssertionsInverseExact=True,pmdRaw47=47,classified=classified,declaredTargets=c['targets'],manualSuppressionAdded=False,liveDbSessionDriverOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=26,pmdRaw=47,spotbugsRaw=1,applicable=0,unclassified=0,physical=196)))
