"""Four original resource-only config cases; retain every Main proof and coverage domain."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16436-current2197-maintenance-parser-registry-v1','3b65e2d1c169bf499c92e096758910b6b8bd611bf39d95586543ded0b7286081')
PREV_POST=('PG16438-current2197-maintenance-parser-registry-post-v1','b726e99ee38ca7ee40bebed71c5a4fbad96f8799956312097b62604a9d9ec7af')
REF=('PG16448-config-source-original-four-post-v1','ac7443811550e5f9c99d7d3eaef1b1319552d141861c78debf435b264bdb432d')
OUT=data.BASE/'PG16450-current2201-config-resource-registry-v1'
DOMAIN='RESOURCE_PUBLIC_CONFIG_TEMPLATE_CONTRACTS'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p=[read(v) for v in [PREV,PREV_POST,REF]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'qualified prior source')
    require((p['tests'],p['suites'],p['metadataNegativeVectors'],p['javaSourceProgramsQualified'],p['productionMainTrueProbeHits'])==(4,1,18,0,0) and p['allMainPhysical']==1843 and p['javaCounterCoverageClaimed'] is p['resourceCounterCoverageClaimed'] is p['formalUpdated'] is False,'resource-only original four, no Main coverage')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==4 and not added&before and all(v['result']=='PASS' for v in p['cases']),'four new unique original methods')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical/candidate owner, not group allocation')
        require(path not in result['owners'] or result['owners'][path]==row,'existing owner preserved');result['owners'][path]=copy.deepcopy(row)
    result['resourceOnlyReferences'].append(dict(name=REF[0],sha256=REF[1],tests=4,suites=1,domain=DOMAIN,javaSourceProgramsQualified=0,actualBrowser=False))
    names=before|added
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+4,uniqueProductMethodDelta=4,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),resourceOnlyJavaMethods=old['resourceOnlyJavaMethods']+4,lastUpdateKind='CURRENT_SOURCE_RESOURCE_ONLY_ORIGINAL_METHODS_NO_MAIN_COUNTER_CREDIT')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2182 and len(names-ordinary)==19,'ordinary resource four, not new quality fixtures')
    decl.update(ordinaryCaseReferences=2182,ordinaryWithoutCurrentCaseReference=3604,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['four100SourcePrograms'],result['four100Physical'],result['totalProductExecs'],result['totalMethodExecutions'],result['resourceOnlyJavaMethods'])==(2201,302,492,723,265,390,140,2333,39),'exact counts: Main unchanged despite resource cases')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=413,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=230,UNKNOWN=181),'seven baseline configs/one C06 candidate')
    changed=set(updates)|{'invocation','owners','resourceOnlyReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()) and result['resourceOnlyReferences'][:-1]==old['resourceOnlyReferences'],'all old Source/physical/counter/JS/proof/cost/acceptance preserved')
    for v in [old,prior,p]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
