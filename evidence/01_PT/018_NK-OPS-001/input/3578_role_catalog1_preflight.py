"""Admit the explicit minimal Role universe, no metadata default or new provider/backend."""
from pathlib import Path
import hashlib,json,subprocess
import pgpt_closed_host_profile as policy
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG33934-role-catalog1-prepare-v1/manifest.json';m=ld(pp);out=b/'evidence/PG33936-role-catalog1-preflight-v1';assert not out.exists()
assert m['actualExit']==0 and m['expectedTests']==m['newDefinitions']==1 and m['necessaryPriorDefinitions']==0 and not m['MainCompilationRepeated'] and not m['protocolOrOtherApiOrSdkPayloadNeeded']
assert all(sha(r/n)==h for n,h in m['inputHashes'].items()) and len(m['apiMainSources'])==2 and len(m['apiTestSources'])==1
for label,v in m['stages'].items():
 assert type(v['actualExit']) is int and v['actualExit']==0 and v['timedOut'] is False
 for stream in ['stdout','stderr']:assert sha(pp.parent/(label+'.'+stream))==v[stream+'Sha256']
assert m['processingErrors']==m['rawFindings']==[] and m['checkstyleFindings']==0
oldp=r/m['exactMainStatic']['path'];old=ld(oldp);assert sha(oldp)==m['exactMainStatic']['sha256'] and old['actualExit']==0 and all(old[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs']) and old['apiUnchanged6Static']['classStats6Verified']
assert all(m['inputHashes'][n]==old['inputHashes'][n] for n in m['apiMainSources'])
normalp=r/old['apiNormalCompile']['path'];normal=ld(normalp);assert sha(normalp)==old['apiNormalCompile']['sha256'] and normal['actualExit']==0 and sha(r/'pom.xml')==normal['begin']['inputHashes']['pom.xml'];policy.compiler_element()
lineage=normal['nullAwayConfiguration']
while isinstance(lineage,dict):
 assert set(lineage)=={'pomBytesUnchanged','reference'} and lineage['pomBytesUnchanged'] is True;lineage=lineage['reference']
assert isinstance(lineage,str) and all(x in lineage for x in ['ErrorProne2.50.0','NullAway0.14.1','JSpecifyMode','no proc-none'])
for key in ['normalStatic','MainSourceStyle']:
 pin=old['apiUnchanged6Static'][key];assert sha(r/pin['path'])==pin['sha256']
assert sha(r/'tools/quality/static/pmd.xml')==hashlib.sha256(subprocess.check_output(['git','show',policy.PMD_POLICY_SOURCE+':tools/quality/static/pmd.xml'])).hexdigest()
work=r.parent/'pgpt-runs/PG379/pg33934-role-catalog1-prepare-v1'
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:
 for name in m[key]:policy.relative_name(name)
 assert {name:sha(work/folder/name) for name in m[key]}==m[key]
assert all(sha(Path(n))==h for n,h in m['dependencies'].items()) and len(m['physicalClassHashes'])==2 and set(m['physicalClassHashes'])=={'dev/codex/schubert/nk/api/domain/Role.class','dev/codex/schubert/nk/api/domain/package-info.class'}
v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(pp),expectedTests=1,newDefinitions=1,necessaryPriorDefinitions=0,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,rootNullAwayReusedExactRole=True,rootNullAwayFresh=False,originalStatic=ref(oldp),newRaw0=True,declaredTargets=['dev/codex/schubert/nk/api/domain/Role'],naturalBranch0AndPackageCode0Explicit=True,owner='WBS-P018-05',productionExpectedMethodUsed=False,onlyLiteralVocabularyOrderIdentityAndUnknownInputOracles=True,manualExclusions=[],actualBackendOrHeldClassActions=0,applicationTestsExecuted=0,newAcceptance=0,whole451Accepted=False)
out.mkdir();(out/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,wholeTests=1,newDefinitions=1,staticApplicable=0,unclassified=0,physical=2,mainRebuilds=0)))
