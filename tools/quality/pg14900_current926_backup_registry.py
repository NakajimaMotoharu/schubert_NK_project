"""Batch binding of twelve original public claim-codec cases/two Source closures; no reexecution."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG14876-current914-carrier-registry-v1','f75bcddfec1b33a972f607881b2de07a129ac5bb0d01f344bb5ce0f5cf74979b')
PREV_POST=('PG14878-current914-carrier-registry-post-v1','8f6e2590dbde2b3ab427c21a1e3311a854020d7e78bb4fdd74b5c4f398b72981')
REFS=[('PG14888-backup-manifest-codec-eight-post-v1','bf31dcc65b69da33f948f7af4e4ddc35871c7339e7e1433bdc1ce22b56ff7048','PG14890-backup-manifest-codec-independent-v1','96f0e91060e99a3313a8a6bfc38bdb06816065bbb10a3b234fe02b91059640e0',8,22),('PG14895-backup-profile-four-post-v2','d32a7fc98d46a964b318402cbe5bd09e671c8e2bd5409d142c3d0206eecfd8b3','PG14896-backup-profile-independent-v1','c34e3cbb732ae4f01113e15bdaa363807b49e29a494bda8560c522181617e290',4,21)]
OUT=data.BASE/'PG14900-current926-backup-registry-v1'

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only926 registry')
    old,prior=[read(pair) for pair in [PREV,PREV_POST]]
    require(old['actualExit']==prior['actualExit']==0 and old['source']==prior['source']==SOURCE and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==29,'genuine independently qualified914')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};units=result['fullSourceUnits'];witnesses=[]
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all frozen current inputs unchanged')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for folder,pin,independent,independent_pin,count,negative_count in REFS:
        p=read((folder,pin));proof=read((independent,independent_pin));witnesses.extend([p,proof])
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['tests']==p['tests']==count and proof['semanticNegativeVectors']==negative_count and proof['sourcePrograms']==proof['physicalClasses']==proof['four100SourcePrograms']==1,'exact independent one-Source whole-codec proof')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==[],'actual distinct new cases/single current exec');cases.update(new)
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==[name] and u['four100'] is True and all(v['missed']==0 and v['covered']>0 for v in u['totals'].values()),'new complete nonempty four100 scope')
            units[name]=dict(post=folder,postSha256=pin,physical=[name],counters=u['totals'],four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical row/UNKNOWN exact owner and byte')
            require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_PUBLIC_BACKUP_CLAIM_CODEC_WHOLE_SOURCE_NOT_ACTUAL_BACKUP'))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'every whole Source physical closure disjoint')
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+2,totalProductExecs=old['totalProductExecs']+2,totalMethodExecutions=old['totalMethodExecutions']+12,uniqueProductMethodDelta=12,newTestIds=12,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(926,134,289,367,349,133,198,188,62,63,1006),'exact batch12/Source2 execution and four100 counts')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':267,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':80,'UNKNOWN':102},'two baseline/three UNKNOWN added, no inferred owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old287/domain/history/cost/metadata/formal preserved')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
