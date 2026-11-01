"""One independent strict DTO projection exec supersedes only its previous partial proof."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17938-current2840-web-ready-joint-registry-v1','a1289d9a32aa20e1c70eb06cf309b655f77f0af8150e13bd4b93ab3be84e2c06')
PREV_POST=('PG17940-current2840-web-ready-joint-registry-post-v1','52b90797d0975f8ddd31ffb5630d1ec49d9d9d093024908d90054c8c39527dca')
POST=('PG17955-closed-projection-six-post-v3','1926662d6d41c53dba39955e9c29a52f1d1e540e8882b4c70257c677a0ad0d9e')
INDEPENDENT=('PG17954-closed-projection-six-independent-v1','17019f5d360ca190b629980bf04815695e8b9b4317ec93c800daf384b868ad1d')
NAME='dev/codex/schubert/nk/web/security/ClosedWebAuthentication'
QUALITY='tools/quality/architecture/ClosedProjectionValueContractTest.java'
QUALITY_SHA='96dc488720504882f06ef476b0482b34975b400a7d6feec55a9b839385c9c29d'
SCOPE='ONE_EXEC_INDEPENDENT_CLOSED_PROJECTION6_SOURCE_REPLACEMENT_NO_CONTEXT_INSTALL_OR_REAL_AUTH'
OUT=data.BASE/'PG17958-current2846-closed-projection-registry-v1'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    def profile(first,out):
        require(first==('PG17938-current2840-web-ready-joint-registry-v1','a1289d9a32aa20e1c70eb06cf309b655f77f0af8150e13bd4b93ab3be84e2c06') and out.name=='PG17958-current2846-closed-projection-registry-v1' and all(pair[0]!=out.name for pair in [first,PREV_POST,POST,INDEPENDENT]),'literal existing predecessor and output disjoint')
    profile(PREV,OUT);profile_checks=[]
    for first,label in [((OUT.name,PREV[1]),'self-reference'),((PREV[0],'0'*64),'wrong-predecessor-hash')]:
        try:profile(first,OUT)
        except ValueError:profile_checks.append(label)
        else:raise ValueError('bad input/output profile accepted')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and q['semanticNegativeVectors']==32 and q['independentOracleVectors']==6,'independent current source chain')
    require(p['tests']==6 and p['suites']==1 and p['targetSourceUnits']==1 and set(p['fullSourceUnits'])=={NAME} and p['targetUnitFour100'] is True and p['strictFour100GateExit']==0 and p['syntheticAuthenticationDtoProjectionOnly'] is True and p['normalOrdinaryTestSourceDomain'] is False and p['independentQualityMethodCount']==6 and p['actualAuthenticationOrSessionIssued'] is False and p['syntheticJdbcPortsOnly'] is False and p['explicitDnsLookupInvoked'] is False,'actual complete safe parser only')
    m=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==6 and not added&before and all(v['result']=='PASS' for v in p['cases']),'six new independent quality IDs, no repeat')
    require(NAME in old['fullSourceUnits'] and NAME not in old['qualificationReplacedUnitHistory'] and old['fullSourceUnits'][NAME]['four100'] is False,'one exact old partial qualification')
    u=p['fullSourceUnits'][NAME];previous=old['fullSourceUnits'][NAME]
    require(u['physical']==previous['physical']==[NAME] and all(u['totals'][k]['covered']==previous['counters'][k]['covered']+previous['counters'][k]['missed'] and u['totals'][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']),'same whole denominator, not sum of old execs')
    m['qualificationReplacedUnitHistory'][NAME]=copy.deepcopy(previous)
    m['fullSourceUnits'][NAME]=dict(post=POST[0],postSha256=POST[1],physical=[NAME],counters=copy.deepcopy(u['totals']),four100=True,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=False)
    require(QUALITY not in old['owners'] and q['originalTestSourceHashes'][QUALITY]==QUALITY_SHA==data.sha((data.ROOT/QUALITY).read_bytes()) and all(old['owners'][path]==v for path,v in p['owners'].items()),'old canonical owners unchanged; quality tool separate namespace')
    m['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=6,newExecs=1,newSourceNames=[],existingSourceNames=[NAME],singleExecSourceReplacements=1,previousSourceProofsRetainedInHistory=True,historyField='qualificationReplacedUnitHistory',qualityToolPath=QUALITY,qualityToolSha256=QUALITY_SHA,qualityToolNotCanonicalArtifact=True,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    m['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=6,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    cases=before|added
    m.update(registryInputNegativeVectors=len(profile_checks),registryInputNegativeLabels=profile_checks,invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+6,uniqueProductMethodDelta=6,newTestIds=6,sourceProgramDelta=0,four100SourcePrograms=old['four100SourcePrograms']+1,four100Physical=old['four100Physical']+1,four100ExecutablePhysical=old['four100ExecutablePhysical']+1,incompleteSourcePrograms=old['incompleteSourcePrograms']-1,lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(not added&ordinary and len(cases&ordinary)==2806 and len(cases-ordinary)==40,'quality six never ordinary declaration progress')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=40);m['currentOrdinaryTestDeclarationReference']=decl
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']),m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['four100ExecutablePhysical'],m['incompleteSourcePrograms'])==(2846,426,216,2985,139,55,5,587,1020,296,441,416,83),'actual full Source improvement, unrelated scopes unchanged')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','four100SourcePrograms','four100Physical','four100ExecutablePhysical','incompleteSourcePrograms','lastUpdateKind','qualificationReplacedUnitHistory','fullSourceUnits','additionalScopeReferences','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(m['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items() if n!=NAME) and all(m['qualificationReplacedUnitHistory'][n]==v for n,v in old['qualificationReplacedUnitHistory'].items()),'all old proofs/history/cost retained, sole previous partial saved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
