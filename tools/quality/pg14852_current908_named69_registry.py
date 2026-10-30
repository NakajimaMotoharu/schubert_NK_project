"""Source-only expansion from already counted31/current exec; original908 cases and60 JVMs unchanged."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg14750_current860_joint_registry import SOURCE,read,require

PREV=('PG14836-current908-resource-registry-v1','af91672ea724386906cce9ad70ae6e85e33f68455fcc14db020715da5b0033dd')
PREV_POST=('PG14838-current908-resource-registry-post-v1','acb119d2f176b09ac2cf673883b5061d701d94c06907aa263fddc2e8fc774681')
QUAL=('PG14846-named-dto-existing-exec-post-v1','cdb2e9a507db0c0199ae199bab7c4ffa3aaa3045a699901ba00e25b493846cd8')
QUAL_POST=('PG14848-named-dto-existing-exec-independent-v1','31ba15f6704e53fa6602c8ad0d7880f8c45382ba0362d183dc44594034a3e6e7')
OUT=data.BASE/'PG14852-current908-named69-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only69 Source binding registry')
    old,prior,p,proof=[read(pair) for pair in [PREV,PREV_POST,QUAL,QUAL_POST]]
    require(all(v['source']==SOURCE and v['actualExit']==0 for v in [old,prior,p,proof]),'genuine same source receipts')
    require(prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==22 and proof['postSha256']==QUAL[1] and proof['semanticNegativeVectors']==20 and proof['newSourcePrograms']==69,'independent old/current69 proofs')
    require(proof['originalXmlMethodsAlreadyCounted']==31 and proof['newUniqueMethods']==proof['productTestsExecuted']==p['newProductExecutions']==p['newUniqueMethods']==0 and p['currentSourceExistingExecReanalyzed'] is p['originalTestsCountedElsewhere'] is True,'no original case/JVM double count')
    old_cases={(v['classname'],v['name']) for v in old['cases']};require(len(p['cases'])==31 and {(v['classname'],v['name']) for v in p['cases']}<=old_cases,'all31 already registered')
    result=copy.deepcopy(old);units=result['fullSourceUnits']
    require(len(p['fullSourceUnits'])==69 and not units.keys()&p['fullSourceUnits'].keys() and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[] and p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True,'new whole69, one unexcluded current exec')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==[name] and u['totals']['BRANCH']==dict(missed=0,covered=0) and all(u['totals'][k]['missed']==0 and u['totals'][k]['covered']>0 for k in ['LINE','METHOD','CLASS']) and u['four100'] is False and u['metadataOnly'] is False,'actual nonempty LMC100/naturalB0, not noCode/four100')
        units[name]=dict(post=QUAL[0],postSha256=QUAL[1],physical=[name],counters=u['totals'],four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=True)
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'whole fixed normal input unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,owned in p['owners'].items():
        require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical/UNKNOWN role actual source join')
        require(path not in result['owners'] or result['owners'][path]==owned,'existing owner unchanged');result['owners'][path]=owned
    result['additionalScopeReferences'].append(dict(name=QUAL[0],sha256=QUAL[1],independentPost=list(QUAL_POST),domain='SAVED_CURRENT_EXEC_ADDITIONAL_SOURCE_SCOPE',sourcePrograms=69,tests=31,originalTestsAlreadyCounted=True,newUniqueMethods=0,newProductExecutions=0,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],coverageExecUnion=False))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'all Source physical closures disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),uniqueProductMethodDelta=0,sourceProgramDelta=69)
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['naturalZeroBranchSourcePrograms'],len(natural),result['totalProductExecs'],result['totalMethodExecutions'])==(908,131,280,354,342,130,195,145,153,60,988),'Source-only extension; exact unchanged case/JVM/method totals')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':258,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':98},'only69 baseline source owners added')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','fullSourceUnits','owners','additionalScopeReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','uniqueProductMethodDelta','sourceProgramDelta'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all cases/executions/old Source/Catalog/joint/JS/formal unchanged')
    for v in [old,prior,p,proof]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
