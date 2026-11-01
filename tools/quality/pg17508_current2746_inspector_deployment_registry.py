"""Eight original owned wrapper/Unit contract cases; retain every Main proof and coverage domain."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17488-current2738-expiry-owner-registry-v1','516ee3390c8ac829351f212f78b8659b0eaf712b457b37a487cfd5961fb18cef')
PREV_POST=('PG17491-current2738-expiry-owner-registry-post-v2','4edc2d21efd741b6aef2bde6c9f686249c79b1592ff42f6bb60b98ea9ab3e945')
REF=('PG17504-inspector-deployment-eight-post-v2','01d2c806530da2f46995fac71d77f0e492d8b4e90ec3433ae50beb36c5df0d6f')
OUT=data.BASE/'PG17508-current2746-inspector-deployment-registry-v1'
DOMAIN='RESOURCE_PUBLIC_INSPECTOR_WRAPPER_UNIT_CONTRACTS_WITH_EMPTY_ENV_CHILD_CLI_NO_MAIN_CREDIT'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p=[read(v) for v in [PREV,PREV_POST,REF]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'qualified prior source')
    require((p['tests'],p['suites'],p['metadataNegativeVectors'],p['javaSourceProgramsQualified'],p['parentProductionMainTrueProbeHits'])==(8,1,25,0,0) and p['allMainPhysical']==1843 and p['parentCoverageScopeOnly'] is True and p['ownJavaChildCount']==1 and p['childJavaCoverageClaimed'] is False and p['publicToolReceiptCount']==50 and p['methodCatalogNegativeVectors']==3 and p['javaCounterCoverageClaimed'] is p['resourceCounterCoverageClaimed'] is p['formalUpdated'] is False,'resource-only original four, no Main coverage')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==8 and not added&before and all(v['result']=='PASS' for v in p['cases']),'four new unique original methods')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical/candidate owner, not group allocation')
        require(path not in result['owners'] or result['owners'][path]==row,'existing owner preserved');result['owners'][path]=copy.deepcopy(row)
    result['resourceOnlyReferences'].append(dict(name=REF[0],sha256=REF[1],tests=8,suites=1,domain=DOMAIN,javaSourceProgramsQualified=0,actualBrowser=False,ownUnadmittedCliChild=1,childJavaCoverageQualified=False,originalPublicToolReceipts=50))
    names=before|added
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+8,uniqueProductMethodDelta=8,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),resourceOnlyJavaMethods=old['resourceOnlyJavaMethods']+8,lastUpdateKind='CURRENT_SOURCE_RESOURCE_ONLY_ORIGINAL_METHODS_NO_MAIN_COUNTER_CREDIT')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2727 and len(names-ordinary)==19,'ordinary resource four, not new quality fixtures')
    decl.update(ordinaryCaseReferences=2727,ordinaryWithoutCurrentCaseReference=3059,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['four100SourcePrograms'],result['four100Physical'],result['totalProductExecs'],result['totalMethodExecutions'],result['resourceOnlyJavaMethods'])==(2746,404,559,982,289,434,200,2878,79),'exact counts: Main unchanged despite resource cases')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=496,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=234,UNKNOWN=285),'two candidate POMs and two UNKNOWN tests')
    changed=set(updates)|{'invocation','owners','resourceOnlyReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()) and result['resourceOnlyReferences'][:-1]==old['resourceOnlyReferences'],'all old Source/physical/counter/JS/proof/cost/acceptance preserved')
    for v in [old,prior,p]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
