"""Independent scope-only22 reconstruction from exact original XML and ordinary Source bindings."""
import collections
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG16846-current2422-child-broker-caddy-registry-v1','953d9299af7bb5233dcd1f5b8b83bb7bdc83e4156191144da96777bd330243b3')
PREV_POST=('PG16849-current2422-child-broker-caddy-registry-post-v2','a5784777c0c8128576449a5099168d4fc5c380eeb662a9e3eaadc612aff9487f')
POST=('PG16860-child-parent-inspector-caddy-original-twelve-post-v1','e123dc5841bcb11dbadc3f877013c38a1bb98c6d9279843cc5ff2549236d71cc')
INDEPENDENT=('PG16862-child-parent-inspector-caddy-original-twelve-independent-v1','72c2f4a5526280e27c2b20c539e2aa14d14290aaa1a421e8494fc442f00dbcf6')
SCOPE='SUPPLEMENTAL_ORIGINAL_CHILD_PARENT_INSPECTOR_CADDY12_THREE_EXISTING_SOURCE_UNITS_NO_NATIVE_OR_COUNTER_UNION'
PIN='a93769619fd0f679ed33269e174934ddbedadd97d72dc1b8ecf3c738bf9d7cc1'
OUT=data.BASE/'PG16866-current2434-child-parent-inspector-caddy-registry-post-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG16864-current2434-child-parent-inspector-caddy-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(54,12),'actual independent chain')
    actual=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/name).read_bytes();require(data.sha(blob)==pin,'original copied XML')
        root=ET.fromstring(blob);require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'all FES0')
        for c in root.findall('testcase'):require(not list(c),'all actual PASS');actual.append((c.get('classname'),c.get('name')))
    added=set(actual);before={(v['classname'],v['name']) for v in old['cases']};names=before|added
    require(len(actual)==len(added)==12 and len({c for c,n in added})==3 and not added&before,'22 unique original methods from four whole suites')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and (q['newSourcePrograms'],q['newPhysicalClasses'],q['targetSourceUnitsMeasured'],q['targetPhysicalClassesMeasured'])==(0,0,3,17) and q['existingSourceProofMustBeRetained'] is True and p['actualGetentOrSystemctlInvoked'] is False and p['actualProcRead'] is False,'three existing Source proofs, no Source/native promotion')
    expected=copy.deepcopy(old)
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=len(actual),newTestIds=0,sourceProgramDelta=0,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    for k,d in dict(tests=len(actual),suites=len({c for c,n in added}),originalExecs=1,totalProductExecs=1,totalMethodExecutions=len(actual)).items():expected[k]=old[k]+d
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=len(actual),suites=len({c for c,n in added}),execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=len(actual),newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    decl=expected['currentOrdinaryTestDeclarationReference'];inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    selected_rows=[v for v in bindings if (v['className'],v['method']) in added];test_paths={v['path'] for v in selected_rows}
    require(len(selected_rows)==12 and len(test_paths)==3 and added<=ordinary and len(names&ordinary)==2415 and len(ordinary-names)==3371 and len(names-ordinary)==19,'exact ordinary binding and quality19 domains')
    for row in selected_rows:require(data.sha((data.ROOT/row['path']).read_bytes())==row['sourceSha256'],'current actual Test source')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in sorted(test_paths|set(p['owners'])):
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(row==old['owners'][path],'old exact owner pair')
        else:expected['owners'][path]=row
    expected['ownerStatusCounts']=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values()));expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    decl.update(ordinaryCaseReferences=2415,ordinaryWithoutCurrentCaseReference=3371,existingQualityFixtureCases=19)
    def contract(v):require(wire(v)==wire(expected),'complete independent object; Source/counter/cost/history unchanged')
    contract(m)
    require((m['tests'],m['suites'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['totalProductExecs'],m['totalMethodExecutions'])==(2434,346,527,839,282,426,165,2566),'actual domain totals')
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
    bad=copy.deepcopy(m);bad['fullSourceUnits']['dev/codex/schubert/nk/bootstrap/ChildStartupContext']['four100']=True
    try:contract(bad)
    except ValueError:profile.append('old-Source-proof-promoted')
    else:raise ValueError('old Source proof overwritten')
    summary={k:m[k] for k in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,profileNegativeVectors=len(profile),profileNegativeLabels=profile,newUniqueMethods=len(actual),newSourcePrograms=0,newPhysicalClasses=0,newMetadataPhysical=0,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
