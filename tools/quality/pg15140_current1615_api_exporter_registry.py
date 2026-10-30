"""Bind new48 API exporter cases/necessary repeat14/two complete Source scopes; preserve candidate owners and all old domains."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG15122-current1567-api-pool-registry-v1','abcda0a7df5caf74ad7d419638df817a59811cb86dbc87d0d8a177b9ef8767c5')
PREV_POST=('PG15124-current1567-api-pool-registry-post-v1','0a9e4210da344a41a5dd6d40d40833936d16cc85d50e2584d77043bf36f42e49')
REFS=[('PG15134-api-exporter-joint-sixty-two-post-v1','de73e9d5f0ddcaa7673008f5d8e8a22ed54b8059de30bd7628676c196e95bdd6','PG15136-api-exporter-joint-independent-v1','e484a2b67c29d4d862ddef0aea018c36f4e52afea8b3ec9da996a10058605918',62,26)]
OUT=data.BASE/'PG15140-current1615-api-exporter-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1615 registry')
    old,prior=[read(pair) for pair in [PREV,PREV_POST]]
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==33,'genuine independently qualified1567')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all frozen current inputs unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['tests']==p['tests']==count and proof['semanticNegativeVectors']==negative_count and proof['sourcePrograms']==2 and proof['physicalClasses']==2 and proof['four100SourcePrograms']==2 and proof['naturallyBranchZeroSourcePrograms']==0 and proof['independentMetricRows']==16 and proof['newUniqueMethods']==48 and proof['repeatedOriginalMethods']==14 and proof['necessaryDependencyReplayNotConfirmation'] is True and proof['candidateOwnersNotAccepted'] is True,'exact independent one-Source whole-codec proof')
        attempt={(c['classname'],c['name']) for c in p['cases']};repeated=attempt&cases;new=attempt-cases
        expected_repeated={(c['classname'],c['name']) for c in old['cases'] if c['classname']=='dev.codex.schubert.nk.api.monitoring.ApiMetricScrapeTest'}
        require(len(attempt)==count==62 and len(new)==p['newUniqueMethods']==48 and repeated==expected_repeated and len(repeated)==p['repeatedOriginalMethods']==14 and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'new48 and necessary sameexec repeated14 explicitly separated');cases.update(new)
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and (u['four100'] or u['branchNaturallyZero'] and u['threeCounter100']),'new complete nonempty four100 scope')
            units[name]=dict(post=folder,postSha256=pin,physical=u['physical'],counters=u['totals'],four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical row/UNKNOWN exact owner and byte')
            require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=3,newUniqueMethods=48,repeatedOriginalMethods=14,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_API_EXPORTER_JOINT62_NEW48_NECESSARY_REPEAT14_TWO_WHOLE_SOURCE_FOUR100'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'every whole Source physical closure disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+62,totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods']+14,uniqueProductMethodDelta=48,newTestIds=48,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(1615,193,350,465,447,187,289,279,75,76,1723),'exact batch12/Source2 execution and four100 counts')
    require(result['totalRepeatedOriginalMethods']==108 and old['totalRepeatedOriginalMethods']==94 and result['totalMethodExecutions']==result['tests']+108,'old94 historical repeats retained plus necessary14, no unique inflation')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':270,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':196,'UNKNOWN':103},'two baseline/three UNKNOWN added, no inferred owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','totalRepeatedOriginalMethods'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old348/domain/history/cost/metadata/formal preserved')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
