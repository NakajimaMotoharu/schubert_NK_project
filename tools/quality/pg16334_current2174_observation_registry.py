"""One original synthetic wrapper case and incomplete whole Root preflight Source; no Code exclusion."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16318-current2173-bootstrap-enum-registry-v1','7c618826ff3db2244157c3b1df5fe0c7af7790db3e7d6c45176fbf0b7549e6be')
PREV_POST=('PG16320-current2173-bootstrap-enum-registry-post-v1','fee80f8dc0c4c09a400e3412e64cc66eca3514a70ae25651c2f682e5cffe12c0')
POST=('PG16330-current-observation-one-post-v1','b852ea2d21812f14ce578dd4bad4936d23f33e2c8d1c1e8312bb6f07a5f1dc80')
INDEPENDENT=('PG16332-current-observation-one-independent-v1','5b562b0c1a00814c6841f4c73e139507821f0f404370a54e6dcd510ec857038c')
NAME='dev/codex/schubert/nk/batch/file/RootCurrentPermitPreflight'
OUT=data.BASE/'PG16334-current2174-observation-registry-v1'
SCOPE='ORIGINAL_CURRENT_OBSERVATION1_SYNTHETIC_WRAPPER_WHOLE_ROOT_SOURCE_INCOMPLETE'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q)) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34
            and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'],q['wholeSourceIncompleteCount'])==(26,2,1),'qualified chain')
    require((p['tests'],p['suites'])==(1,1) and p['singleSession'] is True and p['crcMismatch']==0 and p['strictFour100GateExit']==1
            and p['syntheticPublicBindingValuesOnly'] is p['syntheticPermitValueOnly'] is True and p['actualPermitIssueSignPublishOrRetire'] is False and p['actualFilesOpenedByProduct'] is p['rootMainInvoked'] is p['oldCoverageTransferred'] is False,'pure labels, no whole manager acceptance')
    require(set(p['fullSourceUnits'])=={NAME} and not {NAME}&old['fullSourceUnits'].keys(),'two newly measured Sources')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==1 and not added&before and all(v['result']=='PASS' for v in p['cases']),'one original case')
    for name in p['metadataClasses']:
        inv=p['sourcePhysicalInventory'][name]
        require(inv['flags']==1536 and inv['methods'] and not any(v['hasCode'] for v in inv['methods']) and name not in result['metadataClasses'],'genuine NoCode interfaces only')
        result['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    for name,unit in p['fullSourceUnits'].items():
        natural=unit['branchNaturallyZero'] and unit['threeCounter100']
        require(not unit['four100'] and natural is False,'honest natural/partial distinction')
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),counters=copy.deepcopy(unit['totals']),
            four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=natural)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    new_owners=copy.deepcopy(p['owners']);path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CurrentObservationValueTest.java'
    new_owners[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,row in new_owners.items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical role, preserve UNKNOWN')
        require(path not in result['owners'],'new owner rows');result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=1,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'nonoverlap whole physical closures')
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),
        originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+1,uniqueProductMethodDelta=1,newTestIds=0,sourceProgramDelta=1,
        measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-result['metadataClasses'].keys()),metadataPhysical=len(result['metadataClasses']),
        incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),
        naturalZeroBranchSourcePrograms=old['naturalZeroBranchSourcePrograms'],naturalZeroBranchPhysical=old['naturalZeroBranchPhysical'],
        ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),
        lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    four=[u for u in units.values() if u['four100']];four_physical={n for u in four for n in u['physical']}
    updates.update(four100SourcePrograms=len(four),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-result['metadataClasses'].keys()))
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2156 and len(names-ordinary)==18,'one normal original, quality18 separate')
    decl.update(ordinaryCaseReferences=2156,ordinaryWithoutCurrentCaseReference=3630,existingQualityFixtureCases=18);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['metadataPhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'])==(2174,296,485,682,637,45,40,136,2306),'derived exact counts')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=399,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229,UNKNOWN=177),'baseline AES plus UNKNOWN manager/Test')
    changed=set(updates)|{'invocation','fullSourceUnits','metadataClasses','owners','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items())
            and all(result['metadataClasses'][k]==v for k,v in old['metadataClasses'].items()) and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old scopes/history/cost/acceptance preserved')
    for v in (old,prior,p,q):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
