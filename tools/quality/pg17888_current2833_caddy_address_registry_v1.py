"""Single genuine memory proxy exec supersedes one partial Source; no joint repeat or union."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG17858-current2827-codefree17-registry-v1','1979776c9e85f43e9e69ed30ceb1dc7444c5bc5ad09b044f479eefff4c46d40f')
PREV_POST=('PG17860-current2827-codefree17-registry-post-v1','cab0b503a6782a8cdf5f4bc88487be24f52a83449c693c8af3830b3a3a6ffd86')
POST=('PG17882-caddy-address-boundary-six-post-v1','22f6c56e81a6194651e054694fb881c17da3857840e4db491f570d429e5851bb')
INDEPENDENT=('PG17884-caddy-address-boundary-six-independent-v1','2594c867ee5d542223d53feaa3c2caaf0ab99bc378f50f1b67fbb9a9c0f9e51a')
NAME='dev/codex/schubert/nk/web/security/CaddyClientAddressResolver'
QUALITY='tools/quality/architecture/CaddyAddressBoundaryContractTest.java'
QUALITY_SHA='f0612ddb3090a317163f1793408c724796c1ab818fde23b0942192283178c6c0'
SCOPE='ONE_EXEC_INDEPENDENT_NUMERIC_PROXY6_SOURCE_REPLACEMENT_NO_FILTER_AUDIT_OR_BIZ_ACCEPTANCE'
OUT=data.BASE/'PG17888-current2833-caddy-address-registry-v1'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and prior['metadataNegativeVectors']==34 and q['postSha256']==POST[1] and q['semanticNegativeVectors']==32 and q['independentOracleVectors']==6,'independent current source chain')
    require(p['tests']==6 and p['suites']==1 and p['targetSourceUnits']==1 and set(p['fullSourceUnits'])=={NAME} and p['targetUnitFour100'] is True and p['strictFour100GateExit']==0 and p['memoryServletHeaderFixtureOnly'] is True and p['syntheticJdbcPortsOnly'] is False and p['explicitDnsLookupInvoked'] is False,'actual complete safe parser only')
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
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+6,uniqueProductMethodDelta=6,newTestIds=6,sourceProgramDelta=0,four100SourcePrograms=old['four100SourcePrograms']+1,four100Physical=old['four100Physical']+1,four100ExecutablePhysical=old['four100ExecutablePhysical']+1,incompleteSourcePrograms=old['incompleteSourcePrograms']-1,lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(not added&ordinary and len(cases&ordinary)==2806 and len(cases-ordinary)==27,'quality six never ordinary declaration progress')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=27);m['currentOrdinaryTestDeclarationReference']=decl
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']),m['measuredSourcePrograms'],m['measuredPhysical'],m['four100SourcePrograms'],m['four100Physical'],m['four100ExecutablePhysical'],m['incompleteSourcePrograms'])==(2833,423,213,2968,135,51,4,587,1020,293,438,413,86),'actual full Source improvement, unrelated scopes unchanged')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','four100SourcePrograms','four100Physical','four100ExecutablePhysical','incompleteSourcePrograms','lastUpdateKind','qualificationReplacedUnitHistory','fullSourceUnits','additionalScopeReferences','originalPostReferences','currentOrdinaryTestDeclarationReference'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(m['fullSourceUnits'][n]==v for n,v in old['fullSourceUnits'].items() if n!=NAME) and all(m['qualificationReplacedUnitHistory'][n]==v for n,v in old['qualificationReplacedUnitHistory'].items()),'all old proofs/history/cost retained, sole previous partial saved')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
