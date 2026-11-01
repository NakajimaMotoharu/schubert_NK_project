"""Independently reconstruct XML cases, binary Source categories and unchanged old registry facts."""
import collections
import copy
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg18238_current2937_media_display_registry import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,NAMES,CLOSURES,QUALITY,QUALITY_SHA,SCOPE,read,require,wire
PIN='0a8a2f43c4eed352e40b73003297244475c34bafe48df79f1899b7c818ee0358'
OUT=data.BASE/'PG18240-current2937-media-display-registry-post-v1'
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG18238-current2937-media-display-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==44 and q['independentOracleVectors']==12,'exact independent chain')
    local=[]
    for filename,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/filename).read_bytes();require(data.sha(blob)==pin,'original XML hash')
        root=ET.fromstring(blob);require(int(root.get('tests'))==12 and all(root.get(k)=='0' for k in ['failures','errors','skipped']),'eight actual PASS')
        for c in root.findall('testcase'):
            require(not list(c),'no failed/skipped/aborted');local.append((c.get('classname'),c.get('name')))
    before={(c['classname'],c['name']) for c in old['cases']};added=set(local)
    require(len(local)==len(added)==12 and not before&added and {c for c,n in added}=={'dev.codex.schubert.nk.web.view.MediaDisplayContractTest'},'all new quality identities')
    expected=copy.deepcopy(old);units=expected['fullSourceUnits']
    require(set(p['fullSourceUnits'])==NAMES and not NAMES&set(units),'two only new source qualifications')
    for name,u in p['fullSourceUnits'].items():
        values={k:dict(covered=sum(p['executable'][n]['counters'][k]['covered'] for n in u['physical'] if n in p['executable']),missed=sum(p['executable'][n]['counters'][k]['missed'] for n in u['physical'] if n in p['executable'])) for k in ['LINE','METHOD','CLASS','BRANCH']}
        four=all(v['covered']>0 and v['missed']==0 for v in values.values())
        natural=values['BRANCH']==dict(covered=0,missed=0) and all(values[k]['covered']>0 and values[k]['missed']==0 for k in ['LINE','METHOD','CLASS'])
        require(u['physical']==CLOSURES[name] and values==u['totals'] and u['four100'] is four and u['branchNaturallyZero'] is natural and four,'independent full physical counter category, no natural0 promoted to strict-four')
        units[name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=values,four100=four,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=natural)
    for path,owner in p['owners'].items():
        require(path not in expected['owners'],'only new two owner references');expected['owners'][path]=copy.deepcopy(owner)
    require(len(p['owners'])==2 and QUALITY not in expected['owners'] and q['originalTestSourceHashes'][QUALITY]==QUALITY_SHA==data.sha((data.ROOT/QUALITY).read_bytes()),'quality namespace separate')
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=12,newExecs=1,newSourceNames=sorted(NAMES),existingSourceNames=[],qualityToolPath=QUALITY,qualityToolSha256=QUALITY_SHA,qualityToolNotCanonicalArtifact=True,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    expected['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=12,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    cases=before|added;physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=expected['metadataClasses']
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=2,registryInputNegativeLabels=['self-reference','wrong-predecessor-hash'],cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+12,uniqueProductMethodDelta=12,newTestIds=12,sourceProgramDelta=len(units)-len(old['fullSourceUnits']),measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(len(ordinary)==5786 and len(cases&ordinary)==2806 and len(cases-ordinary)==131 and not added&ordinary,'no ordinary progress inferred')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=131);expected['currentOrdinaryTestDeclarationReference']=decl
    def contract(value):require(wire(value)==wire(expected),'all independently reconstructed scope/old facts/costs/cases exact')
    contract(m);labels=[]
    vectors=[('tests',0),('suites',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('necessaryJointRepeatedMethods',0),('uniqueProductMethodDelta',0),('newTestIds',0),('sourceProgramDelta',0),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('four100ExecutablePhysical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',old['cases']),('fullSourceUnits',old['fullSourceUnits']),('owners',old['owners']),('ownerStatusCounts',{}),('additionalScopeReferences',old['additionalScopeReferences']),('jointQualificationReferences',[]),('metadataClasses',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('naturalZeroBranchPhysical',0)]
    for key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value;require(wire(bad)!=wire(m),'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false registry '+key)
    for key,value in [('ordinaryCaseReferences',2812),('ordinaryWithoutCurrentCaseReference',0),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('false ordinary/quality domain')
    additions=set(m['owners'])-set(old['owners']);require(len(labels)==34 and additions==set(p['owners']) and all(m['owners'][n]==v for n,v in old['owners'].items()),'only two canonical target owners added')
    boundary=[]
    for label,change in [('strict-four-erased',lambda v:v['fullSourceUnits']['dev/codex/schubert/nk/web/view/MusicTrackViewModel'].update(four100=False)),('quality-as-owner',lambda v:v['owners'].update({QUALITY:dict(canonicalOwner='WBS-F03')})),('quality-hash',lambda v:v['additionalScopeReferences'][-1].update(qualityToolSha256='0'*64)),('new-source-erased',lambda v:v['fullSourceUnits'].pop(next(iter(NAMES))))]:
        bad=copy.deepcopy(m);change(bad)
        try:contract(bad)
        except ValueError:boundary.append(label)
        else:raise ValueError('scope boundary accepted '+label)
    input_checks=[]
    for key,value in [('registryInputNegativeVectors',0),('registryInputNegativeLabels',[])]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:input_checks.append(key)
        else:raise ValueError('input/output guard missing')
    require(m['jointQualificationReferences']==old['jointQualificationReferences'] and m['jointQualificationReplacedUnitHistory']==old['jointQualificationReplacedUnitHistory'] and m['qualificationReplacedUnitHistory']==old['qualificationReplacedUnitHistory'],'all old histories unchanged; no artificial joint repeat')
    for value in [old,prior,p,q,m]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary={k:m[k] for k in prior['summary']},metadataNegativeVectors=len(labels),negativeLabels=labels,replacementBoundaryNegativeVectors=len(boundary),replacementBoundaryNegativeLabels=boundary,registryInputNegativeVectors=len(input_checks),newSourcePrograms=2,singleExecSourceReplacements=0,previousSourceProofsNotReplaced=True,previousProofsPreservedInHistory=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,currentOrdinaryTestDeclarationReference=decl,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
