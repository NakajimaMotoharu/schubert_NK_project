"""Independent one enum case, natural-B0 AES and incomplete whole manager Source, all prior histories preserved."""
import copy
import json
import xml.etree.ElementTree as ET
from collections import Counter
from trace_owner_join import canonical
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg16318_current2173_bootstrap_enum_registry import SOURCE, PREV, PREV_POST, POST, INDEPENDENT, AES, MANAGER, SCOPE, read, require

PIN='7c618826ff3db2244157c3b1df5fe0c7af7790db3e7d6c45176fbf0b7549e6be'
OUT=data.BASE/'PG16320-current2173-bootstrap-enum-registry-post-v1'

def wire(value):
    return json.dumps(value,sort_keys=True)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in (PREV,PREV_POST,POST,INDEPENDENT,('PG16318-current2173-bootstrap-enum-registry-v1',PIN))]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in (old,prior,p,q,m))
            and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1]
            and (q['semanticNegativeVectors'],q['independentOracleVectors'],q['metadataPhysicalClasses'])==(26,12,3),'qualified chain')
    actual=[]
    for filename,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(blob)==pin,'exact copied originalXML')
        xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ('failures','errors','skipped')),'no failure/skip')
        for node in xml.findall('testcase'):
            require(not list(node),'actual case no nonpass');actual.append((node.get('classname'),node.get('name')))
    old_cases={(v['classname'],v['name']) for v in old['cases']};added=set(actual)
    require(len(actual)==len(added)==1 and not added&old_cases,'eight unique new original methods')
    names=old_cases|added;expected=copy.deepcopy(old)
    expected['invocation']=m['invocation'];expected['previousUniqueRegistryReference']=list(PREV);expected['previousRegistryPostReference']=list(PREV_POST)
    expected['cases']=[dict(classname=c,name=n) for c,n in sorted(names)];expected['suiteNames']=sorted({c for c,n in names})
    for key,delta in [('tests',1),('suites',1),('originalExecs',1),('totalProductExecs',1),('totalMethodExecutions',1),('measuredSourcePrograms',2),('measuredPhysical',8),('executablePhysical',5),('metadataPhysical',3),('incompleteSourcePrograms',1),('four100SourcePrograms',0),('four100Physical',0),('four100ExecutablePhysical',0)]:expected[key]=old[key]+delta
    expected['naturalZeroBranchSourcePrograms']=old['naturalZeroBranchSourcePrograms']+1
    expected['naturalZeroBranchPhysical']=old['naturalZeroBranchPhysical']+1
    expected.update(uniqueProductMethodDelta=1,newTestIds=0,sourceProgramDelta=2,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=1,suites=1,execSha256=p['execSha256'],
        sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    decl=expected['currentOrdinaryTestDeclarationReference'];inv=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    declarations=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inv['files']['exact-ordinary-bindings.json'])
    ordinary={(v['className'],v['method']) for v in declarations}
    require(added<=ordinary and len(names&ordinary)==2155 and len(names-ordinary)==18,'new original declarations, no fixture mixing')
    decl.update(ordinaryCaseReferences=len(names&ordinary),ordinaryWithoutCurrentCaseReference=len(ordinary-names),existingQualityFixtureCases=18)
    require((expected['tests'],expected['suites'],expected['totalProductExecs'],expected['totalMethodExecutions'],
             decl['ordinaryCaseReferences'],decl['ordinaryWithoutCurrentCaseReference'])==(2173,295,135,2305,2155,3631),'independently derived counts')
    require(not {AES,MANAGER}&old['fullSourceUnits'].keys() and p['strictFour100GateExit']==1
            and p['publicEnumLabelsAndSerializationSchemaOnly'] is True and p['actualBackupOrArchiveOperations']==0 and p['actualCredentialFileValuesRead'] is False,'new pure labels, no manager acceptance')
    require(set(p['fullSourceUnits'])=={AES,MANAGER},'two complete Source denominators')
    for name in (AES,MANAGER):
        unit=p['fullSourceUnits'][name]
        expected['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(unit['physical']),counters=copy.deepcopy(unit['totals']),
            four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=name==AES)
        require(unit['four100'] is False and (unit['branchNaturallyZero'] and unit['threeCounter100'])==(name==AES),'natural versus incomplete')
    meta={MANAGER+'$Budget',MANAGER+'$Factory',MANAGER+'$Session'}
    require(set(p['metadataClasses'])==meta and len(p['physicalClasses'])==8,'all physical including NoCode')
    for name in sorted(meta):
        inventory=p['sourcePhysicalInventory'][name]
        require(inventory['flags']==1536 and inventory['methods'] and not any(v['hasCode'] for v in inventory['methods']),'genuine abstract interfaces')
        expected['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    additions=copy.deepcopy(p['owners'])
    for simple in ('EnumValueCatalogCompatibilityTest',):
        path='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/file/'+simple+'.java'
        additions[path]=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
    for path,value in additions.items():
        require(path not in old['owners'],'exact four newly measured owner rows');expected['owners'][path]=value
    expected['ownerStatusCounts']=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values()))
    expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    require(expected['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=398,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229,UNKNOWN=176),'not inferred from changeOwner')
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
        summary=summary,metadataNegativeVectors=34,negativeLabels=negative,newUniqueMethods=1,newSourcePrograms=2,newPhysicalClasses=8,newMetadataPhysical=3,
        previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,
        currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,
        whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
