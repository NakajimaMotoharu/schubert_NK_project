"""Bind new48 Web exporter cases/necessary repeat14/four complete Source scopes; preserve candidate owners and all old domains."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG15026-current1319-batch-standard-registry-v1','4b1299e57ecb5616727e338e0ef8bc080e5b38fb70c61bd1789df696aebbfbe0')
PREV_POST=('PG15028-current1319-batch-standard-registry-post-v1','e7fcc951b33f0ca4dbbbc46ace25e41377a5c81033cdee70a657c0edc7846892')
REFS=[('PG15044-web-exporter-joint-sixty-two-post-v1','c4622ca8b0bf1ceda149532636dfd47d3195e757db62f874201d8662b874f0e0','PG15046-web-exporter-joint-independent-v1','8c1d9034924e166ebb1cf61ad14163e1e595c9d7f466bed3cce5dc942f27fba5',62,26)]
OUT=data.BASE/'PG15050-current1367-web-exporter-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only1367 registry')
    old,prior=[read(pair) for pair in [PREV,PREV_POST]]
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==33,'genuine independently qualified1319')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all frozen current inputs unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['tests']==p['tests']==count and proof['semanticNegativeVectors']==negative_count and proof['sourcePrograms']==4 and proof['physicalClasses']==4 and proof['four100SourcePrograms']==4 and proof['naturallyBranchZeroSourcePrograms']==0 and proof['independentMetricRows']==7 and proof['newUniqueMethods']==48 and proof['repeatedOriginalMethods']==14 and proof['necessaryDependencyReplayNotConfirmation'] is True and proof['candidateOwnersNotAccepted'] is True,'exact independent one-Source whole-codec proof')
        attempt={(c['classname'],c['name']) for c in p['cases']};repeated=attempt&cases;new=attempt-cases
        expected_repeated={(c['classname'],c['name']) for c in old['cases'] if c['classname']=='dev.codex.schubert.nk.web.monitoring.WebMetricScrapeTest'}
        require(len(attempt)==count==62 and len(new)==p['newUniqueMethods']==48 and repeated==expected_repeated and len(repeated)==p['repeatedOriginalMethods']==14 and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'new48 and necessary sameexec repeated14 explicitly separated');cases.update(new)
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and (u['four100'] or u['branchNaturallyZero'] and u['threeCounter100']),'new complete nonempty four100 scope')
            units[name]=dict(post=folder,postSha256=pin,physical=u['physical'],counters=u['totals'],four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical row/UNKNOWN exact owner and byte')
            require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=4,newUniqueMethods=48,repeatedOriginalMethods=14,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_WEB_EXPORTER_JOINT62_NEW48_NECESSARY_REPEAT14_FOUR_WHOLE_SOURCE_FOUR100'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'every whole Source physical closure disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+62,totalRepeatedOriginalMethods=old['totalRepeatedOriginalMethods']+14,uniqueProductMethodDelta=48,newTestIds=48,sourceProgramDelta=4,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(1367,179,336,447,429,175,273,263,70,71,1461),'exact batch12/Source2 execution and four100 counts')
    require(result['totalRepeatedOriginalMethods']==94 and old['totalRepeatedOriginalMethods']==80 and result['totalMethodExecutions']==result['tests']+94,'old80 historical repeats retained plus necessary14, no unique inflation')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':270,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':168,'UNKNOWN':103},'two baseline/three UNKNOWN added, no inferred owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','totalRepeatedOriginalMethods'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old332/domain/history/cost/metadata/formal preserved')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
