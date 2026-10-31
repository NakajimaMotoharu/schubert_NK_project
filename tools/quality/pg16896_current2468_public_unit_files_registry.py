"""Five original Unit-resource cases; preserve every Main proof, syntax is not runtime admission."""
import copy
import json
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16880-current2454-caddy-readiness-registry-v1','bc6ef9046abb3f7963afc36303c8d61f5f6324de0ed13a6b497f3046744af5df')
PREV_POST=('PG16882-current2454-caddy-readiness-registry-post-v1','f2e4754641c2ed28b791f3128c02f6f19df7dd782d55067bd448d4fe1bf79946')
REF=('PG16893-public-unit-files-original-fourteen-post-v2','47876c06dd3d76cfbd4a759e6da4eb1470c959d83facdde342aead8eba968a34')
OUT=data.BASE/'PG16896-current2468-public-unit-files-registry-v1'
DOMAIN='RESOURCE_PUBLIC_UNIT_FILES_FOUR_WHOLE_SUITES_SEVEN_SELF_COPIES_NO_MAIN_CREDIT'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p=[read(v) for v in [PREV,PREV_POST,REF]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'qualified prior source')
    require((p['tests'],p['suites'],p['metadataNegativeVectors'],p['javaSourceProgramsQualified'],p['productionMainTrueProbeHits'])==(14,4,22,0,0) and p['allMainPhysical']==1843 and p['javaCounterCoverageClaimed'] is p['resourceCounterCoverageClaimed'] is p['formalUpdated'] is False,'resource-only original four, no Main coverage')
    q=read(('PG16894-public-unit-files-original-fourteen-independent-v1','274360f7060afaad6ed68c791f01d7c2823304b9da4badc6d96fa3a4cd724545'))
    require(q['actualExit']==0 and q['source']==SOURCE and q['postSha256']==REF[1] and q['semanticNegativeVectors']==45 and q['independentOracleGroups']==14 and q['originalMutationCanaries']==0 and p['productionMainRecordsObserved']==[] and p['ownSyntaxParserInvocationsDeclared']==0,'independent text-only qualification')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==14 and not added&before and all(v['result']=='PASS' for v in p['cases']),'four new unique original methods')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical/candidate owner, not group allocation')
        require(path not in result['owners'] or result['owners'][path]==row,'existing owner preserved');result['owners'][path]=copy.deepcopy(row)
    result['resourceOnlyReferences'].append(dict(name=REF[0],sha256=REF[1],tests=len(added),suites=len({c for c,n in added}),domain=DOMAIN,javaSourceProgramsQualified=0,actualBrowser=False))
    names=before|added
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+len(added),uniqueProductMethodDelta=len(added),newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),resourceOnlyJavaMethods=old['resourceOnlyJavaMethods']+len(added),lastUpdateKind='CURRENT_SOURCE_RESOURCE_ONLY_ORIGINAL_METHODS_NO_MAIN_COUNTER_CREDIT')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2449 and len(names-ordinary)==19,'ordinary resource four, not new quality fixtures')
    decl.update(ordinaryCaseReferences=2449,ordinaryWithoutCurrentCaseReference=3337,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['four100SourcePrograms'],result['four100Physical'],result['totalProductExecs'],result['totalMethodExecutions'],result['resourceOnlyJavaMethods'])==(2468,351,528,843,282,426,167,2600,67),'exact counts: Main unchanged despite resource cases')

    changed=set(updates)|{'invocation','owners','resourceOnlyReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['owners'][k]==v for k,v in old['owners'].items()) and result['resourceOnlyReferences'][:-1]==old['resourceOnlyReferences'],'all old Source/physical/counter/JS/proof/cost/acceptance preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
