"""Reconstruct Code-free-only population correction; no old case, proof or cost change."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
from pg17858_current2827_codefree17_registry_v1 import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,SCOPE,read,require
PIN='1979776c9e85f43e9e69ed30ceb1dc7444c5bc5ad09b044f479eefff4c46d40f'
OUT=data.BASE/'PG17860-current2827-codefree17-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG17858-current2827-codefree17-registry-v1',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==24,'genuine independent source chain')
    expected=copy.deepcopy(old);new_names=set(p['fullSourceUnits'])
    require(len(new_names)==17 and not new_names&old['fullSourceUnits'].keys(),'17 interface definitions, not new runtime programs')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    zero={k:dict(covered=0,missed=0) for k in ['LINE','METHOD','CLASS','BRANCH']}
    for name in new_names:
        u=p['fullSourceUnits'][name]
        require(u['physical']==[name] and u['totals']==zero and u['metadataOnly'] is True and u['four100'] is False and u['branchNaturallyZero'] is False,'exact whole NoCode, zero is not a percentage')
        expected['fullSourceUnits'][name]=dict(post=POST[0],postSha256=POST[1],physical=[name],counters=copy.deepcopy(zero),four100=False,execSha256=p['originalExecSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=True,branchNaturallyZero=False)
        expected['metadataClasses'][name]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][name])
        row=dict(sha256=data.sha((data.ROOT/u['path']).read_bytes()),**canonical(u['path'],logical))
        if u['path'] in old['owners']:require(old['owners'][u['path']]==row,'old exact canonical owner unchanged')
        else:expected['owners'][u['path']]=row
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=0,newExecs=0,newSourceNames=sorted(new_names),newMeasuredCodefreeSources=17,newExecutablePrograms=0,sourceProgramsAcceptedByThisScope=0,officialPackageInfoDefinitions=copy.deepcopy(p['officialPackageInfoDefinitions']),packageInfoReferenceOnly=True,packageInfoNotCountedAsProgramsOrPt=True,coverageExecUnion=False))
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=17,measuredSourcePrograms=old['measuredSourcePrograms']+17,measuredPhysical=old['measuredPhysical']+17,executablePhysical=old['executablePhysical'],metadataPhysical=old['metadataPhysical']+17,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),lastUpdateKind=SCOPE)
    def contract(v):require(wire(v)==wire(expected),'complete old cases/proofs/history/cost unchanged, only inert definition population')
    contract(m);labels=[]
    vectors=[('tests',0),('suites',0),('originalExecs',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('necessaryJointRepeatedMethods',0),('uniqueProductMethodDelta',1),('newTestIds',1),('sourceProgramDelta',54),('measuredSourcePrograms',0),('measuredPhysical',0),('executablePhysical',0),('metadataPhysical',0),('four100SourcePrograms',309),('four100Physical',454),('naturalZeroBranchSourcePrograms',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',17),('effortPercent',100),('cases',[]),('fullSourceUnits',old['fullSourceUnits']),('metadataClasses',old['metadataClasses']),('owners',{}),('ownerStatusCounts',{}),('jointQualificationReplacedUnitHistory',{}),('additionalScopeReferences',old['additionalScopeReferences']),('lastUpdateKind','IMPLEMENTATION_COMPLETED')]
    for key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value;require(wire(bad)!=wire(m),'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false inert metadata '+key)
    for key,value in [('ordinaryCaseReferences',0),('ordinaryWithoutCurrentCaseReference',0),('existingQualityFixtureCases',54),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('false ordinary/quality count')
    require(len(labels)==34,'fixed negative inventory')
    separate=[]
    for label,change in [('NoCode-as-four100',lambda v:v['fullSourceUnits'][sorted(new_names)[0]].update(four100=True)),('annotation-as-runtime',lambda v:v['additionalScopeReferences'][-1].update(packageInfoNotCountedAsProgramsOrPt=False)),('NoCode-as-PT',lambda v:v['additionalScopeReferences'][-1].update(newTests=17)),('annotation-drop',lambda v:v['additionalScopeReferences'][-1].update(officialPackageInfoDefinitions={})),('zero-as-natural-three100',lambda v:v['fullSourceUnits'][sorted(new_names)[0]].update(branchNaturallyZero=True))]:
        bad=copy.deepcopy(m);change(bad)
        try:contract(bad)
        except ValueError:separate.append(label)
        else:raise ValueError('NoCode/annotation boundary accepted '+label)
    require(m['tests']==old['tests']==2827 and m['suites']==422 and m['necessaryJointRepeatedMethods']==51 and len(m['jointQualificationReferences'])==4 and sum(u['metadataOnly'] for u in m['fullSourceUnits'].values())==23,'unchanged methods/run domain;23 inert Source definitions')
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary={k:m[k] for k in prior['summary']},metadataNegativeVectors=len(labels),negativeLabels=labels,definitionBoundaryNegativeVectors=len(separate),definitionBoundaryNegativeLabels=separate,newSourcePrograms=17,newMeasuredCodefreeSources=17,newExecutablePrograms=0,newUniqueMethods=0,newPhysicalClasses=17,newMetadataPhysical=17,totalCodefreeSourceDefinitions=23,officialPackageInfoDefinitionReferences=37,previousSourceProofsNotReplaced=True,allOldCasesAndSourceProofsPreserved=True,originalMethodsReexecutedByRegistry=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
