"""Independently qualify exact Main reuse, source inverses, finite fixture ownership, all static sites."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));norm=lambda s:'\n'.join(line.strip() for line in s.strip().splitlines())
pp=b/'evidence/PG33785-ssc420-encrypt27-fixed-prepare-v2/manifest.json';sp=b/'evidence/PG33787-ssc420-encrypt27-fixed-static-v2/manifest.json';m=ld(pp);st=ld(sp);out=b/'evidence/PG33788-ssc420-encrypt27-preflight-v1';assert not out.exists()
assert m['actualExit']==st['actualExit']==0 and m['expectedTests']==27 and m['rootCompileRepeated'] is False and m['mainSourceByteExact'] and m['bug3019AllOldAssertionsInverseExact']
assert m['inputHashes']==st['inputHashes'] and all(sha(r/n)==h for n,h in m['inputHashes'].items())
origin=r/m['reusedSameGroupFreshMainCompile']['path'];assert sha(origin)==m['reusedSameGroupFreshMainCompile']['sha256'];fresh=ld(origin);assert fresh['MainSafeClosureRebuilt'] and fresh['stages']['nullaway-compile']==m['stages']['nullaway-compile']
for obj,slot in [(m,pp.parent),(st,sp.parent)]:
 for label,v in obj['stages'].items():
  assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
  for stream in ['stdout','stderr']:assert sha(slot/(label+'.'+stream))==v[stream+'Sha256']
assert st['processingErrors']==[] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
base='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/'
for name,marker in [('revocation/RevocationPayloadCodecTest.java','  /** REVOKE-OWN001/SSC420:'),('logging/WebLogPayloadCodecTest.java','  /** WEBLOG-OWN001/SSC420:')]:
 path=base+name;old=subprocess.check_output(['git','show','d3f0aa6862d280c30f6e5025ebb2bb608594ec63:'+path],text=True);text=(r/path).read_text();prefix=text[:text.index(marker)]
 if name.startswith('logging'):
  fix=ld(b/'evidence/PG33786-ssc420-encrypt27-static-v1/BUG3019-original-site.json');a=prefix.index('    try {\n      EncryptedWebLogPayload encrypted');closing='    } finally {\n      codec.close();\n    }';z=prefix.index(closing,a)+len(closing);prefix=prefix[:a]+fix['oldSegment']+prefix[z:]
  pool=ld(b/'evidence/PG33787-ssc420-encrypt27-fixed-static-v1/BUG3019-pool-source-correction.json');assert pool['assertContentsChanged'] is False
  assert pool['newFirst'] in prefix;prefix=prefix.replace(pool['newFirst'],pool['oldFirst'],1)
  a=prefix.index('    WebLogPayloadCodec codec = new WebLogPayloadCodec("v2", CURRENT, "v1", PREVIOUS);',prefix.index('void concurrentProductionNonceGeneration'));z=prefix.index('\n  }',a);assert norm(prefix[a:z])==norm(pool['newSecond']);prefix=prefix[:a]+pool['oldSecond']+prefix[z:]
 assert prefix.rstrip()==old.rsplit('}',1)[0].rstrip(),name
allowed={
 'WebLogPayloadCodecTest.java':{'CloseResource':[50,321,497,498],'DoNotUseThreads':[50,53,68,69,321,328,337,338,498,506,514,515],'AvoidSynchronizedStatement':[52],'AvoidLiteralsInIfCondition':[491],'DoNotThrowExceptionInFinally':[513]},
 'RevocationPayloadCodecTest.java':{'CloseResource':[227,275,410,411],'DoNotUseThreads':[227,230,240,241,269,275,277,280,302,303,411,421,427,428],'DoNotThrowExceptionInFinally':[239,300,426]}}
expected={(name,rule,str(line)) for name,rules in allowed.items() for rule,lines in rules.items() for line in lines};actual={(Path(v['path']).name,v['rule'],v['line']) for v in st['rawFindings']};assert len(st['rawFindings'])==len(expected)==40 and actual==expected
classified=[]
for finding in st['rawFindings']:
 path=Path(finding['path']);line=path.read_text().splitlines()[int(finding['line'])-1]
 if finding['rule']=='AvoidSynchronizedStatement':reason='Intentional caller-monitor regression fixture holds the caller codec monitor while an independent worker uses only private ReentrantLock. Future5s and exact independent envelope prove that external monitor cannot control the codec; standalone Test only.'
 elif finding['rule']=='AvoidLiteralsInIfCondition':reason='Two-phase independent nonce fault fixture: literal1 selects first synthetic directError, second call runs on owned other worker. This is fixed test-case dispatch, not business or cryptographic policy.'
 elif finding['rule']=='DoNotThrowExceptionInFinally':reason='Unconfirmed owned-worker termination must fail Test and leave codec ownership unclaimed, rather than pass or call a potentially blocking close while worker owns lock. shutdownNow precedes await10, original boundedFuture/latches retained.'
 else:
  reason='Standalone wholeJUnit owns all pools/codecs. WebLog caller-monitor Future5s; old100jobs invokeAll10/Future10, each finally shutdownNow/assert await10 before codec.close. New other-worker Future5s then shutdownNow/await10 before close. Revocation original100 Futures20/two-worker bounded latch20 and finally release/shutdownNow/await10 before close. Codec resource sites are in explicit finally and close only after worker termination; false/interrupt remains failed/unconfirmed, never PASS. No managed application thread, real key, external service or process is created.'
 classified.append(dict(**finding,sourceLine=line,sourceSha256=sha(path),reason=reason,disposition='NOT_APPLICABLE_CONCRETE_STANDALONE_FINITE_FIXTURE_AFTER_BUG3019_CORRECTION'))
work=r.parent/'pgpt-runs/PG379/pg33785-ssc420-encrypt27-fixed-test-v2'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert len(m['physicalClassHashes'])==191 and len(m['mainClassHashes'])==15
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),static=ref(sp),expectedTests=27,newDefinitions=2,necessaryPriorDefinitions=25,physicalClasses=191,sourceMain13=13,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayFreshWithinSameGroup=True,mainCompilationRepeated=False,old25FunctionalAndLifetimeAssertionsInverseExact=True,onlyExplicitLifetimeControlGuardsChangedForBug3019=True,pmdRaw40=40,classified=classified,declaredTargetCodecs=['dev/codex/schubert/nk/web/logging/WebLogPayloadCodec','dev/codex/schubert/nk/web/revocation/RevocationPayloadCodec'],entireOwn15PhysicalNotInferredAccepted=True,manualSuppressionAdded=False,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=27,rawSites=40,applicable=0,unclassified=0,old25AssertionsInverseExact=True)))
