"""Admit all concrete new fixture sites and exact existing Main quality, no warning suppression."""
from pathlib import Path
import hashlib,json
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));pp=b/'evidence/PG34116-revocation-fatal4-prepare-v2/manifest.json';m=ld(pp);out=b/'evidence/PG34118-revocation-fatal4-preflight-v1';assert not out.exists();assert m['actualExit']==0 and m['expectedTests']==14 and m['newDefinitions']==4 and m['necessaryPriorDefinitions']==10 and not m['MainCompilationRepeated'];assert all(sha(r/p)==h for p,h in m['inputHashes'].items());assert all(sha(Path(p))==h for p,h in m['dependencies'].items())
for label,v in m['stages'].items():
 assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
 for stream in ['stdout','stderr']:assert sha(pp.parent/(label+'.'+stream))==v[stream+'Sha256']
assert m['processingErrors']==[] and m['checkstyleFindings']==0;expected={'RevokedContextValueContractTest.java':{'EqualsNull':[34]},'SessionRevocationJdbcPortTest.java':{'UseProperClassLoader':[90],'UseConcurrentHashMap':[96,113,179],'CloseResource':[482,758],'DoNotUseThreads':[758,764,789,790]}};wanted=sorted((n,k,str(x)) for n,v in expected.items() for k,lines in v.items() for x in lines);assert len(wanted)==11 and sorted((Path(x['path']).name,x['rule'],x['line']) for x in m['rawFindings'])==wanted;classified=[]
for x in m['rawFindings']:
 p=Path(x['path']);s=p.read_text();line=s.splitlines()[int(x['line'])-1];rule=x['rule']
 if rule=='EqualsNull':
  assert line.strip()=='assertFalse(value.equals(null));';reason='Explicit public record equals(null) negative contract; replacing by value==null would not test equals. Fixed false expectation, no normal null-comparison shortcut.'
 elif rule=='UseProperClassLoader':
  assert 'type.getClassLoader()' in s;reason='Hardcoded JDK JDBC interface proxies use defining loader in standalone JUnit, no private reflection/class-name discovery/backend or forbidden type substitute.'
 elif rule=='UseConcurrentHashMap':
  assert 'final Map<String, Throwable> injectedFailures = new HashMap<>();' in s;reason='Each worker/case owns a fresh Fixture fields/fault map and fresh statement bindings. New negative maps are configured before synchronous service call; parent reads only after bounded Future completion. Shared service never contains any map; concurrent mutable access absent.'
 elif rule=='CloseResource' and x['line']=='482':
  assert line.strip()=='var c = f.connection();';reason='Pure JDK proxy owns no backend/socket/handle. close/commit/rollback are explicit forbidden assertions proving borrowed TX nonownership; fake connection cannot require actual close.'
 else:
  assert rule in ['CloseResource','DoNotUseThreads'] and 'assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));' in s;reason='Standalone fixture pool has get5/finally shutdownNow/await10assert/classTimeout30, worker owns its resources. J2EE thread restriction does not apply and unsuccessful stop is not PASS.'
 classified.append(dict(**x,sourceLine=line,sourceSha256=sha(p),disposition='NOT_APPLICABLE_EXPLICIT_NEGATIVE_OR_CONFINED_FIXTURE',reason=reason))
ap=r/m['exactMainStatic']['path'];a=ld(ap);cp=r/m['exactMainCompile']['path'];c=ld(cp);assert sha(ap)==m['exactMainStatic']['sha256'] and sha(cp)==m['exactMainCompile']['sha256'] and a['actualExit']==c['actualExit']==0 and a['staticApplicable']==a['unclassified']==a['processingErrors']==0 and a['rootNullAwayFresh'];assert all(a['inputHashes'][p]==m['inputHashes'][p] for p in m['inputHashes'] if p not in m['apiTestSources']);assert c['dependencies']==m['dependencies'];policy.compiler_element();work=r.parent/'pgpt-runs/PG379/pg34116-revocation-fatal4-v2'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for n in m[key]:policy.relative_name(n)
 assert {n:sha(work/folder/n) for n in m[key]}==m[key]
proofp=b/'evidence/PG34114-revocation-fatal4-source-binding-v2/manifest.json';proof=ld(proofp);assert proof['actualExit']==0 and proof['old10InverseFormattedExact'] and proof['allMainAndPomsUnchanged'];v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),expectedTests=14,newDefinitions=4,necessaryPriorDefinitions=10,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugsApplicable=0,rootNullAwayFresh=False,rootNullAwayReusedExactCurrentMain=True,originalMainStatic=ref(ap),classified=classified,original10Inverse=ref(proofp),declaredTargets=['dev/codex/schubert/nk/api/security/AuthSessionRevocationService','dev/codex/schubert/nk/api/security/RevokedContext'],manualSuppressionAdded=False,actualBackendOrHeldActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False);out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=14,rawStatic=11,applicable=0,mainRebuilt=False,old10InverseExact=True)))
