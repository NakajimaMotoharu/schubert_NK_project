"""Admit the exact reused Main/whole11 and the two explicit null-equality negative sites."""
from pathlib import Path
import hashlib,json
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33844-authvalue13-prepare-v1/manifest.json';m=ld(pp);out=b/'evidence/PG33846-authvalue13-preflight-v1';assert not out.exists()
assert m['actualExit']==0 and m['expectedTests']==13 and m['newDefinitions']==2 and m['necessaryPriorDefinitions']==11 and m['MainCompilationRepeated'] is False and m['old11TestCompilationRepeated'] is False
assert all(sha(r/n)==h for n,h in m['inputHashes'].items()) and len(m['apiMainSources'])==5 and len(m['apiTestSources'])==2
for label,v in m['stages'].items():
 assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
 for stream in ['stdout','stderr']:assert sha(pp.parent/(label+'.'+stream))==v[stream+'Sha256']
assert m['processingErrors']==[] and m['checkstyleFindings']==0
oldp=r/m['exactMainStatic']['path'];old=ld(oldp);assert sha(oldp)==m['exactMainStatic']['sha256'] and old['actualExit']==0 and old['staticApplicable']==old['unclassified']==old['processingErrors']==old['checkstyle']==old['spotbugs']==0 and old['rootNullAwayFresh']
assert all(m['inputHashes'][n]==h for n,h in old['inputHashes'].items())
assert {(Path(v['path']).name,v['rule'],v['line']) for v in m['rawFindings']}=={('AuthContextValueContractTest.java','EqualsNull','36'),('AuthContextValueContractTest.java','EqualsNull','61')} and len(m['rawFindings'])==2
classified=[]
for v in m['rawFindings']:
 path=Path(v['path']);line=path.read_text().splitlines()[int(v['line'])-1];assert line.strip() in ['assertFalse(first.equals(null));','assertFalse(cipherA.equals(null));']
 classified.append(dict(**v,sourceLine=line,sourceSha256=sha(path),disposition='NOT_APPLICABLE_EXPLICIT_NEGATIVE_RECORD_NULL_CONTRACT',reason='The null operand is the independent negative input to the Java record value contract, and false is the literal expected value. This is not a production null-check idiom and cannot be replaced by receiver==null without ceasing to test equals. No suppression or private reflection.'))
work=r.parent/'pgpt-runs/PG379/pg33844-authvalue13-prepare-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert all(sha(Path(n))==h for n,h in m['dependencies'].items()) and len(m['physicalClassHashes'])==183
bridge8=ld(b/'evidence/PG33840-forecast-bridge-tool8-v1/manifest.json');guard=ld(b/'evidence/PG33842-bridge-writer-integration-v1/manifest.json');assert bridge8['actualExit']==guard['actualExit']==0 and bridge8['testDefinitions']==8 and guard['existingInputTests12Requalified'] and guard['noEventsOrStateMutated']
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),expectedTests=13,newDefinitions=2,necessaryPriorDefinitions=11,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayReusedExact5Main=True,rootNullAwayFresh=True,oldWhole11SourceAndClassExact=True,originalStatic24=ref(oldp),newRaw2=classified,staticRaw26Total=26,declaredTargets=[n[:-6] for n in m['mainClassHashes']],abstractFactoryAndPackageCode0Explicit=True,productionExpectedMethodUsed=False,onlyLiteralMapValuesBooleanFormatAndVectorOracles=True,tool8AndExisting12AndIndependent1SeparateFromApplication=True,tool8=ref(b/'evidence/PG33840-forecast-bridge-tool8-v1/manifest.json'),toolWriter=ref(b/'evidence/PG33842-bridge-writer-integration-v1/manifest.json'),manualExclusions=[],actualBackendOrHeldClassActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=13,newDefinitions=2,staticSites=26,applicable=0,unclassified=0,mainRebuilds=0)))
