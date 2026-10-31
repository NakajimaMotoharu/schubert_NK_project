"""Append three independently checked original methods; preserve every previous Source counter proof."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16750-current2374-broker-xml-registry-v1','afa9060c34781dc13ea5bc9ad56554b00bc0df56f906c6bb877e97b043aa1399')
PREV_POST=('PG16753-current2374-broker-xml-registry-post-v2','65d58ec75beaddd9a49976619493e115168d1ac2996e3952ea300c11edbf334b')
POST=('PG16762-bootstrap-closing-original-three-post-v1','4eb4713eb084a176e253a32ab3d76b2600dfe21dafecb2c6eb9689479411cd4e')
INDEPENDENT=('PG16764-bootstrap-closing-original-three-independent-v1','6a3fad517e1382d06f971995460bc3470367737643c23c47d9f489c93f4c8d8b')
OUT=data.BASE/'PG16766-current2377-bootstrap-closing-registry-v1'
SCOPE='SUPPLEMENTAL_ORIGINAL_CLOSING3_INJECTED_INSTANCE_MAIN_NOT_ADMIN_OR_TERMINATION_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/BootstrapClosingBoundaryTest.java'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(50,1),'qualified independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']),len(p['metadataClasses']))==(3,1,1,3,2) and p['strictFour100GateExit']==1 and p['explicitInjectedInstanceMainOnly'] is True and p['actualAdministratorOrProcessTerminationInvoked'] is False and q['existingSourceProofMustBeRetained'] is True,'supplemental partial Source not source replacement')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and p['actualRootRecoveryOperations']==p['actualJmsConnectionsCreated']==0,'existing Source and no operational authority')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==3 and not added&before and all(v['result']=='PASS' for v in p['cases']),'three new original methods')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in list(p['owners'])+[TEST]:
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owner retained')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=3,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=3,newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    names=before|added
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+3,uniqueProductMethodDelta=3,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2358 and len(ordinary-names)==3428 and len(names-ordinary)==19,'ordinary and quality domain')
    decl.update(ordinaryCaseReferences=2358,ordinaryWithoutCurrentCaseReference=3428,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'],result['unknownOwnerPaths'])==(2377,334,521,812,159,2509,281,421,214),'exact scope-only totals')
    changed=set(updates)|{'invocation','owners','originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all Source proofs/physical/counters/history/cost unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
