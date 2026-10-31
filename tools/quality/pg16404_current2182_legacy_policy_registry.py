"""Add eight original current-source cases, all six physical closures and explicit official-filter zero counters."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16334-current2174-observation-registry-v1','4692639392b626eaecd51bf435d54399ada80d7ba95b680e839b378484806215')
PREV_POST=('PG16336-current2174-observation-registry-post-v1','da04a476eb878923825e746d5fca270f910decdd6304d0b7c1f007c8f85c2e46')
POST=('PG16403-legacy-policy-original-eight-post-v3','cfef910bf1c7f8ba95970e36f9eb2893892dda25e54903cf52a7183aab189fdd')
INDEPENDENT=('PG16405-legacy-policy-original-eight-independent-v2','cc40954b365e6d773da24bf57039824e7d0ee2191b77a2aa32eba5bb22054ef2')
OUT=data.BASE/'PG16404-current2182-legacy-policy-registry-v1'
SCOPE='ORIGINAL_LEGACY1_POLICY7_FAKE_PROCESS_SIX_WHOLE_SOURCES_ONE_FOUR100_FIVE_INCOMPLETE'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(value):return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'],q['officialFilterNegativeVectors'])==(34,8,4),'qualified chain')
    require((p['tests'],p['suites'],len(p['physicalClasses']),p['targetSourceUnits'])==(8,2,40,6) and p['strictFour100GateExit']==1 and p['existingFakeProcessFixtureUsed'] is True and p['productExternalProcessesStarted']==0 and p['defaultNativeCallbackInvoked'] is False,'pure original whole eight')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==8 and not added&before and all(v['result']=='PASS' for v in p['cases']) and not set(p['fullSourceUnits'])&old['fullSourceUnits'].keys(),'new original cases and whole Sources')
    for name in p['metadataClasses']:
        inventory=p['sourcePhysicalInventory'][name];genuine=name in p['genuineNoCodeClasses'];filtered=name in p['officialGeneratedNoCounterClasses']
        require(genuine!=filtered and name not in result['metadataClasses'],'zero-counter classification is disjoint and new')
        require((genuine and not any(v['hasCode'] for v in inventory['methods'])) or (filtered and any(v['hasCode'] for v in inventory['methods'])),'genuine NoCode versus official filtered Code')
        result['metadataClasses'][name]=dict(kind='NO_CODE' if genuine else 'OFFICIAL_GENERATED_ONLY_FILTER_ZERO_COUNTER',postSha256=POST[1],sha256=p['physicalClasses'][name])
    for name,unit in p['fullSourceUnits'].items():
        natural=unit['branchNaturallyZero'] and unit['threeCounter100']
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),counters=copy.deepcopy(unit['totals']),four100=unit['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=natural)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    additions=copy.deepcopy(p['owners'])
    for simple in ['LegacyReceiptValueTest','MaintenanceUnitStopPolicyTest']:
        path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'+simple+'.java'
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,row in additions.items():
        require(path not in result['owners'] and row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical owner, no inferred allocation')
        result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=8,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'nonoverlap physical closures')
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+8,uniqueProductMethodDelta=8,newTestIds=0,sourceProgramDelta=6,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-result['metadataClasses'].keys()),metadataPhysical=len(result['metadataClasses']),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),naturalZeroBranchSourcePrograms=old['naturalZeroBranchSourcePrograms'],naturalZeroBranchPhysical=old['naturalZeroBranchPhysical'],ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    four=[u for u in units.values() if u['four100']];four_physical={n for u in four for n in u['physical']}
    updates.update(four100SourcePrograms=len(four),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-result['metadataClasses'].keys()))
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2164 and len(names-ordinary)==18,'ordinary current methods versus quality18')
    decl.update(ordinaryCaseReferences=2164,ordinaryWithoutCurrentCaseReference=3622,existingQualityFixtureCases=18);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['metadataPhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'],result['four100ExecutablePhysical'])==(2182,298,491,722,655,67,45,137,2314,263,386,373),'derived exact counts including all forty physical')
    changed=set(updates)|{'invocation','fullSourceUnits','metadataClasses','owners','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items()) and all(result['metadataClasses'][k]==v for k,v in old['metadataClasses'].items()) and all(result['owners'][k]==v for k,v in old['owners'].items()),'old counter proof/history/acceptance/cost preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
