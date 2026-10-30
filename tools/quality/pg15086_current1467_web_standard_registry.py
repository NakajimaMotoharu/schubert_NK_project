"""Bind original44 Web standard cases/three entire Sources; preserve all old domains and owners."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG15068-current1423-web-pool-registry-v1','ca9843224a63a80910ecaffa5fc47ce92b8bf52a0f034fad490421d72edd4a99')
PREV_POST=('PG15070-current1423-web-pool-registry-post-v1','27a08c454a62113a61248de58570dd7d6489e82b388f62c3736b02b4706f1ebd')
REFS=[('PG15080-web-standard-forty-four-post-v1','3d157b5e9596798af838176596aa2afe0804fa279912b9008c909817d91fcbd6','PG15082-web-standard-independent-v1','3212e3a2d7130027494925359710810c852cdf97669b9752bea9c3024e6405f3',44,26)]
OUT=data.BASE/'PG15086-current1467-web-standard-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1467 registry')
    old,prior=[read(pair) for pair in [PREV,PREV_POST]]
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==33,'genuine independently qualified1423')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all frozen current inputs unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['tests']==p['tests']==count and proof['semanticNegativeVectors']==negative_count and proof['sourcePrograms']==3 and proof['physicalClasses']==3 and proof['four100SourcePrograms']==3 and proof['naturallyBranchZeroSourcePrograms']==0 and proof['independentMetricRows']==0 and proof['candidateOwnersNotAccepted'] is True,'exact independent one-Source whole-codec proof')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'actual distinct new cases/single current exec');cases.update(new)
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and (u['four100'] or u['branchNaturallyZero'] and u['threeCounter100']),'new complete nonempty four100 scope')
            units[name]=dict(post=folder,postSha256=pin,physical=u['physical'],counters=u['totals'],four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical row/UNKNOWN exact owner and byte')
            require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=3,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_WEB_GC_JVM_SYSTEM44_THREE_WHOLE_SOURCE_FOUR100_CANDIDATE_NOT_ACCEPTED'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'every whole Source physical closure disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+44,uniqueProductMethodDelta=44,newTestIds=44,sourceProgramDelta=3,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(1467,185,342,455,437,180,280,270,72,73,1561),'exact batch12/Source2 execution and four100 counts')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':270,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':180,'UNKNOWN':103},'two baseline/three UNKNOWN added, no inferred owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old339/domain/history/cost/metadata/formal preserved')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
