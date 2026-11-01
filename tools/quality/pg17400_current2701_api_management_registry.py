"""Add original own HTTP11; maintain complete partial Source and all old qualified proofs."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17378-current2690-web-codec-owner-registry-v1','6ebc5bde4fe2f26d0ddebd442788fb9cd347777080d50187c5e87ff4f0e64790')
PREV_POST=('PG17380-current2690-web-codec-owner-registry-post-v1','8662713ec01aaeb32c4b2d5c1cf6ede8e36fdf6e18b6e02455c4f06c4c27f32c')
POST=('PG17396-api-management-eleven-post-v2','d0c5dbda2ec74f00bb1f6bf136c70ab9a15d3ac75673303a1d4ddd5617584ede')
INDEPENDENT=('PG17398-api-management-eleven-independent-v1','4bfd1bfcd5c23583ba851305be089e4e189e05f4eee1d75c2b1bc4d467717334')
OUT=data.BASE/'PG17400-current2701-api-management-registry-v1'
SCOPE='ORIGINAL_API_MANAGEMENT11_ONE_SOURCE_TWO_PHYSICAL_PARTIAL_SELF_OWNED_HTTP_NOT_PRODUCTION_NATIVE_OR_COUNTER_UNION'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(31,11),'independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']))==(11,2,1,2) and p['strictFour100GateExit']==1 and p['approvedInjectedBackupCycleOnly'] is False and p['cryptoOrKeyOperationsInvoked'] is False and p['publicDigestOnly'] is False and p['publicSyntheticUuidFixture'] is False and p['actualRootRecoveryOperations']==p['actualJmsConnectionsCreated']==0,'partial enum closure not whole acceptance')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==11 and not added&before and all(v['result']=='PASS' for v in p['cases']),'two unique new original methods')
    new=set(p['fullSourceUnits'])-old['fullSourceUnits'].keys()
    retained=set(p['fullSourceUnits'])&old['fullSourceUnits'].keys()
    require(len(new)==1 and len(retained)==0,'retain all five broader old proofs')
    for name in sorted(new):
        u=p['fullSourceUnits'][name]
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    for name in p['metadataClasses']:
        if name in old['metadataClasses']:
            require(old['metadataClasses'][name]['sha256']==p['physicalClasses'][name] and old['metadataClasses'][name]['kind']=='NO_CODE','existing metadata retained')
        else:
            require(any(name in p['fullSourceUnits'][n]['physical'] for n in new),'new metadata belongs to new Source')
            result['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=11,newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(retained),newSourceNames=sorted(new),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    additions=copy.deepcopy(p['owners'])
    for path in ['src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServerTest.java','src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementStopTest.java']:
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,row in additions.items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical owner')
        if path in old['owners']:require(old['owners'][path]==row,'old owner unchanged')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=11,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'whole source nonoverlap')
    four=[u for u in units.values() if u['four100']];four_physical={n for u in four for n in u['physical']}
    natural=[u for u in units.values() if u['branchNaturallyZero']]
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+11,uniqueProductMethodDelta=11,newTestIds=0,sourceProgramDelta=len(new),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-result['metadataClasses'].keys()),metadataPhysical=len(result['metadataClasses']),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),naturalZeroBranchSourcePrograms=len(natural),naturalZeroBranchPhysical=sum(len(u['physical']) for u in natural),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),four100SourcePrograms=len(four),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-result['metadataClasses'].keys()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_BROADER_OLD_PROOFS_RETAINED_PARTIAL_DISCLOSED')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2682 and len(names-ordinary)==19,'ordinary versus quality19')
    decl.update(ordinaryCaseReferences=2682,ordinaryWithoutCurrentCaseReference=3104,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['metadataPhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(2701,397,555,962,795,167,77,195,2833,289,434,183,198),'honest exact counts')
    changed=set(updates)|{'invocation','fullSourceUnits','metadataClasses','owners','originalPostReferences','additionalScopeReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items()) and all(result['metadataClasses'][k]==v for k,v in old['metadataClasses'].items()) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old evidence/history/cost preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
