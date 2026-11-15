"""Require new whole6 source closure and classify each of the24 current static sites."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33885-ssc423-hash6-prepare-v2/manifest.json';sp=b/'evidence/PG33887-ssc423-hash6-static-v2/manifest.json';fp=b/'evidence/PG33883-ssc423-hash6-source-prefix-v1/manifest.json';m=ld(pp);st=ld(sp);fix=ld(fp);out=b/'evidence/PG33888-ssc423-hash6-preflight-v1';assert not out.exists()
assert m['actualExit']==st['actualExit']==fix['actualExit']==0 and m['expectedTests']==6 and m['MainSafeClosureRebuilt'] and len(m['apiMainSources'])==2 and len(m['apiTestSources'])==1
assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
path=fix['testPath'];text=(r/path).read_text();old=subprocess.check_output(['git','show','2ab247e59c2670be7f1bc8853252140eb3409deb:'+path],text=True);assert hashlib.sha256(old.encode()).hexdigest()==fix['oldWhole3Sha256'] and text[:text.index('  @Test\n  void hashOwn001')].rstrip()==old.rsplit('}',1)[0].rstrip()
assert text.count('executor.shutdownNow();')==text.count('assertTrue(executor.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));')==4 and text.count('@Test')==6 and 'futures.get(i).get()' not in text
allowed={'ContextHash.java':{'AvoidSynchronizedStatement':[55]},'ContextHashTest.java':{'CloseResource':[29,54,128,185],'DoNotUseThreads':[29,34,39,40,54,59,64,65,128,132,136,137,185,190,195,196],'AvoidSynchronizedStatement':[31,187],'AvoidDuplicateLiterals':[33]}}
expected={(n,rule,str(line)) for n,rules in allowed.items() for rule,lines in rules.items() for line in lines};assert {(Path(v['path']).name,v['rule'],v['line']) for v in st['rawFindings']}==expected and len(st['rawFindings'])==len(expected)==24
classified=[]
for v in st['rawFindings']:
 path=Path(v['path']);source=path.read_text();line=source.splitlines()[int(v['line'])-1]
 if path.name=='ContextHash.java':
  assert 'private final Object stateLock = new Object();' in source and 'synchronized (stateLock)' in source and 'synchronized (this)' not in source
  reason='Private final unexposed lock makes digest/reset+hex ownership atomic across concurrent calls. New operations retain this exact lock; independent caller-monitor and100-task vector regression verify its necessity. Rule preference against synchronization is not a defect on this required state boundary.'
 elif v['rule']=='AvoidDuplicateLiterals':
  assert 'ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb' in source
  reason='Repeated public independently calculated SHA256 literal is the self-contained oracle for original MON, original100 vectors and the two new fault/normal-boundary tests. It is never generated through production, and preserving old whole3 prefix prevents changing its original expected value. It is Test vector data rather than production policy duplication.'
 elif v['rule']=='AvoidSynchronizedStatement':reason='Deliberately hold the caller-visible object monitor as a regression input while another owned worker must progress through the private lock in5s. Removing this trigger removes the lifetime contract. Always release the monitor before finally shutdownNow/await10.'
 else:reason='Standalone wholeJUnit owns four syntactically scoped worker pools; all Futures get5, finally shutdownNow/assert await10, no Executor.close. Original100 andMON plus new Error/RTE recovery/fixedvector/private-monitor checks are ordinary noncontainer fixture threads, not application thread-pool lifecycle. Worker failure remains failure and independent source/run post verifies terminal.'
 classified.append(dict(**v,sourceLine=line,sourceSha256=sha(path),disposition='NOT_APPLICABLE_EXPLICIT_PRIVATE_STATE_LOCK_OR_LITERAL_ORACLE_OR_FINITE_STANDALONE_FIXTURE',reason=reason))
work=r.parent/'pgpt-runs/PG379/pg33885-ssc423-hash6-v2'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert len(m['physicalClassHashes'])==180 and len(m['mainClassHashes'])==4
main=(r/m['apiMainSources'][0]).read_text();assert 'this(new JdkOperations(MessageDigest.getInstance("SHA-256")));' in main and 'operations = Objects.requireNonNull(operations, "operations");' in main and 'return sha256.digest(raw);' in main and 'return HexFormat.of().formatHex(hashed);' in main and 'private final MessageDigest digest;' not in main
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=6,newDefinitions=3,necessaryPriorDefinitions=3,physicalClasses=180,sourceMain2=2,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayFresh=True,old3ExactPrefix=True,onlyTrustedPackageOperationsAndFixedPrivateJdkDefault=True,oldSourcePrefix=ref(fp),pmdRaw24=24,classified=classified,firstStatic25ApplicableFieldName1Retained=ref(b/'evidence/PG33886-ssc423-hash6-static-v1/manifest.json'),declaredTargets=['dev/codex/schubert/nk/api/security/ContextHash','dev/codex/schubert/nk/api/security/ContextHash$JdkOperations'],naturalAbstractFactoryAndPackageCode0=True,branchNatural0NotArtificial100=True,manualSuppressionAdded=False,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=6,rawSites=24,applicable=0,unclassified=0,old3PrefixExact=True)))
