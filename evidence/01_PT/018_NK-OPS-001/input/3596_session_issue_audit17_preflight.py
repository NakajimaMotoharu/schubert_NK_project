"""Bind all18 concrete static sites and prove the two old worker edits invert to unchanged oracles."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33974-session-issue-audit17-prepare-v1/manifest.json';sp=b/'evidence/PG33976-session-issue-audit17-static-v1/manifest.json';fp=b/'evidence/PG33971-session-issue-audit17-fixture-inverse-v1/manifest.json';m=ld(pp);st=ld(sp);fix=ld(fp);out=b/'evidence/PG33978-session-issue-audit17-preflight-v1';assert not out.exists()
assert m['actualExit']==st['actualExit']==fix['actualExit']==0 and m['expectedTests']==17 and m['MainSafeClosureRebuilt'] and len(m['apiMainSources'])==14 and len(m['apiTestSources'])==2
assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','-'];inverses=[]
for record in fix['records']:
 path=record['path'];text=(r/path).read_text();s=text.replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','')
 for change in reversed(record['changes']):assert s.count(change['new'])==1;s=s.replace(change['new'],change['old'])
 old=subprocess.check_output(['git','show',fix['sourceBefore']+':'+path]);assert hashlib.sha256(old).hexdigest()==record['oldSha256'];formatted=subprocess.run(formatter,input=s.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==old
 assert text.count('workers.shutdownNow();')==text.count('assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));')==1 and text.count('@Test')==record['oldDefinitions'];inverses.append(dict(path=path,restoredSha256=hashlib.sha256(formatted.stdout).hexdigest(),actualFormatterExit=0,originalBusinessAssertionsExact=True))
allowed={'AuthContextCodec.java':{'UseConcurrentHashMap':[82]},'ContextHash.java':{'AvoidSynchronizedStatement':[55]},'SessionAuditPortTest.java':{'CloseResource':[189],'DoNotUseThreads':[189,192,199,208,209],'UseConcurrentHashMap':[275],'UseProperClassLoader':[326]},'SessionIssueJdbcPortTest.java':{'UseProperClassLoader':[84],'UseConcurrentHashMap':[180],'NullAssignment':[405],'CloseResource':[525],'DoNotUseThreads':[525,531,547,548]}}
expected={(n,rule,str(line)) for n,rules in allowed.items() for rule,lines in rules.items() for line in lines};assert {(Path(v['path']).name,v['rule'],v['line']) for v in st['rawFindings']}==expected and len(st['rawFindings'])==len(expected)==18
classified=[]
for v in st['rawFindings']:
 path=Path(v['path']);text=path.read_text();line=text.splitlines()[int(v['line'])-1]
 if path.name=='AuthContextCodec.java':
  assert 'keys = Map.copyOf(copies);' in text and 'copies' not in text[text.index('  public EncryptedAuthContext encrypt'):]
  reason='Constructor-confined copies HashMap becomes final Map.copyOf; mutable key copies remain private and all encrypt/decrypt/close operations use private stateLock. No mutable map is shared, ConcurrentHashMap cannot enforce this key-array ownership contract.'
 elif path.name=='ContextHash.java':
  assert 'private final Object stateLock = new Object();' in text and 'synchronized (stateLock)' in text
  reason='Private unexposed lock is the existing atomic MessageDigest state/digest/format boundary. Removing synchronization would corrupt shared digest state; caller monitor is deliberately independent. Source unchanged from independently qualified Hash6.'
 elif v['rule']=='UseProperClassLoader':
  assert 'Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler)' in text
  reason='Standalone fake JDBC uses the explicitly supplied java.sql interface defining loader, with hardcoded Connection/PreparedStatement/ResultSet Class callers only. No arbitrary Class.forName/private reflection/context-loader/service/plugin backend resolution. This is a deterministic JDK dynamic proxy, not a container loader preference or fake forbidden production type.'
 elif v['rule']=='NullAssignment':
  assert line.strip()=='f.status = null;'
  reason='Deliberate SQL NULL result negative input, not a reset or normal null production value. The following original assertion demands fixed infrastructure failure before issuance and owned buffers/borrowed TX postconditions. Replacing null by empty would test a different persisted status contract.'
 elif v['rule']=='UseConcurrentHashMap':
  if path.name=='SessionAuditPortTest.java':assert 'private final Map<Integer, Object> bindings = new LinkedHashMap<>();' in text
  else:assert 'Map<Integer, Object> bound = new HashMap<>();' in text
  reason='Each fake statement/Fixture owns its own binding map, writes occur on its one invocation worker and the parent reads only after Future.get completion. The parallel test creates distinct fixtures and independent maps; stateless AUDIT_WRITER has no map field. No concurrently written shared map exists. Literal insertion/binding semantics are the independent SQL oracle.'
 else:
  assert 'workers.shutdownNow();' in text and 'assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));' in text and 'try (var workers' not in text
  reason='Standalone wholeJUnit owns one fixed two-worker pool per class. Existing all Future.get5 and new finally shutdownNow/assert await10/classTimeout30 bound both success and failure. Session crypto Fixture closes only inside its owning worker after issue returns/throws, never from an unconfirmed outer cleanup. J2EE thread restriction does not apply; failed worker termination is not a passing assertion.'
 classified.append(dict(**v,sourceLine=line,sourceSha256=sha(path),disposition='NOT_APPLICABLE_CONCRETE_PRIVATE_LOCK_OR_CONFINED_FIXTURE_OR_TYPED_NEGATIVE_INPUT',reason=reason))
work=r.parent/'pgpt-runs/PG379/pg33974-session-issue-audit17-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert len(m['physicalClassHashes'])==194 and len(m['mainClassHashes'])==18
assert {v.replace('.','/')+'.class' for v in st['spotbugs']['classStats']}==set(m['mainClassHashes'])
closure=b/'evidence/PG33970-session-issue-audit17-source-closure-v1/manifest.json';c=ld(closure);assert all(sha(Path(n))==h==m['dependencies'][n] for n,h in c['sdkHashes'].items()) and c['memoryProxyOnly'] and c['actualDbFixtureNotCopiedOrExtracted']
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=17,newDefinitions=0,necessaryPriorDefinitions=17,physicalClasses=194,sourceMain14=14,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayFresh=True,original17FunctionalAssertionsInverseExact=True,onlyTwoWorkerBoundsChanged=True,oldSourceInverse=ref(fp),independentFormatterInverses=inverses,pmdRaw18=18,classified=classified,declaredTargets=c['targets'],explicitSdkHashes=c['sdkHashes'],manualSuppressionAdded=False,liveDbSessionDriverOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=17,rawSites=18,applicable=0,unclassified=0,original17AssertionsInverseExact=True,physical=194)))
