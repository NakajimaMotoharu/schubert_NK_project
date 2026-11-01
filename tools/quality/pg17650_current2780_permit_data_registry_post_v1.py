"""Independent scope-only7 reconstruction from exact original XML and ordinary Source bindings."""
import collections
import copy
import json
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17628-current2774-checkpoint-public-provider-registry-v1','d3d5bd52d29fecf9b227ff98f8af753af1be71b21b49c8be6f06c68602a3e616')
PREV_POST=('PG17630-current2774-checkpoint-public-provider-registry-post-v1','499cb96aed7d848ae9c40d8933b241c51b8b50bdfa54cd503ad1b500fd99c07d')
POST=('PG17642-current-permit-data-six-post-v1','f59b1db5c4b23ed3981bad802ab621b9f90dce497ac030ce73d4a7892b87cfea')
INDEPENDENT=('PG17644-current-permit-data-six-independent-v1','d59a5f733907ca5badb4b3805a338f89209f2bfbea4f01d9c584d2af68bc840e')
SCOPE='SUPPLEMENTAL_ORIGINAL_CURRENT_PERMIT_DATA6_NO_REAL_PERMIT_ROOT_OR_IO_NO_COUNTER_UNION'
PIN='ffd247fe95c7560885b25d0eff356d673841c8d0959e153ba9dc35c7d3c0560a'
OUT=data.BASE/'PG17650-current2780-permit-data-registry-post-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG17648-current2780-permit-data-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(28,6),'actual independent chain')
    actual=[]
    for name,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/name).read_bytes();require(data.sha(blob)==pin,'original copied XML')
        root=ET.fromstring(blob);require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'all FES0')
        for c in root.findall('testcase'):require(not list(c),'all actual PASS');actual.append((c.get('classname'),c.get('name')))
    added=set(actual);before={(v['classname'],v['name']) for v in old['cases']};names=before|added
    require(len(actual)==len(added)==6 and len({c for c,n in added})==1 and not added&before,'seven unique original methods from one whole suite')
    require(set(p['fullSourceUnits'])<=old['fullSourceUnits'].keys() and (p['targetSourceUnits'],len(p['physicalClasses']))==(1,2) and p['syntheticPermitRecordConstructionOnly'] is p['nativeNamedReadNullGuardOnlyInvoked'] is p['syntheticRootAdmissionCallbackInvoked'] is True and p['actualPermitNamespaceLookups']==0 and p['actualRootOsAdmissionInvoked'] is False and q['sourceLinePairNegativeVectors']==3,'complete old Source preserved, not Root/permit operation or new authority')
    expected=copy.deepcopy(old)
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=len(actual),newTestIds=0,sourceProgramDelta=0,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_SUPPLEMENT_ALL_PREVIOUS_COUNTER_PROOFS_RETAINED')
    for k,d in dict(tests=len(actual),suites=len({c for c,n in added}),originalExecs=1,totalProductExecs=1,totalMethodExecutions=len(actual)).items():expected[k]=old[k]+d
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=len(actual),suites=len({c for c,n in added}),execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=len(actual),newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    decl=expected['currentOrdinaryTestDeclarationReference'];inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    selected_rows=[v for v in bindings if (v['className'],v['method']) in added];test_paths={v['path'] for v in selected_rows}
    require(len(selected_rows)==6 and len(test_paths)==1 and added<=ordinary and len(names&ordinary)==2761 and len(ordinary-names)==3025 and len(names-ordinary)==19,'exact ordinary binding and quality19 domains')
    for row in selected_rows:require(data.sha((data.ROOT/row['path']).read_bytes())==row['sourceSha256'],'current actual Test source')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path in sorted(test_paths|set(p['owners'])):
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(row==old['owners'][path],'old exact owner pair')
        else:expected['owners'][path]=row
    expected['ownerStatusCounts']=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values()));expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    decl.update(ordinaryCaseReferences=2761,ordinaryWithoutCurrentCaseReference=3025,existingQualityFixtureCases=19)
    def contract(v):require(wire(v)==wire(expected),'complete independent object; Source/counter/cost/history unchanged')
    contract(m)
    require((m['tests'],m['suites'],m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['totalProductExecs'],m['totalMethodExecutions'])==(2780,409,560,990,289,434,204,2912),'actual domain totals')
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
    bad=copy.deepcopy(m);bad['fullSourceUnits']['dev/codex/schubert/nk/batch/repository/MorningDatabaseSession']['four100']=True
    try:contract(bad)
    except ValueError:profile.append('old-Source-proof-promoted')
    else:raise ValueError('old Source proof overwritten')
    summary={k:m[k] for k in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=len(labels),negativeLabels=labels,profileNegativeVectors=len(profile),profileNegativeLabels=profile,newUniqueMethods=len(actual),newSourcePrograms=0,newPhysicalClasses=0,newMetadataPhysical=0,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
