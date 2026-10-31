"""Independent mixed-case registry, new whole parser and old enum proof retained in history."""
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg16436_current2197_maintenance_parser_registry import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,NAME,ENUM,FIXTURE,FIXTURE_SHA,SCOPE,read,require
PIN='3b65e2d1c169bf499c92e096758910b6b8bd611bf39d95586543ded0b7286081'
OUT=data.BASE/'PG16438-current2197-maintenance-parser-registry-post-v1'
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG16436-current2197-maintenance-parser-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(30,9),'qualified current chain')
    actual=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/name).read_bytes();require(data.sha(blob)==pin,'copied original XML');xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in xml.findall('testcase'):require(not list(case),'no hidden nonpass');actual.append((case.get('classname'),case.get('name')))
    added=set(actual);before={(v['classname'],v['name']) for v in old['cases']};names=before|added
    require(len(actual)==len(added)==8 and not added&before,'eight new current unique methods')
    expected=copy.deepcopy(old);expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=8,newTestIds=1,sourceProgramDelta=1,lastUpdateKind='CURRENT_SOURCE_MIXED_ORIGINAL_AND_NEW_QUALITY_FIXTURE_NO_EXEC_UNION')
    for key,delta in [('tests',8),('suites',2),('originalExecs',1),('totalProductExecs',1),('totalMethodExecutions',8),('measuredSourcePrograms',1),('measuredPhysical',1),('executablePhysical',1),('four100SourcePrograms',1),('four100Physical',1),('four100ExecutablePhysical',1),('incompleteSourcePrograms',-1),('naturalZeroBranchSourcePrograms',1),('naturalZeroBranchPhysical',1)]:expected[key]=old[key]+delta
    require(set(p['fullSourceUnits'])=={NAME,ENUM} and NAME not in old['fullSourceUnits'] and ENUM in old['fullSourceUnits'] and ENUM not in old['qualificationReplacedUnitHistory'] and p['metadataClasses']==[],'two units/one new/one replacement')
    expected['qualificationReplacedUnitHistory'][ENUM]=copy.deepcopy(old['fullSourceUnits'][ENUM])
    for n in [NAME,ENUM]:
        unit=p['fullSourceUnits'][n];require(unit['physical']==[n],'whole one physical Source')
        expected['fullSourceUnits'][n]=dict(post=POST[0],postSha256=POST[1],physical=[n],counters=copy.deepcopy(unit['totals']),four100=n==NAME,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=n==ENUM)
    require(p['fullSourceUnits'][NAME]['four100'] is True and p['fullSourceUnits'][ENUM]['branchNaturallyZero'] is p['fullSourceUnits'][ENUM]['threeCounter100'] is True,'full parser/natural enum')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical Main owner')
        if path in old['owners']:require(old['owners'][path]==row,'existing owner')
        else:expected['owners'][path]=copy.deepcopy(row)
    path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MaintenanceStopSnapshotTest.java'
    require(path not in old['owners'],'new ordinary Test owner');expected['owners'][path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    expected['ownerStatusCounts']={'BASELINE_LOGICAL_REFERENCE':406,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':229,'UNKNOWN':181};expected['unknownOwnerPaths']=181
    expected['valueFixtureQualificationReferences'].append(dict(post=list(POST),independentPost=list(INDEPENDENT),source=SOURCE,fixture=str(FIXTURE.relative_to(data.ROOT)),fixtureSha256=FIXTURE_SHA,tests=1,newUniqueMethods=1,necessaryRepeatedMethods=0,normalOrdinaryTestSourceDomain=False,mixedOriginalOrdinaryMethods=7,wholeSourcesReplaced=[ENUM],newWholeSources=[NAME],countedInOriginalExecs=True,coverageExecUnion=False))
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=8,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    decl=expected['currentOrdinaryTestDeclarationReference'];inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(len(added&ordinary)==7 and len(added-ordinary)==1 and len(names&ordinary)==2178 and len(names-ordinary)==19,'ordinary/quality exact distinct domains')
    decl.update(ordinaryCaseReferences=2178,ordinaryWithoutCurrentCaseReference=3608,existingQualityFixtureCases=19)
    require((expected['tests'],expected['suites'],expected['measuredSourcePrograms'],expected['measuredPhysical'],expected['four100SourcePrograms'],expected['naturalZeroBranchSourcePrograms'],expected['incompleteSourcePrograms'],expected['totalProductExecs'],expected['totalMethodExecutions'])==(2197,301,492,723,265,178,43,139,2329),'independent exact counts')
    def contract(value):require(wire(value)==wire(expected),'whole registry independently reconstructed including old costs/acceptance/disclosures')
    contract(m);labels=[]
    vectors=[('tests',0),('suites',0),('originalExecs',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('uniqueProductMethodDelta',0),('newTestIds',False),('sourceProgramDelta',0),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',old['cases']),('fullSourceUnits',old['fullSourceUnits']),('metadataClasses',{}),('owners',old['owners']),('valueFixtureQualificationReferences',[]),('postDisclosureCorrections',{}),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('originalPostReferences',old['originalPostReferences'])]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false registry '+key)
    for key,value in [('ordinaryCaseReferences',2171),('ordinaryWithoutCurrentCaseReference',3615),('existingQualityFixtureCases',18),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('false ordinary/quality '+key)
    require(len(labels)==34,'finite thirty-four metadata negatives')
    summary={key:m[key] for key in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,newUniqueMethods=8,newSourcePrograms=1,newPhysicalClasses=1,newMetadataPhysical=0,sourceProofsReplaced=1,originalOrdinaryMethodsAdded=7,newQualityFixtureMethodsAdded=1,previousSourceProofsNotReplaced=False,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
