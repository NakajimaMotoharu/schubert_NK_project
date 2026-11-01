"""Scope-only original default1 join; preserve every existing Source/counter/proof and cost."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17508-current2746-inspector-deployment-registry-v1','eb7902fee60aaf3966019a81ce70ffde89e1d070181fa83264508fc381f6de6a')
PREV_POST=('PG17510-current2746-inspector-deployment-registry-post-v1','a36a52c7f9929cc941898d04794ba361ffbb5bb1a437b2ca9948846300107ba2')
POST=('PG17542-api-default-bind-one-post-v1','7f18c495eaa28389e1b233b6fafc9298ff954bb792f9fc46605a8d61f01d51ea')
INDEPENDENT=('PG17544-api-default-bind-one-independent-v1','59e9990d6ebe91d5aa94eb31f1f87eb8cdc192b00692f2ae7bed23d9ad2ec6aa')
SCOPE='SUPPLEMENTAL_ORIGINAL_API_DEFAULT_BIND1_OWN_FIXED_LOOPBACK_8091_NO_BUSINESS_START_OR_COUNTER_UNION'
OUT=data.BASE/'PG17548-current2747-api-default-bind-registry-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(31,1),'exact independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']),len(p['metadataClasses']))==(1,1,1,2,1) and p['strictFour100GateExit']==1 and p['actualOwnedLoopbackFixtureNetwork'] is True and p['actualExternalNetworkActions']==p['actualProductionServiceActions']==0 and q['transformDefinitionNegativeVectors']==3,'original owned fixed8091 only, not business or Source replacement')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and all(old['metadataClasses'][n]['sha256']==p['physicalClasses'][n] and old['metadataClasses'][n]['kind']=='NO_CODE' for n in p['metadataClasses']),'all three Source and metadata already qualified, no new counter credit')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']};names=before|added
    require(len(added)==1 and not added&before and all(v['result']=='PASS' for v in p['cases']),'seven new unique whole original methods')
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    test_paths={v['path'] for v in bindings if (v['className'],v['method']) in added}
    require(len(test_paths)==1 and added<=ordinary and len(names&ordinary)==2728 and len(ordinary-names)==3058 and len(names-ordinary)==19,'four actual ordinary Test paths, no copied profile path')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in sorted(set(p['owners'])|test_paths):
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owners retained')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=len(added),suites=len(test_paths),execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=len(added),newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+len(added),uniqueProductMethodDelta=len(added),newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    result.update(updates,invocation=invocation);decl.update(ordinaryCaseReferences=2728,ordinaryWithoutCurrentCaseReference=3058,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'])==(2747,405,559,982,201,2879,289,434),'scope-only counts, no Source/physical/four-counter increase')
    changed=set(updates)|{'invocation','owners','originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old Source proofs/physical/counters/history/cost unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
