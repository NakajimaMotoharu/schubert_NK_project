"""Independently reconstruct passive Source addition while all tests, JVMs and old proofs stay exact."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg18059_current2863_caddy_passive_registry_v2 import SOURCE,PREV,PREV_POST,POST,INDEPENDENT,SCOPE,read,require
import pg18050_caddy_exception_passive_post_v1 as measured
PIN='e3d39ba1ef37df634338d1be0bc6cb02f0104c16c3c6c634071d772288f78bba'
OUT=data.BASE/'PG18060-current2863-caddy-passive-registry-post-v1'
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old,prior,p,q,m=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT,('PG18059-current2863-caddy-passive-registry-v2',PIN)]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q,m]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==20,'independent exact chain')
    require(p['fullSourceUnits'][measured.NAME]['totals']==dict(LINE=dict(missed=0,covered=2),METHOD=dict(missed=0,covered=1),CLASS=dict(missed=0,covered=1),BRANCH=dict(missed=0,covered=0)),'independent constructor counters')
    expected=copy.deepcopy(old)
    expected['fullSourceUnits'][measured.NAME]=dict(post=POST[0],postSha256=POST[1],physical=[measured.NAME],counters=p['fullSourceUnits'][measured.NAME]['totals'],four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=True)
    expected['owners'][measured.PATH]=copy.deepcopy(p['owners'][measured.PATH])
    expected['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=0,newExecs=0,newSourceNames=[measured.NAME],existingSourceNames=[],originalAlreadyCountedPost=list(measured.POST),existingSingleExecSha256=p['execSha256'],productTestsReexecuted=0,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    allphysical={n for v in expected['fullSourceUnits'].values() for n in v['physical']}
    natural={n for v in expected['fullSourceUnits'].values() if v['branchNaturallyZero'] for n in v['physical']}
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=2,registryInputNegativeLabels=['already-counted-exec-missing','source-already-measured'],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=1,measuredSourcePrograms=len(expected['fullSourceUnits']),measuredPhysical=len(allphysical),executablePhysical=len(allphysical-expected['metadataClasses'].keys()),naturalZeroBranchSourcePrograms=sum(v['branchNaturallyZero'] for v in expected['fullSourceUnits'].values()),naturalZeroBranchPhysical=len(natural),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),lastUpdateKind=SCOPE)
    def contract(value):require(wire(value)==wire(expected),'all independently reconstructed old/new facts exact')
    contract(m);labels=[]
    vectors=[('tests',0),('suites',0),('totalProductExecs',0),('totalMethodExecutions',0),('totalRepeatedOriginalMethods',0),('necessaryJointRepeatedMethods',0),('uniqueProductMethodDelta',1),('newTestIds',1),('sourceProgramDelta',0),('measuredSourcePrograms',0),('measuredPhysical',0),('four100SourcePrograms',0),('four100Physical',0),('four100ExecutablePhysical',0),('incompleteSourcePrograms',0),('coverageExecUnion',True),('formalUpdated',True),('newAccepted',1),('effortPercent',100),('cases',[]),('fullSourceUnits',old['fullSourceUnits']),('owners',old['owners']),('ownerStatusCounts',{}),('additionalScopeReferences',old['additionalScopeReferences']),('jointQualificationReferences',[]),('metadataClasses',{}),('metadataPhysical',0),('resourceOnlyReferences',[]),('javascriptResourceDomain',{}),('naturalZeroBranchPhysical',0)]
    for key,value in vectors:
        bad=copy.deepcopy(m);bad[key]=value;require(bad!=m,'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false passive registry '+key)
    for key,value in [('ordinaryCaseReferences',2812),('ordinaryWithoutCurrentCaseReference',0),('existingQualityFixtureCases',0),('phaseCompletionPercent',100)]:
        bad=copy.deepcopy(m);bad['currentOrdinaryTestDeclarationReference'][key]=value
        try:contract(bad)
        except ValueError:labels.append('ordinary-'+key)
        else:raise ValueError('false ordinary progress')
    boundary=[]
    for label,change in [('natural-as-four',lambda v:v['fullSourceUnits'][measured.NAME].update(four100=True)),('new-exec-count',lambda v:v['additionalScopeReferences'][-1].update(newExecs=1)),('new-case-count',lambda v:v['additionalScopeReferences'][-1].update(newTests=6)),('same-count-unknown-physical',lambda v:v['fullSourceUnits'][measured.NAME].update(physical=['unknown']))]:
        bad=copy.deepcopy(m);change(bad)
        try:contract(bad)
        except ValueError:boundary.append(label)
        else:raise ValueError('invalid passive boundary')
    inputs=[]
    for key,value in [('registryInputNegativeVectors',0),('registryInputNegativeLabels',[])]:
        bad=copy.deepcopy(m);bad[key]=value
        try:contract(bad)
        except ValueError:inputs.append(key)
        else:raise ValueError('missing actual input vectors')
    require(len(labels)==34 and len(boundary)==4 and len(inputs)==2,'actual vector counts')
    require(m['cases']==old['cases'] and m['originalPostReferences']==old['originalPostReferences'] and m['currentOrdinaryTestDeclarationReference']==old['currentOrdinaryTestDeclarationReference'] and m['jointQualificationReferences']==old['jointQualificationReferences'],'no doubled methods/JVM/repeat')
    for v in [old,prior,p,q,m]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=PIN,summary={k:m[k] for k in prior['summary']},metadataNegativeVectors=len(labels),negativeLabels=labels,replacementBoundaryNegativeVectors=len(boundary),replacementBoundaryNegativeLabels=boundary,registryInputNegativeVectors=len(inputs),newSourcePrograms=1,singleExecSourceReplacements=0,previousSourceProofsNotReplaced=True,previousProofsPreservedInHistory=True,originalMethodsReexecutedByRegistry=0,newMethodOrJunitCount=0,coverageExecUnion=False,currentOrdinaryTestDeclarationReference=m['currentOrdinaryTestDeclarationReference'],newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
