"""Preserve prior joint histories; one Question fullproof replacement and true-noCode mapper."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg14750_current860_joint_registry import SOURCE,read,require

PREV=('PG14750-current860-joint-registry-v1','aa7344e8b7996e235239ca529c71b523b3f2d1bcf155ce49ffe38ebc48ebb33c')
PREV_POST=('PG14752-current860-joint-registry-post-v1','0095a9cee26bbfb33cd5d5024a9df362161ce3a8fafee73e5ad932ec8111b5c8')
JOINT=('PG14762-question-sql-joint-eighteen-post-v1','9653028e361d41a2b0793e485797ff93c00c4500acf9a06249a54c2f1179c84e')
JOINT_POST=('PG14764-question-sql-joint-independent-v1','379f0c2f1025dd0cee71fbfd937e3f9a84714d2664edff43a6bc5ec00b10847c')
REQUEST='dev/codex/schubert/nk/api/application/question/QuestionQueryRequest'
REPO='dev/codex/schubert/nk/api/persistence/QuestionQueryRepository'
MAPPER=REPO+'$RowMapper'
OUT=data.BASE/'PG14768-current870-question-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only Question proof registry')
    old,prior,p,proof=[read(v) for v in [PREV,PREV_POST,JOINT,JOINT_POST]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,proof]),'same source actual independent witnesses')
    require(prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==21 and all(json.dumps(v,sort_keys=True)==json.dumps(old[k],sort_keys=True) for k,v in prior['summary'].items()),'qualified860 independent typed summary')
    require(proof['postSha256']==JOINT[1] and proof['newUniqueMethods']==10 and proof['necessaryRepeatedMethods']==8 and proof['semanticNegativeVectors']==20 and proof['rawInvocationRoleNegativeVectors']==4 and proof['forbiddenProductProbeHits']==0,'qualified new10/necessary8 and heldprobe0')
    require(p['singleSession'] is True and p['crcMismatch']==0 and p['oldCoverageTransferred'] is p['priorProductResultsReused'] is False and p['normalManifestSha256']==old['normalManifestSha256'],'single current exec, never union')
    result=copy.deepcopy(old);units=result['fullSourceUnits'];old_cases={(v['classname'],v['name']) for v in old['cases']};local={(v['classname'],v['name']) for v in p['cases']}
    require(len(local)==18 and len(local-old_cases)==10 and len(local&old_cases)==8 and local-old_cases=={(v['classname'],v['name']) for v in proof['newCases']} and local&old_cases=={(v['classname'],v['name']) for v in proof['repeatedCases']},'exact new and repeated identities')
    require(set(p['fullSourceUnits'])=={REQUEST,REPO} and set(units)&{REQUEST,REPO}=={REQUEST},'one declared replacement and one new Source')
    prior_request=copy.deepcopy(units[REQUEST]);require(not prior_request['four100'] and p['fullSourceUnits'][REQUEST]['four100'] is True,'incomplete Request becomes same-exec complete')
    for name,u in p['fullSourceUnits'].items():
        four=all(v['missed']==0 and v['covered']>0 for v in u['totals'].values());require(u['four100'] is four,'actual measured four counters')
        require(u['physical']==([REQUEST] if name==REQUEST else [REPO,MAPPER]),'whole literal Source closure')
        units[name]=dict(post=JOINT[0],postSha256=JOINT[1],physical=u['physical'],counters=u['totals'],four100=four,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    metadata=p['sourcePhysicalInventory'][MAPPER]
    require(p['metadataClasses']==[MAPPER] and metadata==proof['trueNoCodeMetadata'][MAPPER] and metadata['sha256']=='64041f2bfa092b6440952bd1bfcbc9794ecceca64017d3288df8f04264ae63b9' and metadata['flags']==1536 and not any(v['hasCode'] for v in metadata['methods']) and p['manualCounterExclusions']==[],'exact true-noCode mapper included, not filtered code')
    require(MAPPER not in result['metadataClasses'],'new mapper metadata not counted twice');result['metadataClasses'][MAPPER]=dict(kind='NO_CODE',sha256=metadata['sha256'],postSha256=JOINT[1])
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes'];require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all normal current inputs unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,owned in p['owners'].items():
        require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'exact canonical/UNKNOWN role')
        require(path not in result['owners'] or result['owners'][path]==owned,'shared ownership preserved');result['owners'][path]=owned
    cases=old_cases|local;physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'physical closure disjoint')
    result['originalPostReferences'].append(dict(name=JOINT[0],sha256=JOINT[1],tests=18,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='JOINT_ORIGINAL10_AND_NECESSARY_QUALIFICATION8_NOT_WHOLE_451'))
    result['jointQualificationReferences'].append(dict(post=list(JOINT),independentPost=list(JOINT_POST),originalMethods=18,newUniqueMethods=10,necessaryRepeatedMethods=8,originalProductJvms=1,countedInOriginalExecs=True,coverageExecUnion=False,purpose='CURRENT_QUESTION_REQUEST_QUERY_METHOD_COMPLETE_SOURCE_CLOSURE'))
    require(REQUEST not in result['jointQualificationReplacedUnitHistory'],'new replacement history only');result['jointQualificationReplacedUnitHistory'][REQUEST]=prior_request
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),metadataPhysical=len(meta),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+18,uniqueProductMethodDelta=10,sourceProgramDelta=1,necessaryJointRepeatedMethods=old['necessaryJointRepeatedMethods']+8,totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods']+8)
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],len(meta),result['four100SourcePrograms'],len(four),result['totalProductExecs'],result['totalMethodExecutions'],result['totalRepeatedOriginalMethods'])==(870,122,209,281,269,12,130,195,54,950,80),'actual counts from complete current scopes')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':167,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':85} and sum(v['kind']=='NO_CODE' for v in meta.values())==7,'unchanged candidate roles plus true-noCode7')
    require(all(units[n]==v for n,v in old['fullSourceUnits'].items() if n!=REQUEST) and result['jointQualificationReferences'][:-1]==old['jointQualificationReferences'] and all(result['jointQualificationReplacedUnitHistory'][n]==v for n,v in old['jointQualificationReplacedUnitHistory'].items()) and result['additionalQualificationReferences']==old['additionalQualificationReferences'] and result['qualificationReplacedUnitHistory']==old['qualificationReplacedUnitHistory'],'all old cases/proofs/joint and Catalog history preserved')
    for v in [old,prior,p,proof]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
