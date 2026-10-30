"""Only new original24 resource methods; every211 Main Source qualification stays immutable."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg14750_current860_joint_registry import SOURCE,read,require

PREV=('PG14796-current884-resource-registry-v1','7418311af8225dc268023b9d8465b918e878109cb97a8b507a2261f57b425135')
PREV_POST=('PG14798-current884-resource-registry-post-v1','64c9cbea686999868eca761309e9e032ccdfca1297f2f30099116dc7cfa36b22')
REFS=[
 ('PG14814-animation-template-eight-post-v1','af726019a613f03756174386152577f6626086b83d950e0a6d8542d748c74a7e'),
 ('PG14826-log-search-template-eight-post-v1','4876ed0887161392cb9c22acc348f59a97ab2858580073582595d9db840d14a5'),
 ('PG14832-scenario-search-template-eight-post-v1','c9ab33590acbd3cc65f01836dbf9c5f27654869633e3640d634bebf82937e108')]
OUT=data.BASE/'PG14836-current908-resource-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only908 registry')
    old,prior=[read(pair) for pair in [PREV,PREV_POST]]
    require(old['source']==prior['source']==SOURCE and old['actualExit']==prior['actualExit']==0 and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==22,'genuine independently qualified884')
    require(all(json.dumps(v,sort_keys=True)==json.dumps(old[k],sort_keys=True) for k,v in prior['summary'].items()),'all old typed summary fields match')
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'every current normal input unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    result=copy.deepcopy(old);cases={(v['classname'],v['name']) for v in old['cases']};witnesses=[]
    for folder,pin in REFS:
        p=read((folder,pin));witnesses.append(p)
        require(p['source']==SOURCE and p['actualExit']==0 and p['tests']==8 and p['suites']==1 and p['metadataNegativeVectors']==9,'all genuine original8 resource receipts')
        require(p['javaSourceProgramsQualified']==0 and p['javaCounterCoverageClaimed'] is p['resourceCounterCoverageClaimed'] is p['formalUpdated'] is False and p['productTestsReexecutedByPost']==p['newAccepted']==0,'no new Source/counter/acceptance claims')
        local={(v['classname'],v['name']) for v in p['cases']};require(len(local)==8 and not local&cases,'exact new methods disjoint');cases.update(local)
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'all resource/Test canonical/UNKNOWN owners')
            require(path not in result['owners'] or result['owners'][path]==owned,'shared ownership unchanged');result['owners'][path]=owned
        result['resourceOnlyReferences'].append(dict(name=folder,sha256=pin,tests=8,suites=1,domain='RESOURCE_DOM_WRAPPERS',javaSourceProgramsQualified=0,actualBrowser=False))
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+3,totalProductExecs=old['totalProductExecs']+3,totalMethodExecutions=old['totalMethodExecutions']+24,uniqueProductMethodDelta=24,sourceProgramDelta=0,ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),resourceOnlyJavaMethods=old['resourceOnlyJavaMethods']+24)
    require((result['tests'],result['suites'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['resourceOnlyJavaMethods'])==(908,131,59,60,988,35),'exact original/resource domains and method accounting')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','sourceProgramDelta','owners','ownerStatusCounts','unknownOwnerPaths','resourceOnlyReferences','resourceOnlyJavaMethods'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed),'every old Main/counter/metadata/JS/Catalog/joint/history/cost/formal flag unchanged')
    for value in [old,prior,*witnesses]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
