"""Controlled single-exec Request proof replacement; new18, repeat16, no coverage union."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG14732-current842-incremental-registry-v1','aa96fcee286c5ca767581006cf4ed5803d3a9f72e0b9b2d961e79fabd235f096')
PREV_POST=('PG14734-current842-incremental-registry-post-v1','8c924252413a7767c6a2bc938e263cb1dc8cb8f43154e09c9e1fc414405edc02')
JOINT=('PG14744-user-log-sql-joint-thirty-four-post-v1','4f4d6559dcc2ab58451504be29405129c71407d79d117274d3d23616c42093f7')
JOINT_POST=('PG14747-user-log-sql-joint-independent-v2','a015245cc2b21dc7cf457cc26726e80384d9efb9806f5f547c6b9be3e88ffd22')
REPLACED={'dev/codex/schubert/nk/api/application/admin/UserQueryRequest','dev/codex/schubert/nk/api/application/log/LogRequest'}
OUT=data.BASE/'PG14750-current860-joint-registry-v1'

def require(ok,message):
    if not ok:raise ValueError(message)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only controlled registry')
    old,prior,p,proof=[read(v) for v in [PREV,PREV_POST,JOINT,JOINT_POST]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,proof]),'all same source genuine independent references')
    require(prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==22 and all(json.dumps(v,sort_keys=True)==json.dumps(old[k],sort_keys=True) for k,v in prior['summary'].items()),'old842 independent typed summary')
    require(proof['postSha256']==JOINT[1] and proof['originalXmlMethods']==34 and proof['newUniqueMethods']==18 and proof['necessaryRepeatedMethods']==16 and proof['semanticNegativeVectors']==18 and proof['rawInvocationRoleNegativeVectors']==4 and p['forbiddenProductProbeHits']==proof['forbiddenProductProbeHits']==0,'genuine34/new18/repeat16 and probe0')
    require(p['normalManifestSha256']==old['normalManifestSha256'] and p['singleSession'] is True and p['crcMismatch']==0 and p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False,'one current exec, not old coverage')
    result=copy.deepcopy(old);cases={(v['classname'],v['name']) for v in old['cases']};local={(v['classname'],v['name']) for v in p['cases']}
    require(len(local)==34 and len(local-cases)==18 and len(local&cases)==16,'count only genuine new methods')
    require(local-cases=={(v['classname'],v['name']) for v in proof['newCases']} and local&cases=={(v['classname'],v['name']) for v in proof['repeatedCases']},'exact independently identified repeated original identities')
    units=result['fullSourceUnits'];history={n:copy.deepcopy(units[n]) for n in REPLACED}
    require(set(units)&set(p['fullSourceUnits'])==REPLACED,'only declared Request proofs may be replaced')
    for name,u in p['fullSourceUnits'].items():
        four=all(v['covered']>0 and v['missed']==0 for v in u['totals'].values());require(u['four100'] is four and len(u['physical'])==1,'complete one-class source measurement')
        if name in REPLACED:require(not units[name]['four100'] and four and u['physical']==units[name]['physical'],'strictly complete replacement preserves physical Source identity')
        units[name]=dict(post=JOINT[0],postSha256=JOINT[1],physical=u['physical'],counters=u['totals'],four100=four,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'every normal input unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,owned in p['owners'].items():
        require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical/UNKNOWN ownership preserved')
        require(path not in result['owners'] or result['owners'][path]==owned,'shared owner unchanged');result['owners'][path]=owned
    cases.update(local);physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'no shared physical counter')
    result['originalPostReferences'].append(dict(name=JOINT[0],sha256=JOINT[1],tests=34,suites=5,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='JOINT_ORIGINAL18_AND_NECESSARY_QUALIFICATION16_NOT_WHOLE_451'))
    joint_reference=dict(post=list(JOINT),independentPost=list(JOINT_POST),originalMethods=34,newUniqueMethods=18,necessaryRepeatedMethods=16,originalProductJvms=1,countedInOriginalExecs=True,coverageExecUnion=False,purpose='CURRENT_REQUEST_QUERY_METHOD_COMPLETE_SOURCE_CLOSURE')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+34,uniqueProductMethodDelta=18,sourceProgramDelta=2,jointQualificationReferences=[joint_reference],jointQualificationReplacedUnitHistory=history,necessaryJointRepeatedMethods=16,totalRepeatedOriginalMethods=72)
    require((result['tests'],result['suites'],len(units),len(physical),result['four100SourcePrograms'],len(four),result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'])==(860,121,208,279,129,194,4,53,932),'actual joint accounting and Source quality')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':166,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':84},'known/candidate/UNKNOWN roles not promoted')
    require(all(units[n]==u for n,u in old['fullSourceUnits'].items() if n not in REPLACED) and result['qualificationReplacedUnitHistory']==old['qualificationReplacedUnitHistory'] and result['additionalQualificationReferences']==old['additionalQualificationReferences'],'all unrelated units and Catalog history immutable')
    for v in [old,prior,p,proof]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
