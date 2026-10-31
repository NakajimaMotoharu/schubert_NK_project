"""Independent scope-only22 reconstruction from exact original XML and ordinary Source bindings."""
import collections
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16932-current2493-original-start-client-registry-v1','17cdab3bd42a1a08320df62bfc6d05bcde98e0abb65853ab1cb38712cb0dfbd4')
PREV_POST=('PG16934-current2493-original-start-client-registry-post-v1','62c45e6c7be2545c393601f244f82d43d70af2832c1b8f1c81fc81e79c3df14e')
POST=('PG16944-root-memory-truth-deadline-uid-three-post-v1','da036acf4f317615e7be597eb269ee9165feeb51e92022ef41b960709bf82205')
INDEPENDENT=('PG16946-root-memory-truth-deadline-uid-three-independent-v1','ab5fd221fcd2f5e324a6ff03f406173f57cae6ec7f0da4486c51dab55b6c0825')
SCOPE='SUPPLEMENTAL_ORIGINAL_ROOT_MEMORY_TRUTH_DEADLINE_UID3_EXISTING_SOURCE_NO_NATIVE_OR_COUNTER_UNION'
PIN='8f3e4e94b231f47165d6c74db933b7ef64f3928f84344dea69bcf3c8bc3c5708'
OUT=data.BASE/'PG16950-current2496-root-memory-truth-deadline-uid-registry-post-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG16948-current2496-root-memory-truth-deadline-uid-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(58,3),'actual independent chain')
    actual=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/name).read_bytes();require(data.sha(blob)==pin,'original copied XML')
        root=ET.fromstring(blob);require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'all FES0')
        for c in root.findall('testcase'):require(not list(c),'all actual PASS');actual.append((c.get('classname'),c.get('name')))
    added=set(actual);before={(v['classname'],v['name']) for v in old['cases']};names=before|added
    require(len(actual)==len(added)==3 and len({c for c,n in added})==3 and not added&before,'22 unique original methods from four whole suites')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and (q['newSourcePrograms'],q['newPhysicalClasses'],q['targetSourceUnitsMeasured'],q['targetPhysicalClassesMeasured'])==(0,0,1,8) and q['existingSourceProofMustBeRetained'] is True and p['actualGetentOrSystemctlInvoked'] is False and p['actualProcRead'] is False,'three existing Source proofs, no Source/native promotion')
    expected=copy.deepcopy(old)
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=len(actual),newTestIds=0,sourceProgramDelta=0,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    for k,d in dict(tests=len(actual),suites=len({c for c,n in added}),originalExecs=1,totalProductExecs=1,totalMethodExecutions=len(actual)).items():expected[k]=old[k]+d
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=len(actual),suites=len({c for c,n in added}),execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=len(actual),newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    decl=expected['currentOrdinaryTestDeclarationReference'];inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    selected_rows=[v for v in bindings if (v['className'],v['method']) in added];test_paths={v['path'] for v in selected_rows}
    require(len(selected_rows)==3 and len(test_paths)==3 and added<=ordinary and len(names&ordinary)==2477 and len(ordinary-names)==3309 and len(names-ordinary)==19,'exact ordinary binding and quality19 domains')
    for row in selected_rows:require(data.sha((data.ROOT/row['path']).read_bytes())==row['sourceSha256'],'current actual Test source')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in sorted(test_paths|set(p['owners'])):
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(row==old['owners'][path],'old exact owner pair')
        else:expected['owners'][path]=row
    expected['ownerStatusCounts']=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values()));expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    decl.update(ordinaryCaseReferences=2477,ordinaryWithoutCurrentCaseReference=3309,existingQualityFixtureCases=19)
    def contract(v):require(wire(v)==wire(expected),'complete independent object; Source/counter/cost/history unchanged')
    contract(m)
    require((m['tests'],m['suites'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['totalProductExecs'],m['totalMethodExecutions'])==(2496,358,529,850,282,426,170,2628),'actual domain totals')
    labels=[]
    vectors=[('tests',0),('suites',0),('originalExecs',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('uniqueProductMethodDelta',0),('newTestIds',True),('sourceProgramDelta',1),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',old['cases']),('fullSourceUnits',{}),('metadataClasses',{}),('owners',old['owners']),('ownerStatusCounts',old['ownerStatusCounts']),('additionalScopeReferences',old['additionalScopeReferences']),('qualificationReplacedUnitHistory',None),('jointQualificationReplacedUnitHistory',None),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('originalPostReferences',old['originalPostReferences'])]
    require(len(vectors)==30,'30 distinct top-level contracts')
    for k,v in vectors:
        require(wire(m[k])!=wire(v),'nondegenerate '+k);bad=copy.deepcopy(m);bad[k]=v
        try:contract(bad)
        except ValueError:labels.append(k)
        else:raise ValueError('wrong supplemental object accepted '+k)
    for k,v in [('ordinaryCaseReferences',0),('ordinaryWithoutCurrentCaseReference',0),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][k]=v
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+k)
        else:raise ValueError('wrong ordinary domain accepted')
    profile=[]
    bad=copy.deepcopy(m);bad['originalPostReferences'][-1]['scope']='OLD_SCHEMA_SCOPE'
    try:contract(bad)
    except ValueError:profile.append('stale-scope')
    else:raise ValueError('stale scope accepted')
    bad=copy.deepcopy(m)
    for path in test_paths:bad['owners'].pop(path,None)
    try:contract(bad)
    except ValueError:profile.append('missing-current-Test-owner')
    else:raise ValueError('missing Test owners accepted')
    bad=copy.deepcopy(m);bad['fullSourceUnits']['dev/codex/schubert/nk/batch/platform/RootStartupContext']['four100']=True
    try:contract(bad)
    except ValueError:profile.append('old-Source-proof-promoted')
    else:raise ValueError('old Source proof overwritten')
    summary={k:m[k] for k in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,profileNegativeVectors=len(profile),profileNegativeLabels=profile,newUniqueMethods=len(actual),newSourcePrograms=0,newPhysicalClasses=0,newMetadataPhysical=0,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
