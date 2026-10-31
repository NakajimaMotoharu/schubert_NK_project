"""Add original memory-port Morning33; keep all partial/NoCode/whole-Source denominators honest."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16608-current2282-application-unit-registry-v1','2474e9273df26df9b0d3af9822dbe6ebb927429ef9e1f0b72b9543b2d6b9576e')
PREV_POST=('PG16610-current2282-application-unit-registry-post-v1','3510478d48ad003acbd47214891848b5e3424af98b8c5c30868fda4c39baa3a1')
POST=('PG16620-morning-pure-data-original-33-post-v1','a878d423f42737c284f3f7aa6cea59619e0da023340a532f5d3f24e93f3e2424')
INDEPENDENT=('PG16622-morning-pure-data-original-33-independent-v1','899f8f79bb5adee3815c59d5549bcff6d6aa968c11a16717b4383c93caaf0874')
OUT=data.BASE/'PG16624-current2315-morning-pure-registry-v1'
SCOPE='ORIGINAL_MORNING33_FOUR_COMPLETE_SOURCE_DENOMINATORS_TWO_FOUR100_ONE_NATURAL_ONE_PARTIAL'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(41,6),'independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']))==(33,6,4,13) and p['strictFour100GateExit']==1 and p['approvedInjectedBackupCycleOnly'] is True and p['cryptoOrKeyOperationsInvoked'] is True and p['publicDigestOnly'] is True and p['actualRootRecoveryOperations']==p['actualJmsConnectionsCreated']==0,'partial enum closure not whole acceptance')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==33 and not added&before and all(v['result']=='PASS' for v in p['cases']),'two unique new original methods')
    new=set(p['fullSourceUnits'])-old['fullSourceUnits'].keys()
    retained=set(p['fullSourceUnits'])&old['fullSourceUnits'].keys()
    require(len(new)==4 and len(retained)==0,'retain all five broader old proofs')
    for name in sorted(new):
        u=p['fullSourceUnits'][name]
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    for name in p['metadataClasses']:
        require(name not in old['metadataClasses'],'new metadata not old overlap')
        result['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    additions=copy.deepcopy(p['owners'])
    for path in json.loads("[\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningBackupObservedCompletionTest.java\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningCompletionChecksTest.java\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningCompletionEvidenceTest.java\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningCompletionRetirementTest.java\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MorningPrestartEvidenceTest.java\",\"src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/StoppedBackupCompletionTest.java\"]"):
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,row in additions.items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical owner')
        if path in old['owners']:require(old['owners'][path]==row,'old owner unchanged')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=33,suites=6,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'whole source nonoverlap')
    four=[u for u in units.values() if u['four100']];four_physical={n for u in four for n in u['physical']}
    natural=[u for u in units.values() if u['branchNaturallyZero']]
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+33,uniqueProductMethodDelta=33,newTestIds=0,sourceProgramDelta=len(new),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-result['metadataClasses'].keys()),metadataPhysical=len(result['metadataClasses']),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),naturalZeroBranchSourcePrograms=len(natural),naturalZeroBranchPhysical=sum(len(u['physical']) for u in natural),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),four100SourcePrograms=len(four),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-result['metadataClasses'].keys()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_BROADER_OLD_PROOFS_RETAINED_PARTIAL_DISCLOSED')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2296 and len(names-ordinary)==19,'ordinary versus quality19')
    decl.update(ordinaryCaseReferences=2296,ordinaryWithoutCurrentCaseReference=3490,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['metadataPhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(2315,321,510,774,692,82,46,151,2447,275,407,183,198),'honest exact counts')
    changed=set(updates)|{'invocation','fullSourceUnits','metadataClasses','owners','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items()) and all(result['metadataClasses'][k]==v for k,v in old['metadataClasses'].items()) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old evidence/history/cost preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
