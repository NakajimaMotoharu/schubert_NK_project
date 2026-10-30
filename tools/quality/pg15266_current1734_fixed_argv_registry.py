"""Bind independent config14/two complete Sources, preserve all previous incomplete scopes and owners."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG15248-current1729-stop-budget-registry-v1','64e5758fc7b382c109741c9f97d291b746046b6446e6befc4beb07c6c662c8bd')
PREV_POST=('PG15250-current1729-stop-budget-registry-post-v1','96044e9d06ed125c56a43da295d29390add8f060e84774c0f4a41b4dca6b9fa6')
REFS=[('PG15261-fixed-service-argv-five-post-v2','330db5435a282e0f6d4c72af0f536871871f2ad20f7fc0760b91bbeebba9a6c8','PG15262-fixed-service-argv-independent-v1','ebe40fe36f407faee91e486ca18901afad67b7c0114fae51e0c223e019a4fbcf',5,29)]
OUT=data.BASE/'PG15266-current1734-fixed-argv-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1697 registry')
    old,prior=[read(pair) for pair in [PREV,PREV_POST]]
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34,'genuine independently qualified1677')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all frozen current inputs unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['tests']==p['tests']==count and proof['semanticNegativeVectors']==negative_count and proof['sourcePrograms']==1 and proof['physicalClasses']==2 and proof['four100SourcePrograms']==1 and p['strictFour100GateExit']==0 and proof['naturallyBranchZeroSourcePrograms']==0 and proof['filesTokenNegativeVectors']==3 and proof['generatedHasCodeNotNoCode'] is True and proof['generatedExecCrcUnmeasured'] is True and proof['baselineMainOwnerRows']==proof['unknownTestOwnerRows']==1 and proof['candidateOwnersNotAccepted'] is True,'exact independent one-Source whole-codec proof')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'actual distinct new cases/single current exec');cases.update(new)
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and u['four100'] is True and u['branchNaturallyZero'] is False and u['threeCounter100'] is True,'new complete nonempty four100 scope')
            units[name]=dict(post=folder,postSha256=pin,physical=u['physical'],counters=u['totals'],four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical row/UNKNOWN exact owner and byte')
            require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_FIXED_ARGV5_WHOLE_SOURCE_TWO_PHYSICAL_CODE_OFFICIAL_SYNTHETIC_FILTER_NOT_NOCODE'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'every whole Source physical closure disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']==5 and len({n for name in incomplete for n in units[name]['physical']})==7,'actual incomplete partition, never hide unexecuted owned overload')
    result.update(incompleteSourcePrograms=len(incomplete),invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+5,uniqueProductMethodDelta=5,newTestIds=5,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(1734,201,358,475,457,194,297,287,82,83,1842),'exact batch12/Source2 execution and four100 counts')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':273,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':204,'UNKNOWN':108},'two baseline/three UNKNOWN added, no inferred owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old353/domain/history/cost/metadata/formal preserved')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
