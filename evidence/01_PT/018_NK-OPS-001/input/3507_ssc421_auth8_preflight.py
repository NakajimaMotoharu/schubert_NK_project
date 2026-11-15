"""Admit only complete source/Test closure and exactly eighteen current static sites."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));norm=lambda s:'\n'.join(v.strip() for v in s.strip().splitlines())
pp=b/'evidence/PG33804-ssc421-authctx8-prepare-v1/manifest.json';sp=b/'evidence/PG33806-ssc421-authctx8-static-v1/manifest.json';m=ld(pp);st=ld(sp);out=b/'evidence/PG33808-ssc421-authctx8-preflight-v1';assert not out.exists()
assert m['actualExit']==st['actualExit']==0 and m['expectedTests']==8 and m['MainSafeClosureRebuilt'] and len(m['apiMainSources'])==5 and len(m['apiTestSources'])==1
assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
proof=b/'evidence/PG33803-ssc421-auth-source-inverse-v1/test-lifetime-changes.json';fix=ld(proof);path=fix['path'];text=(r/path).read_text();prefix=text[:text.index(fix['newTestMarker'])];old=subprocess.check_output(['git','show',fix['sourceBefore']+':'+path],text=True)
markers=[('  @Test\n  void bug036CallerMonitor','\n  @Test'),('  @Test\n  void concurrentEncryption','\n  private static void assertReason')]
for change,(begin,end) in zip(fix['changes'],markers):
 a=prefix.index(begin);z=prefix.index(end,a+len(begin));assert norm(prefix[a:z])==norm(change['newBeforeFormat']);prefix=prefix[:a]+change['old']+prefix[z:]
prefix=prefix.replace('import static org.junit.jupiter.api.Assertions.assertTrue;\n','');assert prefix.rstrip()==old.rsplit('}',1)[0].rstrip()
allowed={'AuthContextCodec.java':{'UseConcurrentHashMap':[63]},'AuthContextCodecTest.java':{'CloseResource':[43,257,365],'DoNotUseThreads':[43,46,59,60,257,261,271,272,365,372,383,384],'AvoidSynchronizedStatement':[45],'AvoidLiteralsInIfCondition':[357]}}
expected={(name,rule,str(line)) for name,rules in allowed.items() for rule,lines in rules.items() for line in lines};actual={(Path(v['path']).name,v['rule'],v['line']) for v in st['rawFindings']};assert actual==expected and len(st['rawFindings'])==len(expected)==18
classified=[]
for finding in st['rawFindings']:
 path=Path(finding['path']);text=path.read_text();line=text.splitlines()[int(finding['line'])-1]
 if finding['rule']=='UseConcurrentHashMap':
  assert 'keys = Map.copyOf(copies);' in text and 'copies' not in text[text.index('  public EncryptedAuthContext encrypt'):]
  reason='Constructor-confined HashMap never escapes: all key/version validation precedes copying, final keys stores Map.copyOf and local copies is not retained. Mutable key arrays are private and every encrypt/decrypt/close is guarded by private stateLock. ConcurrentHashMap would not add safety or enforce that lock.'
 elif finding['rule']=='AvoidSynchronizedStatement':reason='Explicit caller-monitor regression test, deliberately holds the caller-visible monitor while another worker uses private ReentrantLock. Future5s and independent golden are required; this source construct is the test trigger, not production synchronization.'
 elif finding['rule']=='AvoidLiteralsInIfCondition':reason='Fixed two-phase AUTHCTX-OWN001 public nonce fault: first call throws exact synthetic Error, second other-worker call succeeds. Literal1 is test-case dispatch, no business/crypto policy.'
 else:
  assert 'executor.shutdownNow();' in text and text.count('assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));')==3
  reason='Standalone wholeJUnit owns virtual/single-worker pool. Caller monitor/new recovery Future5s and all100 original futures now get5s, unconditional shutdownNow/assert await10 before codec.close; false/interrupt fails without unconfirmed blocking close. All independent golden/count100/null/mutation assertions retained, no private key/service/process. This J2EE thread restriction does not apply to local Test workers and explicit finally owns all resource sites.'
 classified.append(dict(**finding,sourceLine=line,sourceSha256=sha(path),reason=reason,disposition='NOT_APPLICABLE_CONCRETE_CONSTRUCTOR_CONFINEMENT_OR_FINITE_STANDALONE_FIXTURE'))
work=r.parent/'pgpt-runs/PG379/pg33804-ssc421-authctx8-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert len(m['physicalClassHashes'])==182 and len(m['mainClassHashes'])==6
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=8,newDefinitions=1,necessaryPriorDefinitions=7,physicalClasses=182,sourceMain5=5,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayFresh=True,old7FunctionalAssertionsInverseExact=True,onlyFiniteWorkerBoundsChangedForBug3022=True,oldSourceInverse=ref(proof),pmdRaw18=18,classified=classified,declaredTargets=['dev/codex/schubert/nk/api/security/AuthContextCodec'],manualSuppressionAdded=False,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=8,rawSites=18,applicable=0,unclassified=0,old7AssertionsInverseExact=True)))
