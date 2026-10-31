"""Add original23 observation data cases and one whole Source; Root/native authority unchanged."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16450-current2201-config-resource-registry-v1','1a5c0cce5b094ca859c66e83d74987ed4c65ef8c5c6a1ff89c88bf379b05e9b5')
PREV_POST=('PG16452-current2201-config-resource-registry-post-v1','b12f72602c4f8b0aa6336b65b0396bf9ea1fdb75f58dfb94b835aaeaf85f1ce8')
POST=('PG16462-inspector-snapshot-original-twentythree-post-v1','1a169f60c441da38c1e72a8147dc24bd80b47c6f3768e93cd467bf32900d2f5a')
INDEPENDENT=('PG16464-inspector-snapshot-original-twentythree-independent-v1','70f9f89dd9c27e5d3033935b8f5db87d10cac788dcb7e5794c8f43ddf3925918')
OUT=data.BASE/'PG16466-current2224-inspector-snapshot-registry-v1'
SCOPE='ORIGINAL_OBSERVATION_DATA23_THREE_SUITES_ONE_WHOLE_SOURCE_NOT_ROOT_RECOVERY_OR_AUTHORITY'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(value):return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(31,13),'qualified chain')
    require((p['tests'],p['suites'],len(p['physicalClasses']),p['targetSourceUnits'])==(23,3,2,1) and p['strictFour100GateExit']==0 and p['syntheticStateFieldsOnly'] is p['publicDigestOnly'] is p['cryptoOrKeyOperationsInvoked'] is True and p['actualSecretKeysLoaded'] is False and p['actualRootRecoveryOperations']==p['actualFailedCohortCollectionOperations']==0,'whole data-only original23, no Root authority')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==23 and not added&before and all(v['result']=='PASS' for v in p['cases']) and not set(p['fullSourceUnits'])&old['fullSourceUnits'].keys(),'new original cases and whole Sources')
    require(p['metadataClasses']==[],'two genuine executable physical classes, no metadata added')
    for name,unit in p['fullSourceUnits'].items():
        natural=unit['branchNaturallyZero'] and unit['threeCounter100']
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),counters=copy.deepcopy(unit['totals']),four100=unit['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=natural)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    additions=copy.deepcopy(p['owners'])
    for simple in ['InspectorUnitSnapshotTest','InspectorHeldStateContractTest','ArtemisUnitSnapshotTest']:
        path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'+simple+'.java'
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path in ['src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt','src/deployment/systemd/artemis.service']:
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,row in additions.items():
        require(path not in result['owners'] and row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical owner, no inferred allocation')
        result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=23,suites=3,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'nonoverlap physical closures')
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+23,uniqueProductMethodDelta=23,newTestIds=0,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-result['metadataClasses'].keys()),metadataPhysical=len(result['metadataClasses']),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),naturalZeroBranchSourcePrograms=old['naturalZeroBranchSourcePrograms'],naturalZeroBranchPhysical=old['naturalZeroBranchPhysical'],ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    four=[u for u in units.values() if u['four100']];four_physical={n for u in four for n in u['physical']}
    updates.update(four100SourcePrograms=len(four),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-result['metadataClasses'].keys()))
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2205 and len(names-ordinary)==19,'ordinary current methods versus quality18')
    decl.update(ordinaryCaseReferences=2205,ordinaryWithoutCurrentCaseReference=3581,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['metadataPhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'],result['four100ExecutablePhysical'])==(2224,305,493,725,658,67,43,141,2356,266,392,377),'derived exact counts including all forty physical')
    changed=set(updates)|{'invocation','fullSourceUnits','metadataClasses','owners','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items()) and all(result['metadataClasses'][k]==v for k,v in old['metadataClasses'].items()) and all(result['owners'][k]==v for k,v in old['owners'].items()),'old counter proof/history/acceptance/cost preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
