"""Bind actual API16/one entire Source only; Web dynamic HOLD is not promoted."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG15140-current1615-api-exporter-registry-v1','9257a551622f705f5f8364e001dc2b5f5f486436ff84560324a31e6d4e75dc8f')
PREV_POST=('PG15142-current1615-api-exporter-registry-post-v1','6beecec1b86298361f88cf4c4ebd125d8e2530fc95f6e9a4d4b37b536fde113d')
REFS=[('PG15152-api-service-binding-sixteen-post-v1','b2f11b43e299cd166e47cff2352781b89983b6eae2a21e8aaa1e6903dd9b63c8','PG15154-api-service-binding-independent-v1','2107b76d29c05908c5ddcb178ff4520a5957b1848eda2a5e49ed16c269060889',16,26)]
OUT=data.BASE/'PG15158-current1631-api-service-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1631 registry')
    old,prior=[read(pair) for pair in [PREV,PREV_POST]]
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==33,'genuine independently qualified1615')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all frozen current inputs unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['tests']==p['tests']==count and proof['semanticNegativeVectors']==negative_count and proof['sourcePrograms']==1 and proof['physicalClasses']==1 and proof['four100SourcePrograms']==1 and proof['naturallyBranchZeroSourcePrograms']==0 and proof['independentMetricRows']==3 and proof['candidateOwnersNotAccepted'] is True,'exact independent one-Source whole-codec proof')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'actual distinct new cases/single current exec');cases.update(new)
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and (u['four100'] or u['branchNaturallyZero'] and u['threeCounter100']),'new complete nonempty four100 scope')
            units[name]=dict(post=folder,postSha256=pin,physical=u['physical'],counters=u['totals'],four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical row/UNKNOWN exact owner and byte')
            require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_API_SERVICE_BINDING16_ONE_WHOLE_SOURCE_FOUR100_CANDIDATE_NOT_ACCEPTED'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'every whole Source physical closure disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+16,uniqueProductMethodDelta=16,newTestIds=16,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(1631,194,351,466,448,188,290,280,76,77,1739),'exact batch12/Source2 execution and four100 counts')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':270,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':198,'UNKNOWN':103},'two baseline/three UNKNOWN added, no inferred owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old350/domain/history/cost/metadata/formal preserved')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
