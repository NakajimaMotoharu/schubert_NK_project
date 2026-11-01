"""Independent XML and one-source replacement reconstruction; quality cases remain separate."""
import copy
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg17958_current2846_closed_projection_registry_v1 import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,NAME,QUALITY,QUALITY_SHA,SCOPE,read,require,wire
PIN='b65ad3a517cd4ef79b9587ec948e17bf397d873274d2f800861e1bcab59f2c94'
OUT=data.BASE/'PG17961-current2846-closed-projection-registry-post-v2'
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG17958-current2846-closed-projection-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==32 and q['independentOracleVectors']==6,'exact independent chain')
    xml_reference=p['originalCompletedPostReference']
    xml_post=read(xml_reference)
    def lineage(value):
        require(value['actualExit']==0 and value['source']==SOURCE and all(wire(value[k])==wire(p[k]) for k in ['cases','xmlHashes','execSha256','sessionIdentity']),'exact original XML lineage/source/run')
    lineage(xml_post);lineage_checks=[]
    for key,value in [('source','OLD'),('xmlHashes',{}),('cases',[])]:
        bad=copy.deepcopy(xml_post);bad[key]=value
        try:lineage(bad)
        except ValueError:lineage_checks.append(key)
        else:raise ValueError('corrupt XML lineage accepted')
    verify(xml_post['invocation'])
    actual=[]
    for filename,pin in p['xmlHashes'].items():
        blob=(data.BASE/xml_reference[0]/filename).read_bytes();require(data.sha(blob)==pin,'original XML hash')
        root=ET.fromstring(blob);require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'no nonpass')
        for node in root.findall('testcase'):require(not list(node),'actual PASS');actual.append((node.get('classname'),node.get('name')))
    before={(v['classname'],v['name']) for v in old['cases']};added=set(actual);require(len(actual)==len(added)==6 and not before&added and all(c=='dev.codex.schubert.nk.web.security.ClosedProjectionValueContractTest' for c,n in added),'six new quality cases, not repeats')
    expected=copy.deepcopy(old);unit=p['fullSourceUnits'][NAME]
    counters={k:p['executable'][NAME]['counters'][k] for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(counters=={'LINE':dict(covered=14,missed=0),'METHOD':dict(covered=2,missed=0),'CLASS':dict(covered=1,missed=0),'BRANCH':dict(covered=18,missed=0)} and unit['physical']==[NAME] and unit['totals']==counters,'independent whole binary counter identity')
    require(NAME not in old['qualificationReplacedUnitHistory'] and old['fullSourceUnits'][NAME]['physical']==[NAME] and all(old['fullSourceUnits'][NAME]['counters'][k]['covered']+old['fullSourceUnits'][NAME]['counters'][k]['missed']==v['covered'] for k,v in counters.items()),'same denominator, not merged execs')
    expected['qualificationReplacedUnitHistory'][NAME]=copy.deepcopy(old['fullSourceUnits'][NAME])
    expected['fullSourceUnits'][NAME]=dict(post=POST[0],postSha256=POST[1],physical=[NAME],counters=copy.deepcopy(counters),four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=6,newExecs=1,newSourceNames=[],existingSourceNames=[NAME],singleExecSourceReplacements=1,previousSourceProofsRetainedInHistory=True,historyField='qualificationReplacedUnitHistory',qualityToolPath=QUALITY,qualityToolSha256=QUALITY_SHA,qualityToolNotCanonicalArtifact=True,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=6,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    cases=before|added
    expected.update(registryInputNegativeVectors=2,registryInputNegativeLabels=['self-reference','wrong-predecessor-hash'],invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+6,uniqueProductMethodDelta=6,newTestIds=6,sourceProgramDelta=0,four100SourcePrograms=old['four100SourcePrograms']+1,four100Physical=old['four100Physical']+1,four100ExecutablePhysical=old['four100ExecutablePhysical']+1,incompleteSourcePrograms=old['incompleteSourcePrograms']-1,lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(not added&ordinary and len(cases&ordinary)==2806 and len(cases-ordinary)==40,'new quality, ordinary declaration unchanged')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=40);expected['currentOrdinaryTestDeclarationReference']=decl
    def contract(v):require(wire(v)==wire(expected),'all old costs/cases/other Source proofs preserved; exact one Source improvement')
    contract(m);labels=[]
    vectors=[('tests',0),('suites',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('necessaryJointRepeatedMethods',0),('uniqueProductMethodDelta',0),('newTestIds',0),('sourceProgramDelta',1),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('four100ExecutablePhysical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',old['cases']),('fullSourceUnits',old['fullSourceUnits']),('qualificationReplacedUnitHistory',old['qualificationReplacedUnitHistory']),('owners',{}),('ownerStatusCounts',{}),('additionalScopeReferences',old['additionalScopeReferences']),('jointQualificationReferences',[]),('metadataClasses',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{})]
    for key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value;require(wire(bad)!=wire(m),'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false registry '+key)
    for key,value in [('ordinaryCaseReferences',2811),('ordinaryWithoutCurrentCaseReference',0),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('false ordinary/quality domain')
    require(len(labels)==34 and m['owners']==old['owners'] and m['necessaryJointRepeatedMethods']==55 and len(m['jointQualificationReferences'])==5,'no old ownership or joint count reassignment')
    replace_checks=[]
    for label,change in [('old-partial-history-erased',lambda v:v['qualificationReplacedUnitHistory'].pop(NAME)),('current-four100-lost',lambda v:v['fullSourceUnits'][NAME].update(four100=False)),('quality-as-canonical-owner',lambda v:v['owners'].update({QUALITY:dict(canonicalOwner='WBS-F03')})),('quality-hash-wrong',lambda v:v['additionalScopeReferences'][-1].update(qualityToolSha256='0'*64))]:
        bad=copy.deepcopy(m);change(bad)
        try:contract(bad)
        except ValueError:replace_checks.append(label)
        else:raise ValueError('single-source replacement boundary '+label)
    input_checks=[]
    for key,value in [('registryInputNegativeVectors',0),('registryInputNegativeLabels',[])]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:input_checks.append(key)
        else:raise ValueError('missing self-reference/wrong-hash prevention')
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,xmlSourceReference=xml_reference,xmlLineageNegativeVectors=lineage_checks,summary={k:m[k] for k in prior['summary']},registryInputNegativeVectors=len(input_checks),registryInputNegativeLabels=input_checks,metadataNegativeVectors=len(labels),negativeLabels=labels,replacementBoundaryNegativeVectors=len(replace_checks),replacementBoundaryNegativeLabels=replace_checks,newSourcePrograms=0,singleExecSourceReplacements=1,newFour100Sources=1,newUniqueMethods=5,newQualityMethods=5,newOrdinaryMethods=0,necessaryRepeatMethods=0,previousSourceProofsNotReplaced=False,previousProofsPreservedInHistory=True,originalMethodsReexecutedByRegistry=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
