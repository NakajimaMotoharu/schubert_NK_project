"""Independent unknown4/current three added Sources; retain one old natural proof and all misses."""
import copy
import json
import xml.etree.ElementTree as ET
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg16702_current2356_parent_guard_registry import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,SCOPE,read,require
PIN='d5ad11a6daba111c78e448263e4990304e2868f938b9feabee9e82c638fb7893'
OUT=data.BASE/'PG16704-current2356-parent-guard-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG16702-current2356-parent-guard-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(44,1),'independent chain')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML pin');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'no nonpass')
        for node in root.findall('testcase'):require(not list(node),'PASS');actual.append((node.get('classname'),node.get('name')))
    before={(v['classname'],v['name']) for v in old['cases']};added=set(actual);require(len(actual)==len(added)==6 and not added&before,'33 fresh current original methods')
    names=before|added;expected=copy.deepcopy(old)
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=6,newTestIds=0,sourceProgramDelta=1,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_BROADER_OLD_PROOFS_RETAINED_PARTIAL_DISCLOSED')
    root='dev/codex/schubert/nk/bootstrap/'
    expected_new={root+'MaintenanceOwnerFrame'}
    fresh={n for n in p['fullSourceUnits'] if n not in old['fullSourceUnits']}
    four_names=set()
    natural_names=set()
    partial_names=expected_new-four_names-natural_names
    require(fresh==expected_new and (q['newSourcePrograms'],q['newPhysicalClasses'],q['metadataPhysicalClasses'])==(1,5,2),'independent declared closure, not copied deltas')
    physical={c for n in fresh for c in p['fullSourceUnits'][n]['physical']}
    meta=set(p['metadataClasses'])
    four_physical={c for n in four_names for c in p['fullSourceUnits'][n]['physical']}
    natural_physical={c for n in natural_names for c in p['fullSourceUnits'][n]['physical']}
    require(len(physical)==5 and len(meta)==2 and meta<=physical and len(four_physical)==0 and len(natural_physical)==0 and len(partial_names)==1 and len({c for c,n in actual})==1,'independent measured sets and actual XML suites')
    deltas=dict(tests=len(actual),suites=len({c for c,n in actual}),originalExecs=1,totalProductExecs=1,totalMethodExecutions=len(actual),measuredSourcePrograms=len(fresh),measuredPhysical=len(physical),executablePhysical=len(physical-meta),metadataPhysical=len(meta),incompleteSourcePrograms=len(partial_names),naturalZeroBranchSourcePrograms=len(natural_names),naturalZeroBranchPhysical=len(natural_physical),four100SourcePrograms=len(four_names),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-meta))
    for key,delta in deltas.items():expected[key]=old[key]+delta
    new={n for n in p['fullSourceUnits'] if n not in old['fullSourceUnits']}
    require(new==expected_new,'four current complete Source denominators')
    for name in new:
        u=p['fullSourceUnits'][name]
        expected['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=name in four_names,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    for name in p['metadataClasses']:
        require(name not in old['metadataClasses'],'new noCode names');expected['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=6,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=list(p['owners'])+json.loads("[\"src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/MaintenanceParentGuardTest.java\"]")
    for path in paths:
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owner')
        else:expected['owners'][path]=row
    require(len(expected['owners'])-len(old['owners'])==2,'four Source and six original Test owner references')
    expected['ownerStatusCounts']=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values()))
    expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    decl=expected['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2337 and len(ordinary-names)==3449 and len(names-ordinary)==19,'independent ordinary counts')
    decl.update(ordinaryCaseReferences=2337,ordinaryWithoutCurrentCaseReference=3449,existingQualityFixtureCases=19)
    def contract(v):require(wire(v)==wire(expected),'independent exact complete metadata/history/cost object')
    contract(m);labels=[]
    vectors=[('tests',0),('suites',0),('originalExecs',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('uniqueProductMethodDelta',0),('newTestIds',True),('sourceProgramDelta',0),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',old['cases']),('fullSourceUnits',old['fullSourceUnits']),('metadataClasses',{}),('owners',old['owners']),('ownerStatusCounts',old['ownerStatusCounts']),('postDisclosureCorrections',{}),('qualificationReplacedUnitHistory',{}),('jointQualificationReplacedUnitHistory',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('originalPostReferences',old['originalPostReferences'])]
    for key,value in vectors:
        require(wire(m[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false registry '+key)
    for key,value in [('ordinaryCaseReferences',0),('ordinaryWithoutCurrentCaseReference',0),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('false ordinary metadata')
    require(len(labels)==34,'34 independent metadata negatives')
    chain_labels=[]
    for key,value in [('semanticNegativeVectors',43),('independentOracleVectors',2)]:
        bad=dict(q);bad[key]=value
        require((bad['semanticNegativeVectors'],bad['independentOracleVectors'])!=(44,1),'old/wrong oracle chain rejected')
        chain_labels.append(key)
    summary={k:m[k] for k in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=34,negativeLabels=labels,chainNegativeVectors=len(chain_labels),chainNegativeLabels=chain_labels,newUniqueMethods=6,newSourcePrograms=1,newPhysicalClasses=5,newMetadataPhysical=2,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
