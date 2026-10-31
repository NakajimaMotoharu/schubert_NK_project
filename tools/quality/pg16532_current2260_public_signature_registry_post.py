"""Independent public RFC verification8 addition, complete Code/NoCode partitions and old proofs retained."""
import copy
import json
import xml.etree.ElementTree as ET
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg16530_current2260_public_signature_registry import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,SCOPE,read,require
PIN='7ece9543a6701d06707a9b5d53b572d440403ab9948645652391a32dc26bffb3'
OUT=data.BASE/'PG16532-current2260-public-signature-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG16530-current2260-public-signature-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(33,9),'independent chain')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML pin');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'no nonpass')
        for node in root.findall('testcase'):require(not list(node),'PASS');actual.append((node.get('classname'),node.get('name')))
    before={(v['classname'],v['name']) for v in old['cases']};added=set(actual);require(len(actual)==len(added)==8 and not added&before,'two fresh current methods')
    names=before|added;expected=copy.deepcopy(old)
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=8,newTestIds=0,sourceProgramDelta=1,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_BROADER_OLD_PROOFS_RETAINED_PARTIAL_DISCLOSED')
    deltas=dict(tests=8,suites=1,originalExecs=1,totalProductExecs=1,totalMethodExecutions=8,measuredSourcePrograms=1,measuredPhysical=3,executablePhysical=2,metadataPhysical=1,incompleteSourcePrograms=0,naturalZeroBranchSourcePrograms=0,naturalZeroBranchPhysical=0,four100SourcePrograms=1,four100Physical=3,four100ExecutablePhysical=2)
    for key,delta in deltas.items():expected[key]=old[key]+delta
    new={n for n in p['fullSourceUnits'] if n not in old['fullSourceUnits']}
    require(new=={'dev/codex/schubert/nk/bootstrap/ReleaseSignatureVerifier'},'only three new complete Sources')
    for name in new:
        u=p['fullSourceUnits'][name]
        expected['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    for name in p['metadataClasses']:
        require(name not in old['metadataClasses'],'new noCode names');expected['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=8,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=list(p['owners'])+['src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/ReleaseSignatureVerifierTest.java']
    for path in paths:
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owner')
        else:expected['owners'][path]=row
    require(len(expected['owners'])-len(old['owners'])==2,'three Source and two Test owner references')
    expected['ownerStatusCounts']=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values()))
    expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    decl=expected['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2241 and len(ordinary-names)==3545 and len(names-ordinary)==19,'independent ordinary counts')
    decl.update(ordinaryCaseReferences=2241,ordinaryWithoutCurrentCaseReference=3545,existingQualityFixtureCases=19)
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
    summary={k:m[k] for k in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=34,negativeLabels=labels,newUniqueMethods=8,newSourcePrograms=1,newPhysicalClasses=3,newMetadataPhysical=1,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
