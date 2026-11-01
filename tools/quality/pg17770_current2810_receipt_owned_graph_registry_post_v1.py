"""Independent unknown4/current three added Sources; retain one old natural proof and all misses."""
import copy
import json
import xml.etree.ElementTree as ET
from collections import Counter
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg17768_current2810_receipt_owned_graph_registry_v1 import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,SCOPE,read,require
PIN='34cfd2a3112993b52da7443376e7fd7470ed9709fd00e3612f3b5792c24d8727'
OUT=data.BASE/'PG17770-current2810-receipt-owned-graph-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG17768-current2810-receipt-owned-graph-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and (q['semanticNegativeVectors'],q['independentOracleVectors'])==(32,3),'independent chain')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML pin');root=ET.fromstring(blob)
        require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'no nonpass')
        for node in root.findall('testcase'):require(not list(node),'PASS');actual.append((node.get('classname'),node.get('name')))
    before={(v['classname'],v['name']) for v in old['cases']};added=set(actual);require(len(actual)==len(added)==3 and not added&before,'33 fresh current original methods')
    names=before|added;expected=copy.deepcopy(old)
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(names)],suiteNames=sorted({c for c,n in names}),uniqueProductMethodDelta=3,newTestIds=0,sourceProgramDelta=2,lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_BROADER_OLD_PROOFS_RETAINED_PARTIAL_DISCLOSED')
    root='dev/codex/schubert/nk/batch/platform/'
    expected_new={'dev/codex/schubert/nk/web/receipt/ReceiptReferenceRepository','dev/codex/schubert/nk/web/receipt/ReceiptReferenceException'}
    fresh={n for n in p['fullSourceUnits'] if n not in old['fullSourceUnits']}
    four_names=set()
    natural_names={'dev/codex/schubert/nk/web/receipt/ReceiptReferenceException'}
    partial_names=expected_new-four_names-natural_names
    require(fresh==expected_new and (q['newSourcePrograms'],q['newPhysicalClasses'],q['metadataPhysicalClasses'])==(2,3,1),'independent declared closure, not copied deltas')
    physical={c for n in fresh for c in p['fullSourceUnits'][n]['physical']}
    meta=set(p['metadataClasses'])-old['metadataClasses'].keys()
    four_physical={c for n in four_names for c in p['fullSourceUnits'][n]['physical']}
    natural_physical={c for n in natural_names for c in p['fullSourceUnits'][n]['physical']}
    require(len(physical)==3 and len(meta)==1 and meta<=physical and len(four_physical)==0 and len(natural_physical)==1 and len(partial_names)==1 and len({c for c,n in actual})==1,'independent measured sets and actual XML suites')
    deltas=dict(tests=len(actual),suites=len({c for c,n in actual}),originalExecs=1,totalProductExecs=1,totalMethodExecutions=len(actual),measuredSourcePrograms=len(fresh),measuredPhysical=len(physical),executablePhysical=len(physical-meta),metadataPhysical=len(meta),incompleteSourcePrograms=len(partial_names),naturalZeroBranchSourcePrograms=len(natural_names),naturalZeroBranchPhysical=len(natural_physical),four100SourcePrograms=len(four_names),four100Physical=len(four_physical),four100ExecutablePhysical=len(four_physical-meta))
    for key,delta in deltas.items():expected[key]=old[key]+delta
    new={n for n in p['fullSourceUnits'] if n not in old['fullSourceUnits']}
    require(new==expected_new,'four current complete Source denominators')
    for name in new:
        u=p['fullSourceUnits'][name]
        expected['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=name in four_names,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=name in natural_names)
    for name in meta:expected['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
    retained=set(p['fullSourceUnits'])&old['fullSourceUnits'].keys()
    require(not retained,'retain both whole old Source qualifications')
    for name in set(p['metadataClasses'])-meta:require(expected['metadataClasses'][name]==old['metadataClasses'][name],'eight old NoCode rows retained')
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=3,newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],existingSourceNames=sorted(retained),newSourceNames=sorted(new),existingSourceQualificationPreserved=True,coverageExecUnion=False,sourceProgramsAcceptedByThisScope=0))
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=3,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=list(p['owners'])+["src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/receipt/ReceiptFailureGraph329Test.java"]
    for path in paths:
        row=dict(sha256=data.sha((data.ROOT/path).read_bytes()),**canonical(path,logical))
        if path in old['owners']:require(old['owners'][path]==row,'old exact owner')
        else:expected['owners'][path]=row
    require(len(expected['owners'])-len(old['owners'])==3,'four Source and six original Test owner references')
    expected['ownerStatusCounts']=dict(Counter(v['ownershipStatus'] for v in expected['owners'].values()))
    expected['unknownOwnerPaths']=sum(v['canonicalOwner'] is None for v in expected['owners'].values())
    decl=expected['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(added<=ordinary and len(names&ordinary)==2791 and len(ordinary-names)==2995 and len(names-ordinary)==19,'independent ordinary counts')
    decl.update(ordinaryCaseReferences=2791,ordinaryWithoutCurrentCaseReference=2995,existingQualityFixtureCases=19)
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
    for key,value in [('semanticNegativeVectors',47),('independentOracleVectors',2)]:
        bad=dict(q);bad[key]=value
        require((bad['semanticNegativeVectors'],bad['independentOracleVectors'])!=(32,3),'old/wrong oracle chain rejected')
        chain_labels.append(key)
    require(SCOPE=='ORIGINAL_RECEIPT_OWNED_GRAPH3_TWO_SOURCE_THREE_PHYSICAL_NATURAL_EXCEPTION_AND_PARTIAL_REPOSITORY_NO_REAL_DB_OR_AUTH','independent truthful partial scope')
    test_paths={v['path'] for v in bindings if (v['className'],v['method']) in added}
    require(test_paths==set(paths)-set(p['owners']) and all(path in m['owners'] for path in test_paths),'actual catalog Test path, no stale profile reference')
    profile=[]
    bad=copy.deepcopy(m);bad['originalPostReferences'][-1]['scope']='OLD_FOUR100_SCOPE'
    try:contract(bad)
    except ValueError:profile.append('wrong-scope')
    else:raise ValueError('false scope accepted')
    for name in sorted(partial_names):
        require(name in m['fullSourceUnits'] and m['fullSourceUnits'][name]['four100'] is False,'all actual partial Source keys exist')
        bad=copy.deepcopy(m);bad['fullSourceUnits'][name]['four100']=True
        require(bad!=m,'nondegenerate partial promotion')
        try:contract(bad)
        except ValueError:profile.append('partial-promoted-to-four100:'+name)
        else:raise ValueError('false full-Source success accepted')
    require(len(profile)==len(partial_names)+1,'all new partial Sources covered, no stale copied name')
    for name in sorted(four_names):
        require(m['fullSourceUnits'][name]['four100'] is True,'current complete Source already four100')
        bad=copy.deepcopy(m);bad['fullSourceUnits'][name]['four100']=False
        require(bad!=m,'nondegenerate four100 downgrade')
        try:contract(bad)
        except ValueError:profile.append('four100-downgraded:'+name)
        else:raise ValueError('false Source downgrade accepted')
    for name in sorted(natural_names):
        require(m['fullSourceUnits'][name]['branchNaturallyZero'] is True and m['fullSourceUnits'][name]['four100'] is False and m['fullSourceUnits'][name]['counters']['BRANCH']==dict(missed=0,covered=0),'natural B0 never manufactured as four100')
        bad=copy.deepcopy(m);bad['fullSourceUnits'][name]['branchNaturallyZero']=False
        try:contract(bad)
        except ValueError:profile.append('natural-source-lost:'+name)
        else:raise ValueError('false natural classification accepted')
    require(len(profile)==len(partial_names)+len(four_names)+len(natural_names)+1,'all actual Source profiles')
    declared=dict(newUniqueMethods=len(actual),newSourcePrograms=len(fresh),newPhysicalClasses=len(physical),newMetadataPhysical=len(meta))
    require(declared==dict(newUniqueMethods=3,newSourcePrograms=2,newPhysicalClasses=3,newMetadataPhysical=1),'public summary from actual delta')
    summary_labels=[]
    for key in declared:
        bad=dict(declared);bad[key]+=1
        require(bad!=declared and bad!=dict(newUniqueMethods=3,newSourcePrograms=2,newPhysicalClasses=3,newMetadataPhysical=1),'false public summary rejected')
        summary_labels.append(key)
    summary={k:m[k] for k in prior['summary']}
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary=summary,metadataNegativeVectors=34,negativeLabels=labels,chainNegativeVectors=len(chain_labels),chainNegativeLabels=chain_labels,profileNegativeVectors=len(profile),profileNegativeLabels=profile,publicSummaryNegativeVectors=len(summary_labels),publicSummaryNegativeLabels=summary_labels,**declared,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
