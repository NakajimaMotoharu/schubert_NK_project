"""Independent original observation23 and whole parser Source; retain all old proof domains."""
import copy
import json
import xml.etree.ElementTree as ET
from collections import Counter
from trace_owner_join import canonical
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg16466_current2224_inspector_snapshot_registry import SOURCE, PREV, PREV_POST, POST, INDEPENDENT, SCOPE, read, require

PIN='1461c4715e3c1fd53ade29bae01ba03e64d44fecb93cff4f115814d2ecab1d94'
OUT=data.BASE/'PG16468-current2224-inspector-snapshot-registry-post-v1'

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT,('PG16466-current2224-inspector-snapshot-registry-v1',PIN))]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q,m))
            and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1]
            and (q['semanticNegativeVectors'],q['independentOracleVectors'],q['metadataPhysicalClasses'])==(31,13,0),'qualified chain')
    actual=[]
    for filename,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(blob)==pin,'exact copied originalXML')
        xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no failure/skip')
        for node in xml.findall('testcase'):
            require(not list(node),'actual case no nonpass');actual.append((node.get('classname'),node.get('name')))
    old_cases={(v['classname'],v['name']) for v in old['cases']};added=set(actual)
    require(len(actual)==len(added)==23 and not added&old_cases,'eight unique new original methods')
    names=old_cases|added;expected=copy.deepcopy(old)
    expected['invocation']=m['invocation'];expected['previousUniqueRegistryReference']=list(PREV);expected['previousRegistryPostReference']=list(PREV_POST)
    expected['cases']=[dict(classname=c,name=n) for c,n in sorted(names)];expected['suiteNames']=sorted({c for c,n in names})
    for key,delta in [('tests',23),('suites',3),('originalExecs',1),('totalProductExecs',1),('totalMethodExecutions',23),('measuredSourcePrograms',1),('measuredPhysical',2),('executablePhysical',2),('metadataPhysical',0),('incompleteSourcePrograms',0),('four100SourcePrograms',1),('four100Physical',2),('four100ExecutablePhysical',2)]:expected[key]=old[key]+delta
    expected['naturalZeroBranchSourcePrograms']=old['naturalZeroBranchSourcePrograms']
    expected['naturalZeroBranchPhysical']=old['naturalZeroBranchPhysical']
    expected.update(uniqueProductMethodDelta=23,newTestIds=0,sourceProgramDelta=1,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=23,suites=3,execSha256=p['execSha256'],
        sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    decl=expected['currentOrdinaryTestDeclarationReference'];inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    declarations=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json'])
    ordinary={(v['className'],v['method']) for v in declarations}
    require(added<=ordinary and len(names&ordinary)==2205 and len(names-ordinary)==19,'new original declarations, no fixture mixing')
    decl.update(ordinaryCaseReferences=len(names&ordinary),ordinaryWithoutCurrentCaseReference=len(ordinary-names),existingQualityFixtureCases=19)
    require((expected['tests'],expected['suites'],expected['totalProductExecs'],expected['totalMethodExecutions'],
             decl['ordinaryCaseReferences'],decl['ordinaryWithoutCurrentCaseReference'])==(2224,305,141,2356,2205,3581),'independently derived counts')
    name='dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot'
    require(set(p['fullSourceUnits'])=={name} and name not in old['fullSourceUnits'] and p['strictFour100GateExit']==0 and p['syntheticStateFieldsOnly'] is p['publicDigestOnly'] is p['cryptoOrKeyOperationsInvoked'] is True and p['actualSecretKeysLoaded'] is False and p['actualRootRecoveryOperations']==p['actualFailedCohortCollectionOperations']==0,'whole pure observation data not Root authority')
    unit=p['fullSourceUnits'][name]
    require(unit['physical']==[name,name+'$Target'] and unit['four100'] is True and unit['branchNaturallyZero'] is False and p['metadataClasses']==[],'two full executable physical classes')
    expected['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),counters=copy.deepcopy(unit['totals']),four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    additions=copy.deepcopy(p['owners'])
    for simple in ('InspectorUnitSnapshotTest','InspectorHeldStateContractTest','ArtemisUnitSnapshotTest'):
        path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/'+simple+'.java'
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path in ['src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt','src/deployment/systemd/artemis.service']:
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,value in additions.items():
        require(path not in old['owners'],'exact four newly measured owner rows');expected['owners'][path]=value
    expected['ownerStatusCounts']=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values()))
    expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    require(expected['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=415,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=230,UNKNOWN=185),'not inferred from changeOwner')
    def contract(value):
        require(wire(value)==wire(expected),'exact old/new independent whole object; no silent domain/history changes')
    contract(m);negative=[]
    vectors=[('tests',2136),('suites',286),('originalExecs',128),('totalProductExecs',129),('totalMethodExecutions',2268),
        ('totalRepeatedOriginalMethods',140),('uniqueProductMethodDelta',0),('newTestIds',True),('sourceProgramDelta',0),
        ('measuredSourcePrograms',477),('measuredPhysical',662),('four100SourcePrograms',258),('four100Physical',377),
        ('incompleteSourcePrograms',37),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),
        ('cases',old['cases']),('fullSourceUnits',old['fullSourceUnits']),('metadataClasses',{}),('owners',old['owners']),('ownerStatusCounts',old['ownerStatusCounts']),
        ('postDisclosureCorrections',{}),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),
        ('metadataPhysical',39),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),
        ('originalPostReferences',old['originalPostReferences'])]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:negative.append(key)
        else:raise ValueError('false registry accepted '+key)
    for key,value in [('ordinaryCaseReferences',2119),('ordinaryWithoutCurrentCaseReference',3667),('existingQualityFixtureCases',25),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:negative.append('ordinary-'+key)
        else:raise ValueError('false ordinary count')
    require(len(negative)==34,'finite34 negative vectors')
    summary=copy.deepcopy(prior['summary'])
    for key in summary:summary[key]=m[key]
    for v in (old,prior,p,q,m):verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,
        summary=summary,metadataNegativeVectors=34,negativeLabels=negative,newUniqueMethods=23,newSourcePrograms=1,newPhysicalClasses=2,newMetadataPhysical=0,
        previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,
        currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,
        whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
