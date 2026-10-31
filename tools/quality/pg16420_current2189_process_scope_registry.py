"""Replace current partial ProcessScope proof with one whole original seven exec, without union."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16404-current2182-legacy-policy-registry-v1','34386ddf6c7fe6c067f5b5909735d8f487de5a8fc0b95d959bedb201b8ed9889')
PREV_POST=('PG16406-current2182-legacy-policy-registry-post-v1','ded8a7d3b0798d8696cd6da8f12ecef873297fd06273c89b6b2dfee796395e0f')
POST=('PG16416-process-scope-original-seven-post-v1','b8be11c72b5711b54148e5e71f23af4e94db1196655bac3dd7b8972ec61aba3d')
INDEPENDENT=('PG16418-process-scope-original-seven-independent-v1','ecef5f4127d72efbc7b93f525255d06800862232907d1e4dc8d5aab671d3046a')
NAME='dev/codex/schubert/nk/batch/platform/ProcessResourceScope'
OUT=data.BASE/'PG16420-current2189-process-scope-registry-v1'
SCOPE='ORIGINAL_PROCESS_SCOPE_SEVEN_ONE_COMPLETE_SOURCE_REPLACES_PARTIAL_NO_EXEC_UNION'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(26,7),'qualified chain')
    require((p['tests'],p['suites'],p['targetSourceUnits'])==(7,1,1) and p['targetUnitFour100'] is True and p['singleSession'] is True and p['crcMismatch']==0 and p['existingFakeProcessFixtureUsed'] is True and p['productExternalProcessesStarted']==0,'whole original and no actual query')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==7 and not added&before and all(v['result']=='PASS' for v in p['cases']),'seven new current original cases')
    unit=p['fullSourceUnits'][NAME];previous=old['fullSourceUnits'][NAME]
    require(set(p['fullSourceUnits'])=={NAME} and set(previous['physical'])==set(unit['physical']) and not previous['four100'] and unit['four100'] and NAME not in old['qualificationReplacedUnitHistory'],'one existing partial Source')
    require(all(previous['counters'][k]['covered']+previous['counters'][k]['missed']==unit['totals'][k]['covered'] and unit['totals'][k]['missed']==0 for k in unit['totals']),'same full denominator')
    require(all(v in old['metadataClasses'] and old['metadataClasses'][v]['sha256']==p['physicalClasses'][v] for v in p['metadataClasses']),'same genuine interfaces, no inventory change')
    result['qualificationReplacedUnitHistory'][NAME]=copy.deepcopy(previous)
    result['fullSourceUnits'][NAME]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),counters=copy.deepcopy(unit['totals']),four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    require(all(old['owners'][path]==row for path,row in p['owners'].items()),'existing canonical Main owner')
    path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ProcessResourceScopeTest.java'
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(path not in old['owners'],'new Test owner row')
    result['owners'][path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=7,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];four={n for u in units.values() if u['four100'] for n in u['physical']}
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+7,uniqueProductMethodDelta=7,newTestIds=0,sourceProgramDelta=0,four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-result['metadataClasses'].keys()),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2171 and len(names-ordinary)==18,'normal originals versus quality fixture18')
    decl.update(ordinaryCaseReferences=2171,ordinaryWithoutCurrentCaseReference=3615,existingQualityFixtureCases=18);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['four100SourcePrograms'],result['four100Physical'],result['four100ExecutablePhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'])==(2189,299,491,722,264,389,374,44,138,2321),'derived current totals')
    changed=set(updates)|{'invocation','fullSourceUnits','qualificationReplacedUnitHistory','owners','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items() if k!=NAME) and all(result['qualificationReplacedUnitHistory'][k]==v for k,v in old['qualificationReplacedUnitHistory'].items()) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old proofs/cost/acceptance preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
