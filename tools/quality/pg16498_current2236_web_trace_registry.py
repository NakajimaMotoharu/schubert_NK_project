"""Add original request trace10 and replace partial Context with same-denominator whole proof."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16482-current2226-batch-enum-registry-v1','71620afa247589ff1dc183dc822d7d0ab562eac1f47794b540a44cc37fcfa8f1')
PREV_POST=('PG16484-current2226-batch-enum-registry-post-v1','200c86a94628ca2df6a749a95b33b811f9b48fbb866b78d44135f6064c283e19')
POST=('PG16494-web-request-trace-original-ten-post-v1','3ae5aaf2ebec865b7c3cfad02f18622c12ef7f385484bf658b787a941149a9d6')
INDEPENDENT=('PG16496-web-request-trace-original-ten-independent-v1','f2ce126c295e2b7cfd6579676e809d2954cac366382122cfac7bdcb109be032b')
OUT=data.BASE/'PG16498-current2236-web-trace-registry-v1'
SCOPE='ORIGINAL_REQUEST_TRACE10_FOUR_WHOLE_SOURCES_THREE_NEW_ONE_PARTIAL_CONTEXT_REPLACED_NO_EXEC_UNION'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(31,8),'independent chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'],len(p['physicalClasses']))==(10,1,4,5) and p['strictFour100GateExit']==1 and p['syntheticStateFieldsOnly'] is True and p['actualRootRecoveryOperations']==0,'partial enum closure not whole acceptance')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==10 and not added&before and all(v['result']=='PASS' for v in p['cases']),'two unique new original methods')
    new=set(p['fullSourceUnits'])-old['fullSourceUnits'].keys()
    retained=set(p['fullSourceUnits'])&old['fullSourceUnits'].keys()
    require(len(new)==3 and len(retained)==1,'retain all five broader old proofs')
    context='dev/codex/schubert/nk/web/security/WebRequestContext'
    require(retained=={context} and context not in old['qualificationReplacedUnitHistory'],'one original partial context')
    previous=old['fullSourceUnits'][context];current=p['fullSourceUnits'][context]
    require(not previous['four100'] and current['four100'] and previous['physical']==current['physical'],'same whole context complete')
    require(all(a['covered']+a['missed']==current['totals'][k]['covered'] and current['totals'][k]['missed']==0 for k,a in previous['counters'].items()),'same denominator not exclusion')
    result['qualificationReplacedUnitHistory'][context]=copy.deepcopy(previous)
    for name in sorted(p['fullSourceUnits']):
        u=p['fullSourceUnits'][name]
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    for name in p['metadataClasses']:
        require(name not in old['metadataClasses'],'new metadata not old overlap')
        result['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    additions=copy.deepcopy(p['owners'])
    path='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/WebRequestTraceTest.java'
    additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,row in additions.items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical owner')
        if path in old['owners']:require(old['owners'][path]==row,'old owner unchanged')
        else:result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=10,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'whole source nonoverlap')
    four=[u for u in units.values() if u['four100']];four_physical={n for u in four for n in u['physical']}
    natural=[u for u in units.values() if u['branchNaturallyZero']]
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+10,uniqueProductMethodDelta=10,newTestIds=0,sourceProgramDelta=len(new),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-result['metadataClasses'].keys()),metadataPhysical=len(result['metadataClasses']),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),naturalZeroBranchSourcePrograms=len(natural),naturalZeroBranchPhysical=sum(len(u['physical']) for u in natural),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),four100SourcePrograms=len(four),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-result['metadataClasses'].keys()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TRACE_ADDITION_AND_CONTEXT_COMPLETION_HISTORY_RETAINED')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2217 and len(names-ordinary)==19,'ordinary versus quality19')
    decl.update(ordinaryCaseReferences=2217,ordinaryWithoutCurrentCaseReference=3569,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['metadataPhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'],result['four100SourcePrograms'],result['four100Physical'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'])==(2236,308,499,750,675,75,44,143,2368,269,396,180,195),'honest exact counts')
    changed=set(updates)|{'invocation','fullSourceUnits','metadataClasses','owners','originalPostReferences','currentOrdinaryTestDeclarationReference','qualificationReplacedUnitHistory'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items() if k!=context) and all(result['qualificationReplacedUnitHistory'][k]==v for k,v in old['qualificationReplacedUnitHistory'].items()) and all(result['metadataClasses'][k]==v for k,v in old['metadataClasses'].items()) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old evidence/history/cost preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
