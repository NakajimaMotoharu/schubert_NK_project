"""Scope-only original22 join; preserve every existing Source/counter/proof and cost."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16896-current2468-public-unit-files-registry-v1','c20a6dcd80f11456e1180d875600d7579364756ccd38741099185f63d653221a')
PREV_POST=('PG16898-current2468-public-unit-files-registry-post-v1','b6c615967c884d9d7abf75e9c6c220d56746eb86a49653e26a808ba1c2310ab1')
POST=('PG16910-memory-live-intent-fence-original-eight-post-v1','f1682a56247b26676f366bc4684db898067878a92e996fabb509f04d46d2d0b1')
INDEPENDENT=('PG16912-memory-live-intent-fence-original-eight-independent-v1','4850855d13b902dc1236169893bd9be776ca8d97c96ddd68f7c3e8e073d85198')
SCOPE='SUPPLEMENTAL_ORIGINAL_MEMORY_LIVE_INTENT_FENCE8_ONE_EXISTING_SOURCE_NO_ACTUAL_INTENT_OR_COUNTER_UNION'
OUT=data.BASE/'PG16914-current2476-memory-live-intent-fence-registry-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(54,8),'exact independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']),len(p['metadataClasses']))==(8,3,1,12,5) and p['strictFour100GateExit']==1 and p['memoryProcessAndMarkerPortsOnly'] is True and p['syntheticRetirementCallbacksInvoked'] is True and p['actualGetentOrSystemctlInvoked'] is False and p['actualProcRead'] is False and q['existingSourceProofMustBeRetained'] is True,'partial existing scope, not native/source replacement')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and all(old['metadataClasses'][n]['sha256']==p['physicalClasses'][n] and old['metadataClasses'][n]['kind']=='NO_CODE' for n in p['metadataClasses']),'all three Source and metadata already qualified, no new counter credit')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']};names=before|added
    require(len(added)==8 and not added&before and all(v['result']=='PASS' for v in p['cases']),'22 new unique whole original methods')
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    test_paths={v['path'] for v in bindings if (v['className'],v['method']) in added}
    require(len(test_paths)==3 and added<=ordinary and len(names&ordinary)==2457 and len(ordinary-names)==3329 and len(names-ordinary)==19,'four actual ordinary Test paths, no copied profile path')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in sorted(set(p['owners'])|test_paths):
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owners retained')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=len(added),suites=len(test_paths),execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=len(added),newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+len(added),uniqueProductMethodDelta=len(added),newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    result.update(updates,invocation=invocation);decl.update(ordinaryCaseReferences=2457,ordinaryWithoutCurrentCaseReference=3329,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'])==(2476,354,528,843,168,2608,282,426),'scope-only counts, no Source/physical/four-counter increase')
    changed=set(updates)|{'invocation','owners','originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old Source proofs/physical/counters/history/cost unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
