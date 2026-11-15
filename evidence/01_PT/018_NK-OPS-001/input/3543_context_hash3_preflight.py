"""Admit exactly12 static sites and reversible old-business assertions before whole3."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33862-context-hash3-prepare-v1/manifest.json';sp=b/'evidence/PG33864-context-hash3-static-v1/manifest.json';fp=b/'evidence/PG33858-context-hash3-fixture-inverse-v1/manifest.json';m=ld(pp);st=ld(sp);fix=ld(fp);out=b/'evidence/PG33866-context-hash3-preflight-v1';assert not out.exists()
assert m['actualExit']==st['actualExit']==fix['actualExit']==0 and m['expectedTests']==3 and m['MainSafeClosureRebuilt'] and len(m['apiMainSources'])==2 and len(m['apiTestSources'])==1
assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
path=fix['path'];text=(r/path).read_text();s=text.replace('import static org.junit.jupiter.api.Assertions.assertTrue;\n','').replace('import org.junit.jupiter.api.Timeout;\n','').replace('@Timeout(value = 20, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)\n','')
for change in reversed(fix['changes']):assert s.count(change['new'])==change['count'];s=s.replace(change['new'],change['old'])
old=subprocess.check_output(['git','show',fix['sourceBefore']+':'+path]);assert hashlib.sha256(old).hexdigest()==fix['oldSha256']
formatter=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','-'];formatted=subprocess.run(formatter,input=s.encode(),capture_output=True,timeout=30);assert formatted.returncode==0 and formatted.stdout==old
assert text.count('executor.shutdownNow();')==text.count('assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));')==2 and 'futures.get(i).get()' not in text
assert text[text.index('  @Test\n  void unavailableMandatoryDigest'):]==old.decode()[old.decode().index('  @Test\n  void unavailableMandatoryDigest'):]
allowed={'ContextHash.java':{'AvoidSynchronizedStatement':[24]},'ContextHashTest.java':{'CloseResource':[29,54],'DoNotUseThreads':[29,34,39,40,54,59,64,65],'AvoidSynchronizedStatement':[31]}}
expected={(n,rule,str(line)) for n,rules in allowed.items() for rule,lines in rules.items() for line in lines};assert {(Path(v['path']).name,v['rule'],v['line']) for v in st['rawFindings']}==expected and len(st['rawFindings'])==len(expected)==12
classified=[]
for v in st['rawFindings']:
 path=Path(v['path']);line=path.read_text().splitlines()[int(v['line'])-1]
 if path.name=='ContextHash.java':
  source=path.read_text();assert 'private final Object stateLock = new Object();' in source and 'synchronized (stateLock)' in source and 'synchronized (this)' not in source
  reason='The private final unexposed lock exclusively protects one mutable MessageDigest and its digest/reset state across calls. Caller monitor cannot control it; original MON worker regression checks that contract. The rule generic synchronization preference is not an applicable defect on this required atomic state boundary, and substituting a concurrent collection does not protect MessageDigest.'
 elif v['rule']=='AvoidSynchronizedStatement':reason='Explicit caller-visible monitor is only the negative regression input. Private lock must progress in separate worker within5s; removing the synchronized input would remove the regression. Whole Test owns and terminates pool independently.'
 else:reason='Standalone ordinary JUnit worker pool, not managed-container resource. Both creation/submit/shutdown/await sites are explicitly scoped finally with shutdownNow and assert await10; MON get5 and all100 get5 bound success/failure. No unbounded executor.close or worker survives a qualified terminal. Original assertions and independent golden/provider restoration inverse-exact.'
 classified.append(dict(**v,sourceLine=line,sourceSha256=sha(path),disposition='NOT_APPLICABLE_EXPLICIT_PRIVATE_STATE_LOCK_OR_FINITE_STANDALONE_FIXTURE',reason=reason))
work=r.parent/'pgpt-runs/PG379/pg33862-context-hash3-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert len(m['physicalClassHashes'])==178 and len(m['mainClassHashes'])==2
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=3,newDefinitions=0,necessaryPriorDefinitions=3,physicalClasses=178,sourceMain2=2,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayFresh=True,originalWhole3FunctionalAssertionsInverseExact=True,originalProviderUnavailableBodyExact=True,onlyFiniteWorkerBoundsChanged=True,oldSourceInverse=ref(fp),inverseFormatter=dict(command=formatter,actualExit=formatted.returncode,restoredSha256=hashlib.sha256(formatted.stdout).hexdigest()),pmdRaw12=12,classified=classified,declaredTargets=['dev/codex/schubert/nk/api/security/ContextHash'],manualSuppressionAdded=False,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=3,rawSites=12,applicable=0,unclassified=0,originalAssertionsInverseExact=True)))
