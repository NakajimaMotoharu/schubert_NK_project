"""Four original public-launch cases plus one independent framing fixture, one full Source/two physical."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16182-current2144-backup-values-registry-v1','11c34b85628be56cb0365f3889a747953e5540746b3484014650752de9f0597e')
PREV_POST=('PG16184-current2144-backup-values-registry-post-v1','7fc8f6fbc94faafda0a9211d3a4c5e2571f57240ca1690a3426d2ad146e2f6e0')
POST=('PG16218-public-launch-five-post-v1','e61aea9c4b13c891c619e0686c3ed0ca37eebfd8e41be3c31310b0b57b37ca51')
INDEPENDENT=('PG16220-public-launch-five-independent-v1','15e9933f119867c5c5cb3016723a3f957e0e5eed9f0a31c029edb15c599cd7de')
NAME='dev/codex/schubert/nk/batch/file/StartupLaunchRecord'
OUT=data.BASE/'PG16222-current2149-public-launch-registry-v1'
SCOPE='ORIGINAL_PUBLIC_LAUNCH4_PLUS_INDEPENDENT_FRAMING1_ONE_SOURCE_ONE_NOCODE_NOT_AUTHORITY'

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):
    return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT)]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q))
            and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34
            and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(26,6),'qualified chain')
    require((p['tests'],p['suites'])==(5,2) and p['singleSession'] is True and p['crcMismatch']==0
            and p['strictFour100GateExit']==0 and p['actualBackupOrArchiveOperations']==0
            and p['actualCredentialFileValuesRead'] is p['rootMainInvoked'] is p['oldCoverageTransferred'] is False,'pure original guards, no Backup acceptance')
    require(set(p['fullSourceUnits'])=={NAME} and NAME not in old['fullSourceUnits'],'new measured Source')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==5 and not added&before and all(v['result']=='PASS' for v in p['cases']),'four original and one new quality case')
    unit=p['fullSourceUnits'][NAME];meta={NAME+'$DigestFactory'}
    require(set(unit['physical'])=={NAME,*meta} and set(p['metadataClasses'])==meta and unit['four100'] is True,'all2physical with1genuine NoCode')
    for name in meta:
        inv=p['sourcePhysicalInventory'][name];require(inv['flags']==1536 and len(inv['methods'])==1
                and inv['methods'][0]['hasCode'] is False and name not in result['metadataClasses'],'no Code reclassification')
        result['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    result['fullSourceUnits'][NAME]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),
        counters=copy.deepcopy(unit['totals']),four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    new_owners=copy.deepcopy(p['owners'])
    for simple in ('StartupLaunchRecordTest',):
        path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/'+simple+'.java'
        new_owners[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,row in new_owners.items():
        require(row['sha256']==data.sha((data.ROOT/path).read_bytes()) and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical roles')
        require(path not in result['owners'] or result['owners'][path]==row,'old role preservation');result['owners'][path]=row
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=5,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']}
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'disjoint entire Source closures')
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),
        cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),
        originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+5,
        uniqueProductMethodDelta=5,newTestIds=1,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),
        executablePhysical=len(physical-result['metadataClasses'].keys()),metadataPhysical=len(result['metadataClasses']),
        incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),
        ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),
        unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),
        lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    four=[u for u in units.values() if u['four100']]
    four_physical={n for u in four for n in u['physical']}
    updates.update(four100SourcePrograms=len(four),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-result['metadataClasses'].keys()))
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json'])
    ordinary={(v['className'],v['method']) for v in bindings}
    require(len(added&ordinary)==4 and len(added-ordinary)==1 and len(names&ordinary)==2131 and len(names-ordinary)==18,'ordinary new4 and quality new1 kept separate')
    decl.update(ordinaryCaseReferences=2131,ordinaryWithoutCurrentCaseReference=3655,existingQualityFixtureCases=18);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],len(units),len(physical),result['executablePhysical'],result['metadataPhysical'],
             result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'])==(2149,291,479,667,625,42,38,131,2281),'derived exact domains')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=394,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229,UNKNOWN=171),'one baseline Main/one UNKNOWN original Test; quality fixture outside source owner domain')
    changed=set(updates)|{'invocation','fullSourceUnits','metadataClasses','owners','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed)
            and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items())
            and all(result['metadataClasses'][k]==v for k,v in old['metadataClasses'].items())
            and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old scopes/counters/owners/history/cost preserved')
    for v in (old,prior,p,q):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result)
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
