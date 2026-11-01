"""Scope-only original permit-data6 join; preserve every existing Source/counter/proof and cost."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17648-current2780-permit-data-registry-v1','ffd247fe95c7560885b25d0eff356d673841c8d0959e153ba9dc35c7d3c0560a')
PREV_POST=('PG17650-current2780-permit-data-registry-post-v1','ce166c4d8b591dbd8b29c0345e8fce5d0b4a2ee1b2e90f1d19dfb2aeebaeab68')
POST=('PG17662-root-entry-denial-four-post-v1','733fdc388fe8048c75b75a2a386b6aadce3b071339970bf786351eae051cd508')
INDEPENDENT=('PG17664-root-entry-denial-four-independent-v1','94511da038879b3527e0e3d2007da0654ca4f3cb28b9d26679778e57864508a0')
SCOPE='SUPPLEMENTAL_ORIGINAL_ROOT_ENTRY_DENIAL4_INJECTED_ALL_DENY_AND_FAKE_DESCRIPTOR_NO_NATIVE_COUNTER_UNION'
OUT=data.BASE/'PG17668-current2784-root-entry-denial-registry-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(28,4),'exact independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']),len(p['metadataClasses']))==(4,1,2,9,5) and p['strictFour100GateExit']==1 and p['rootContextInjectedAllDenyConstructorOnly'] is p['declaredFakeDescriptor319Only'] is True and p['syntheticRootAdmissionCallbackInvoked'] is False and p['actualPermitNamespaceLookups']==0 and p['actualRootOsAdmissionInvoked'] is False and q['injectedRootContextCtorAudit']['negativeForgedContextRejected'] is True and len(q['unusedBackupHelperRecordPresent'])==3,'pure data/null guard/injected callback, not actual authority')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and all(old['metadataClasses'][n]['sha256']==p['physicalClasses'][n] and old['metadataClasses'][n]['kind']=='NO_CODE' for n in p['metadataClasses']),'all three Source and metadata already qualified, no new counter credit')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']};names=before|added
    require(len(added)==4 and not added&before and all(v['result']=='PASS' for v in p['cases']),'seven new unique whole original methods')
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    test_paths={v['path'] for v in bindings if (v['className'],v['method']) in added}
    require(len(test_paths)==1 and added<=ordinary and len(names&ordinary)==2765 and len(ordinary-names)==3021 and len(names-ordinary)==19,'four actual ordinary Test paths, no copied profile path')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in sorted(set(p['owners'])|test_paths):
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owners retained')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=len(added),suites=len(test_paths),execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=len(added),newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+len(added),uniqueProductMethodDelta=len(added),newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    result.update(updates,invocation=invocation);decl.update(ordinaryCaseReferences=2765,ordinaryWithoutCurrentCaseReference=3021,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'])==(2784,410,560,990,205,2916,289,434),'scope-only counts, no Source/physical/four-counter increase')
    changed=set(updates)|{'invocation','owners','originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old Source proofs/physical/counters/history/cost unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
