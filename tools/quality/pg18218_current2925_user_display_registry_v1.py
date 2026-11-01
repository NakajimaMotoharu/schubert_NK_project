"""Add eight tests for two complete User display Sources, preserving separate held family and old proofs."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18198-current2917-request-display-registry-v1','6551658fcc9bad07e701e3eb28bfbdbd51d660dd9606b17d6e28ba5e8a163054')
PREV_POST=('PG18200-current2917-request-display-registry-post-v1','5fb3016c181d8a85f31b29a0aed6b69e5404bf818ac74897e3c5ea04a5a0a19b')
POST=('PG18212-user-display-eight-post-v1','1ae44fb4997505174d3b36cc7058b67bf5876c8929a8ac56d7f84d166c298445')
INDEPENDENT=('PG18214-user-display-eight-independent-v1','f05e5f657ed1306e469629a130c3c74cf50c2301e5818a2938b6fd7af9feadb6')
NAMES=set(["dev/codex/schubert/nk/web/view/UserListViewModel","dev/codex/schubert/nk/web/view/UserDetailViewModel"])
CLOSURES={"dev/codex/schubert/nk/web/view/UserListViewModel":["dev/codex/schubert/nk/web/view/UserListViewModel","dev/codex/schubert/nk/web/view/UserListViewModel$Row"],"dev/codex/schubert/nk/web/view/UserDetailViewModel":["dev/codex/schubert/nk/web/view/UserDetailViewModel"]}
QUALITY='tools/quality/architecture/UserDisplayContractTest.java'
QUALITY_SHA='74e37d277cb69b31bbae8b2da0caceb5abe7e7c9cde7714309a2a0b3ef52c970'
SCOPE='ONE_EXEC_USER_DISPLAY8_SOURCE2_LOCAL_ROLE_GUARD_NO_EXTERNAL_AUTH_OR_DB'
OUT=data.BASE/'PG18218-current2925-user-display-registry-v1'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    def profile(first):
        require(first==('PG18198-current2917-request-display-registry-v1','6551658fcc9bad07e701e3eb28bfbdbd51d660dd9606b17d6e28ba5e8a163054') and all(v[0]!=OUT.name for v in [first,PREV_POST,POST,INDEPENDENT]),'literal independent input/output pairs')
    profile(PREV);checks=[]
    for first,label in [((OUT.name,PREV[1]),'self-reference'),((PREV[0],'0'*64),'wrong-predecessor-hash')]:
        try:profile(first)
        except ValueError:checks.append(label)
        else:raise ValueError('invalid input profile accepted')
    old,prior,p,q=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==42 and q['independentOracleVectors']==8,'genuine same-source independently qualified chain')
    require(p['tests']==8 and p['suites']==1 and set(p['fullSourceUnits'])==NAMES and not NAMES&set(old['fullSourceUnits']) and p['singleSession'] is True and p['crcMismatch']==p['forbiddenProductProbeHits']==0,'two new measured Sources, exact eight cases')
    require(p['allMeasuredApplicableCountersCovered'] is True and p['strictFour100GateExit']==0 and p['targetUnitFour100'] is True and p['pureUserDisplayValuesOnly'] is True and p['actualExternalAuthorizationOrMutation'] is p['actualBusinessProviderInvoked'] is p['actualThrowableGraphTraversal'] is False,'both whole Sources strict-four, pure values only')
    require(q['independentUnicodeBasisVectors']==4 and q['independentUnicodeBasisNegativeVectors']==2 and q['correctedSpecificationSha256']=='e15ca367ce07647acc8675867170e15225a8d3917db7a3963018fad842d9cbb6','corrected independent C-byte basis, not repeated product')
    m=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==8 and not before&added and all(v['result']=='PASS' for v in p['cases']),'new quality identities only')
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
    require(QUALITY not in m['owners'] and q['originalTestSourceHashes'][QUALITY]==QUALITY_SHA==data.sha((data.ROOT/QUALITY).read_bytes()),'quality path separate')
    m['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=8,newExecs=1,newSourceNames=sorted(NAMES),existingSourceNames=[],qualityToolPath=QUALITY,qualityToolSha256=QUALITY_SHA,qualityToolNotCanonicalArtifact=True,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    m['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=8,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    cases=before|added;physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=m['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'disjoint complete source closures')
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=len(checks),registryInputNegativeLabels=checks,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+8,uniqueProductMethodDelta=8,newTestIds=8,sourceProgramDelta=2,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(not added&ordinary and len(cases&ordinary)==2806 and len(cases-ordinary)==119,'eight quality not ordinary progress')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=119);m['currentOrdinaryTestDeclarationReference']=decl
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']),m['measuredSourcePrograms'],m['measuredPhysical'],m['executablePhysical'],m['four100SourcePrograms'],m['four100Physical'],m['four100ExecutablePhysical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'],m['incompleteSourcePrograms'])==(2925,439,228,3080,155,71,7,629,1069,870,326,477,451,200,218,80),'current technical scope, no acceptance or old-source transfer')
    require(m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':564,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':236,'UNKNOWN':302},'no guessed owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','owners','fullSourceUnits','additionalScopeReferences','originalPostReferences','currentOrdinaryTestDeclarationReference','lastUpdateKind'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(units[n]==v for n,v in old['fullSourceUnits'].items()) and all(m['owners'][n]==v for n,v in old['owners'].items()),'all old source proofs, histories, repeats, costs and authority unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
