"""Scope-only original permit-data6 join; preserve every existing Source/counter/proof and cost."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17628-current2774-checkpoint-public-provider-registry-v1','d3d5bd52d29fecf9b227ff98f8af753af1be71b21b49c8be6f06c68602a3e616')
PREV_POST=('PG17630-current2774-checkpoint-public-provider-registry-post-v1','499cb96aed7d848ae9c40d8933b241c51b8b50bdfa54cd503ad1b500fd99c07d')
POST=('PG17642-current-permit-data-six-post-v1','f59b1db5c4b23ed3981bad802ab621b9f90dce497ac030ce73d4a7892b87cfea')
INDEPENDENT=('PG17644-current-permit-data-six-independent-v1','d59a5f733907ca5badb4b3805a338f89209f2bfbea4f01d9c584d2af68bc840e')
SCOPE='SUPPLEMENTAL_ORIGINAL_CURRENT_PERMIT_DATA6_NO_REAL_PERMIT_ROOT_OR_IO_NO_COUNTER_UNION'
OUT=data.BASE/'PG17648-current2780-permit-data-registry-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(28,6),'exact independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']),len(p['metadataClasses']))==(6,1,1,2,0) and p['strictFour100GateExit']==1 and p['syntheticPermitRecordConstructionOnly'] is p['nativeNamedReadNullGuardOnlyInvoked'] is p['syntheticRootAdmissionCallbackInvoked'] is True and p['actualPermitNamespaceLookups']==0 and p['actualRootOsAdmissionInvoked'] is False and q['sourceLinePairNegativeVectors']==3,'pure data/null guard/injected callback, not actual authority')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and all(old['metadataClasses'][n]['sha256']==p['physicalClasses'][n] and old['metadataClasses'][n]['kind']=='NO_CODE' for n in p['metadataClasses']),'all three Source and metadata already qualified, no new counter credit')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']};names=before|added
    require(len(added)==6 and not added&before and all(v['result']=='PASS' for v in p['cases']),'seven new unique whole original methods')
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    test_paths={v['path'] for v in bindings if (v['className'],v['method']) in added}
    require(len(test_paths)==1 and added<=ordinary and len(names&ordinary)==2761 and len(ordinary-names)==3025 and len(names-ordinary)==19,'four actual ordinary Test paths, no copied profile path')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in sorted(set(p['owners'])|test_paths):
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owners retained')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=len(added),suites=len(test_paths),execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=len(added),newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+len(added),uniqueProductMethodDelta=len(added),newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    result.update(updates,invocation=invocation);decl.update(ordinaryCaseReferences=2761,ordinaryWithoutCurrentCaseReference=3025,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'])==(2780,409,560,990,204,2912,289,434),'scope-only counts, no Source/physical/four-counter increase')
    changed=set(updates)|{'invocation','owners','originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old Source proofs/physical/counters/history/cost unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
