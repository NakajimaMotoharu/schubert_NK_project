"""Admit exact old6 Main/static and old2; classify the sole deliberate null-equality input site."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33915-actor-value4-prepare-v2/manifest.json';m=ld(pp);out=b/'evidence/PG33916-actor-value4-preflight-v1';assert not out.exists()
assert m['actualExit']==0 and m['expectedTests']==4 and m['newDefinitions']==2 and m['necessaryPriorDefinitions']==2 and not m['MainCompilationRepeated'] and not m['old2TestCompilationRepeated']
assert all(sha(r/n)==h for n,h in m['inputHashes'].items()) and len(m['apiMainSources'])==6 and len(m['apiTestSources'])==2
for label,v in m['stages'].items():
 assert type(v['actualExit']) is int and v['actualExit']==(4 if label=='pmd' else 0) and v['timedOut'] is False
 for stream in ['stdout','stderr']:assert sha(pp.parent/(label+'.'+stream))==v[stream+'Sha256']
assert m['processingErrors']==[] and m['checkstyleFindings']==0
oldp=r/m['exactMainStatic']['path'];old=ld(oldp);assert sha(oldp)==m['exactMainStatic']['sha256'] and old['actualExit']==0 and all(old[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs']) and old['apiUnchanged6Static']['classStats6Verified']
for n in m['apiMainSources']+[m['apiTestSources'][0]]:assert m['inputHashes'][n]==old['inputHashes'][n]
normalp=r/old['apiNormalCompile']['path'];normal=ld(normalp)
assert sha(normalp)==old['apiNormalCompile']['sha256'] and normal['actualExit']==0 and sha(r/'pom.xml')==normal['begin']['inputHashes']['pom.xml']
lineage=normal['nullAwayConfiguration'];lineageDepth=0
while isinstance(lineage,dict):
 assert set(lineage)=={'pomBytesUnchanged','reference'} and lineage['pomBytesUnchanged'] is True
 lineage=lineage['reference'];lineageDepth+=1
assert lineageDepth>0 and isinstance(lineage,str) and all(flag in lineage for flag in ['ErrorProne2.50.0','NullAway0.14.1','JSpecifyMode','no proc-none'])
policy.compiler_element()
for key in ['normalStatic','MainSourceStyle','testStyle']:
 pin=old['apiUnchanged6Static'][key];assert sha(r/pin['path'])==pin['sha256']
assert sha(r/'tools/quality/static/pmd.xml')==hashlib.sha256(subprocess.check_output(['git','show',policy.PMD_POLICY_SOURCE+':tools/quality/static/pmd.xml'])).hexdigest()
assert {(Path(v['path']).name,v['rule'],v['line']) for v in m['rawFindings']}=={('AuthenticatedActorValueContractTest.java','EqualsNull','55')} and len(m['rawFindings'])==1
v=m['rawFindings'][0];line=Path(v['path']).read_text().splitlines()[54];assert line.strip()=='assertFalse(first.equals(null));';classified=[dict(**v,sourceLine=line,sourceSha256=sha(Path(v['path'])),disposition='NOT_APPLICABLE_EXPLICIT_RECORD_NULL_NEGATIVE_INPUT',reason='The null operand is the literal negative input to record.equals and false is the independent expected contract. Replacing equals(null) by first==null would cease testing equality behavior. No suppression.')]
work=r.parent/'pgpt-runs/PG379/pg33915-actor-value4-prepare-v2'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert all(sha(Path(n))==h for n,h in m['dependencies'].items()) and len(m['physicalClassHashes'])==182
closure=b/'evidence/PG33910-actor-value-caller-boundary-v1/manifest.json';c=ld(closure);assert c['actualExit']==0 and c['directProductionConstructorSites3'] and c['directJdbcUsernameSites2'] and c['retainedCopyOfExistingActorSite1'] and not c['dbEffectiveRuntimeProven'] and all(sha(r/n)==h for n,h in c['sourceHashes'].items())
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),expectedTests=4,newDefinitions=2,necessaryPriorDefinitions=2,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayReusedExact6Main=True,rootNullAwayFresh=False,rootAndSixMainAndClassesExact=True,oldWhole2SourceAndClassExact=True,originalStatic=ref(oldp),newRaw1=classified,declaredTargets=['dev/codex/schubert/nk/api/security/AuthenticatedActor'],sourceBoundary=ref(closure),productionExpectedMethodUsed=False,onlyLiteralMapValuesAndExplicitByteArithmeticOracles=True,originalFixtureLiteralFinding1CorrectedWithoutMainRebuild=True,manualExclusions=[],actualBackendOrHeldClassActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=4,newDefinitions=2,staticSites=1,applicable=0,unclassified=0,mainRebuilds=0)))
