"""Append three independently checked original methods; preserve every previous Source counter proof."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16547-current2264-artemis-unknown-registry-v2','a0adfe5eea43bfa8ee31dee06915388363e4ffdb839878c03689aca59c25b2db')
PREV_POST=('PG16548-current2264-artemis-unknown-registry-post-v1','ada6860c959f5df3189ad1416c76db66dee2686c56138cedc19cf59282524c6c')
POST=('PG16558-management-encoder-original-three-post-v1','74db80ee6173cb1ae309f125572070673008dd3d86cadd70c50186b6ec6e4e54')
INDEPENDENT=('PG16560-management-encoder-original-three-independent-v1','263239554edf87a9f3a17c7485cf4c19ece1f4b76da7f0bd8d148df9d97c0ea3')
OUT=data.BASE/'PG16562-current2267-management-encoder-registry-v1'
SCOPE='SUPPLEMENTAL_ORIGINAL_ENCODER3_SUPPLIED_SCALAR_GUARD_NOT_PARENT_AUTHORITY_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisManagementEncoderBoundaryTest.java'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(32,6),'qualified independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']),len(p['metadataClasses']))==(3,1,1,6,5) and p['strictFour100GateExit']==1 and p['borrowedScalarGuardOnly'] is True and p['actualFrameCreated'] is False and p['actualParentAuthorityEstablished'] is False and q['existingSourceProofMustBeRetained'] is True,'supplemental partial Source not source replacement')
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
    require(added<=ordinary and len(names&ordinary)==2248 and len(ordinary-names)==3538 and len(names-ordinary)==19,'ordinary and quality domain')
    decl.update(ordinaryCaseReferences=2248,ordinaryWithoutCurrentCaseReference=3538,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'],result['unknownOwnerPaths'])==(2267,312,504,759,147,2399,271,402,192),'exact scope-only totals')
    changed=set(updates)|{'invocation','owners','originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all Source proofs/physical/counters/history/cost unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
