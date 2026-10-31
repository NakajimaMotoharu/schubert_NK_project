"""One new parser Source and one natural-B0 enum replacement, mixed original/quality cases."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg16430_maintenance_stop_parser_eight_pt import SOURCE,NAME,ENUM,FIXTURE,FIXTURE_SHA
PREV=('PG16420-current2189-process-scope-registry-v1','4346e90455e1497c5317a5388776ef8a8e519fc25262d114b79bec2e0936cbad')
PREV_POST=('PG16423-current2189-process-scope-registry-post-v2','818c5c85144b2729fbc90dd4230729bd0c8113dfcacd5eb7b5d23e58939d92c9')
POST=('PG16432-maintenance-stop-parser-eight-post-v1','db29d2f25d7947d79da7ec819066cb0a6403041d8f01ad4927b57a9661f24851')
INDEPENDENT=('PG16434-maintenance-stop-parser-eight-independent-v1','31c0c2fc3c515b58ec28bf31fb56ba79ce3c70dc0f660a49a077d864d122d773')
OUT=data.BASE/'PG16436-current2197-maintenance-parser-registry-v1'
SCOPE='ORIGINAL_MSTOP7_NEW_LITERAL_ORDER1_ONE_NEW_SOURCE_ENUM_NATURAL_B0_NO_EXEC_UNION'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(30,9),'qualified chain')
    require((p['tests'],p['suites'],p['newTestIds'],p['originalOrdinaryMethods'],p['newQualityFixtureMethods'])==(8,2,1,7,1) and p['mixedOriginalAndNewQualityFixture'] is True and p['syntheticStateFieldsOnly'] is True,'mixed original seven/new quality one')
    result=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==8 and not added&before and all(v['result']=='PASS' for v in p['cases']),'eight distinct new current cases')
    require(set(p['fullSourceUnits'])=={NAME,ENUM} and NAME not in old['fullSourceUnits'] and ENUM in old['fullSourceUnits'] and ENUM not in old['qualificationReplacedUnitHistory'] and p['metadataClasses']==[],'one new Source/one existing enum')
    previous=old['fullSourceUnits'][ENUM];enum=p['fullSourceUnits'][ENUM]
    require(previous['physical']==enum['physical']==[ENUM] and not previous['four100'] and not previous['branchNaturallyZero'] and enum['branchNaturallyZero'] is enum['threeCounter100'] is True,'old partial enum now natural complete')
    for kind in enum['totals']:
        a,b=previous['counters'][kind],enum['totals'][kind];require(a['covered']+a['missed']==b['covered'] and b['missed']==0,'same full enum denominator')
    result['qualificationReplacedUnitHistory'][ENUM]=copy.deepcopy(previous)
    for name,unit in p['fullSourceUnits'].items():
        result['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),counters=copy.deepcopy(unit['totals']),four100=unit['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=unit['branchNaturallyZero'] and unit['threeCounter100'])
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        if path in old['owners']:require(old['owners'][path]==row,'existing owner unchanged')
        else:result['owners'][path]=copy.deepcopy(row)
    path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MaintenanceStopSnapshotTest.java';require(path not in result['owners'],'new ordinary Test owner')
    result['owners'][path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    result['valueFixtureQualificationReferences'].append(dict(post=list(POST),independentPost=list(INDEPENDENT),source=SOURCE,fixture=str(FIXTURE.relative_to(data.ROOT)),fixtureSha256=FIXTURE_SHA,tests=1,newUniqueMethods=1,necessaryRepeatedMethods=0,normalOrdinaryTestSourceDomain=False,mixedOriginalOrdinaryMethods=7,wholeSourcesReplaced=[ENUM],newWholeSources=[NAME],countedInOriginalExecs=True,coverageExecUnion=False))
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=8,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    names=before|added;units=result['fullSourceUnits'];physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural=[u for u in units.values() if u['branchNaturallyZero']]
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'nonoverlap full physical')
    updates=dict(previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),tests=len(names),suites=len({c for c,n in names}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+8,uniqueProductMethodDelta=8,newTestIds=1,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-result['metadataClasses'].keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-result['metadataClasses'].keys()),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),naturalZeroBranchSourcePrograms=len(natural),naturalZeroBranchPhysical=sum(len(u['physical']) for u in natural),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_MIXED_ORIGINAL_AND_NEW_QUALITY_FIXTURE_NO_EXEC_UNION')
    result.update(updates,invocation=invocation)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(len(added&ordinary)==7 and len(added-ordinary)==1 and len(names&ordinary)==2178 and len(names-ordinary)==19,'ordinary seven/quality one never conflated')
    decl.update(ordinaryCaseReferences=2178,ordinaryWithoutCurrentCaseReference=3608,existingQualityFixtureCases=19);result['currentOrdinaryTestDeclarationReference']=decl
    require((result['tests'],result['suites'],result['measuredSourcePrograms'],result['measuredPhysical'],result['executablePhysical'],result['metadataPhysical'],result['four100SourcePrograms'],result['four100Physical'],result['four100ExecutablePhysical'],result['naturalZeroBranchSourcePrograms'],result['naturalZeroBranchPhysical'],result['incompleteSourcePrograms'],result['totalProductExecs'],result['totalMethodExecutions'])==(2197,301,492,723,656,67,265,390,375,178,193,43,139,2329),'derived exact counts')
    changed=set(updates)|{'invocation','fullSourceUnits','qualificationReplacedUnitHistory','owners','originalPostReferences','currentOrdinaryTestDeclarationReference','valueFixtureQualificationReferences'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and all(result['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items() if k!=ENUM) and all(result['qualificationReplacedUnitHistory'][k]==v for k,v in old['qualificationReplacedUnitHistory'].items()) and result['valueFixtureQualificationReferences'][:-1]==old['valueFixtureQualificationReferences'] and all(result['owners'][k]==v for k,v in old['owners'].items()),'all old proof/owner/cost/formal preserved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
