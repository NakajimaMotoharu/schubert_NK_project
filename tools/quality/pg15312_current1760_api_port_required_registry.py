"""Bind independent config14/two complete Sources, preserve all previous incomplete scopes and owners."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg14750_current860_joint_registry import SOURCE,read,require
from trace_owner_join import canonical

PREV=('PG15284-current1748-profile-terminal-registry-v1','7bc09027b74939ddc45fb92d63bb82be1c096f898670f275bed940cbe507435d')
PREV_POST=('PG15286-current1748-profile-terminal-registry-post-v1','06b823d46e3934938ab9e1a3e457f4f22bb920191affb48a334d1f05ded08d97')
REFS=[["PG15302-api-config-readiness-eleven-post-v1","ff665193ddb62c0ed11afac98a9bc5465167ad5348552b2d1d093951de59b92b","PG15305-api-config-readiness-independent-v2","4cc5defabe34aedf85ef9bf461d98138b5a0b8b568a3a49cbcf0a0719564cf79",11,29],["PG15309-required-column-one-post-v2","e26d863768b8659de2840b77421fd2f675d66a5dd9418b91a1796e691853d632","PG15310-required-column-independent-v1","700b7781f168bf6fcab5da9c0c014233d2e56fa10dcd901858c7d03f064941aa",1,29]]
OUT=data.BASE/'PG15312-current1760-api-port-required-registry-v1'

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
        require(p['actualExit']==proof['actualExit']==0 and p['source']==proof['source']==SOURCE and proof['postSha256']==pin and proof['tests']==p['tests']==count and proof['semanticNegativeVectors']==negative_count and proof['sourcePrograms']==1 and proof['physicalClasses']==(3 if count==11 else 1) and proof['four100SourcePrograms']==(0 if count==11 else 1) and p['strictFour100GateExit']==(1 if count==11 else 0) and proof['naturallyBranchZeroSourcePrograms']==0 and proof['baselineMainOwnerRows']==1 and proof['unknownTestOwnerRows']==(2 if count==11 else 1) and (proof['incompleteSourcePrograms']==1 and proof['metadataOnlyPhysical']==2 if count==11 else proof['sqlImportNegativeVectors']==3) and proof['candidateOwnersNotAccepted'] is True,'exact independent one-Source whole-codec proof')
        new={(c['classname'],c['name']) for c in p['cases']};require(len(new)==count and not new&cases and p['singleSession'] is True and p['crcMismatch']==0 and p['metadataClasses']==(['dev/codex/schubert/nk/api/bootstrap/ApiProcessMain$ConfigurationLoad','dev/codex/schubert/nk/api/bootstrap/ApiProcessMain$Startup'] if count==11 else []),'actual distinct new cases/single current exec');cases.update(new)
        for name,u in p['fullSourceUnits'].items():
            require(name not in units and u['physical']==p['completeSourceUnitClosure'][name] and u['four100'] is (count==1) and u['branchNaturallyZero'] is False and u['threeCounter100'] is (count==1),'new complete nonempty four100 scope')
            units[name]=dict(post=folder,postSha256=pin,physical=u['physical'],counters=u['totals'],four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
        for path,owned in p['owners'].items():
            require(hashes[path]==owned['sha256'] and all(owned[k]==v for k,v in canonical(path,logical).items()),'canonical row/UNKNOWN exact owner and byte')
            require(path not in result['owners'] or result['owners'][path]==owned,'old shared owners unchanged');result['owners'][path]=owned
        for n in p['metadataClasses']:
            require(n not in result['metadataClasses'] and not any(m['hasCode'] for m in p['sourcePhysicalInventory'][n]['methods']),'new exact NoCode interface only')
            result['metadataClasses'][n]=dict(kind='NO_CODE',sha256=p['physicalClasses'][n],postSha256=pin)
        result['originalPostReferences'].append(dict(name=folder,sha256=pin,tests=count,suites=p['suites'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=('ORIGINAL_API_STATIC_PORT11_FULL_PHYSICAL_MAIN_COVERAGE_INCOMPLETE_NATIVE_HOLD' if count==11 else 'ORIGINAL_REQUIRED_COLUMN1_FULL_SOURCE_FOUR100_NO_DATABASE')))
    physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};meta=result['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'every whole Source physical closure disjoint')
    incomplete={n for n,u in units.items() if not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly'])}
    require(len(incomplete)==old['incompleteSourcePrograms']+1==6 and len({n for name in incomplete for n in units[name]['physical']})==10,'actual incomplete partition, never hide unexecuted owned overload')
    result.update(metadataPhysical=len(meta),incompleteSourcePrograms=len(incomplete),invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+2,totalProductExecs=old['totalProductExecs']+2,totalMethodExecutions=old['totalMethodExecutions']+12,uniqueProductMethodDelta=12,newTestIds=12,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len({n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']}),ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()))
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['four100SourcePrograms'],len(four),result['four100ExecutablePhysical'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'])==(1760,207,362,484,463,197,303,292,85,86,1868),'exact batch12/Source2 execution and four100 counts')
    require(result['metadataPhysical']==21 and result['metadataSourcePrograms']==6 and all(result['metadataClasses'][n]==v for n,v in old['metadataClasses'].items()),'all old metadata retained plus one explicit NoCode interface, not a new standalone metadata Source')
    require(result['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':277,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':204,'UNKNOWN':114},'two baseline/three UNKNOWN added, no inferred owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','fullSourceUnits','owners','originalPostReferences','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','ownerStatusCounts','unknownOwnerPaths','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','metadataClasses','metadataPhysical'}
    require(all(json.dumps(result[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items()),'all old353/domain/history/cost/metadata/formal preserved')
    for v in [old,prior,*witnesses]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
