"""Add eight tests for two complete User display Sources, preserving separate held family and old proofs."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18348-current2976-user-search-registry-v1','b8906f29f42b0fb00d358003843fc7ba531c752f4653c0221bb8f300b016eab7')
PREV_POST=('PG18350-current2976-user-search-registry-post-v1','bd473b34853e88718dd738683a53f912bb90cc5a123acdd46c5f7a7eb62f8d91')
POST=('PG18362-question-notification-search26-post-v1','37517334dc95f2fa471bd820d6e24a3f497c4a8b6b55f63626684e9afcfff1ce')
INDEPENDENT=('PG18364-question-notification-search26-independent-v1','5b537d900dc3223736eb1b2616355196dccaeb77791878205fb7ea3d09422384')
NAMES=set(["dev/codex/schubert/nk/web/form/QuestionSearchForm","dev/codex/schubert/nk/web/form/NotificationSearchForm"])
CLOSURES={"dev/codex/schubert/nk/web/form/QuestionSearchForm":["dev/codex/schubert/nk/web/form/QuestionSearchForm"],"dev/codex/schubert/nk/web/form/NotificationSearchForm":["dev/codex/schubert/nk/web/form/NotificationSearchForm"]}
QUALITY='tools/quality/architecture/QuestionSearchInputContractTest.java'
QUALITY_SHA='8be5ab3dc80b86f94cdc48ac49cfcfa0a439766c43a4db5b51c4c32011e08489'
QUALITY_PINS={"tools/quality/architecture/QuestionSearchInputContractTest.java":"8be5ab3dc80b86f94cdc48ac49cfcfa0a439766c43a4db5b51c4c32011e08489","tools/quality/architecture/NotificationSearchInputContractTest.java":"3cd834e9f5d8e41ba0ac27d90ec9af2f5b4d7ea670099a03c5547817fff77717"}
SCOPE='ONE_EXEC_QUESTION_NOTIFICATION_SEARCH26_SOURCE2_NO_AUTHORITY_OR_DB'
OUT=data.BASE/'PG18368-current3002-qn-search-registry-v1'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    def profile(first):
        require(first==('PG18348-current2976-user-search-registry-v1','b8906f29f42b0fb00d358003843fc7ba531c752f4653c0221bb8f300b016eab7') and all(v[0]!=OUT.name for v in [first,PREV_POST,POST,INDEPENDENT]),'literal independent input/output pairs')
    profile(PREV);checks=[]
    for first,label in [((OUT.name,PREV[1]),'self-reference'),((PREV[0],'0'*64),'wrong-predecessor-hash')]:
        try:profile(first)
        except ValueError:checks.append(label)
        else:raise ValueError('invalid input profile accepted')
    old,prior,p,q=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==43 and q['independentOracleVectors']==26,'genuine same-source independently qualified chain')
    require(p['tests']==26 and p['suites']==2 and set(p['fullSourceUnits'])==NAMES and not NAMES&set(old['fullSourceUnits']) and p['singleSession'] is True and p['crcMismatch']==p['forbiddenProductProbeHits']==0,'two new measured Sources, exact eight cases')
    require(p['allMeasuredApplicableCountersCovered'] is True and p['strictFour100GateExit']==0 and p['targetUnitFour100'] is True and p['pureQuestionNotificationSearchFormsOnly'] is True and p['actualExternalAuthorizationOrMutation'] is p['actualBusinessProviderInvoked'] is p['actualThrowableGraphTraversal'] is False,'both whole Sources strict-four, pure values only')
    require(q['independentByteAndNormalizationVectors']==7 and q['independentJstDateVectors']==5 and q['independentDateRangeVectors']==3 and q['independentOracleVectors']==26,'independent standard codec and NFC basis, no Product replay')
    m=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==26 and not before&added and all(v['result']=='PASS' for v in p['cases']),'new quality identities only')
    units=m['fullSourceUnits']
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==CLOSURES[name] and u['threeCounter100'] is True and u['four100'] is True,'exact source closure/categories')
        units[name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(len(p['owners'])==2,'only target Main owners')
    for path,owner in p['owners'].items():
        require(owner['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(owner[k]==v for k,v in canonical(path,logical).items()) and owner['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','exact approved original owner/cost pair, not change owner')
        require(path not in m['owners'],'two new scope owner references only');m['owners'][path]=copy.deepcopy(owner)
    require(q['originalTestSourceHashes']==QUALITY_PINS and all(path not in m['owners'] and data.sha((data.ROOT/path).read_bytes())==h for path,h in QUALITY_PINS.items()),'quality path separate')
    m['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=26,newExecs=1,newSourceNames=sorted(NAMES),existingSourceNames=[],qualityToolPath=QUALITY,qualityToolSha256=QUALITY_SHA,qualityToolSourceHashes=QUALITY_PINS,qualityToolNotCanonicalArtifact=True,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    m['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=26,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    cases=before|added;physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=m['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'disjoint complete source closures')
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=len(checks),registryInputNegativeLabels=checks,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+26,uniqueProductMethodDelta=26,newTestIds=26,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(not added&ordinary and len(cases&ordinary)==2806 and len(cases-ordinary)==196,'eight quality not ordinary progress')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=196);m['currentOrdinaryTestDeclarationReference']=decl
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']),m['measuredSourcePrograms'],m['measuredPhysical'],m['executablePhysical'],m['four100SourcePrograms'],m['four100Physical'],m['four100ExecutablePhysical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'],m['incompleteSourcePrograms'])==(3002,450,235,3157,155,71,7,649,1092,892,333,485,459,213,233,80),'current technical scope, no acceptance or old-source transfer')
    require(m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':584,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':236,'UNKNOWN':302},'no guessed owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','owners','fullSourceUnits','additionalScopeReferences','originalPostReferences','currentOrdinaryTestDeclarationReference','lastUpdateKind'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(units[n]==v for n,v in old['fullSourceUnits'].items()) and all(m['owners'][n]==v for n,v in old['owners'].items()),'all old source proofs, histories, repeats, costs and authority unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
