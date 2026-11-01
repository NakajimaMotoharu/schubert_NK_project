"""Add four public stored metadata Sources; no crypto, keyring or DB actions."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18278-current2955-revoke-values-registry-v1','1f8ddb95b0f15c064e702f6ace5023309575a4ddb3796bdb4c8fec1cda26ade3')
PREV_POST=('PG18280-current2955-revoke-values-registry-post-v1','3a1b0bde1131fe01db59eaaf82dbb6e02a87cf95b6b5df5da0e60629f688b78b')
POST=('PG18302-web-terminal-flag-four-post-v1','df15b6c4de3afa0ddcddd150564a9b9ff860737950ecc907cbeda100b20d5777')
INDEPENDENT=('PG18304-web-terminal-flag-four-independent-v1','5388221a81fe80ae03f3379bd197be6f8a7569e1b68ea4513ddba312da0d1682')
NAMES=set(["dev/codex/schubert/nk/web/bootstrap/WebRuntimeFailureSignal"])
QUALITY='tools/quality/architecture/WebTerminalFlagContractTest.java'
QUALITY_SHA='96e51d13830a50e2837a1bfdb6e789392927c2952ae9b265be47ef9e485c70d0'
SCOPE='ONE_EXEC_WEB_TERMINAL_FLAG4_SOURCE1_SELF_OWNED_EXECUTOR_NO_NATIVE'
OUT=data.BASE/'PG18308-current2959-web-terminal-flag-registry-v1'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    def profile(first):
        require(first==('PG18278-current2955-revoke-values-registry-v1','1f8ddb95b0f15c064e702f6ace5023309575a4ddb3796bdb4c8fec1cda26ade3') and all(v[0]!=OUT.name for v in [first,PREV_POST,POST,INDEPENDENT]),'literal independent input/output pairs')
    profile(PREV);checks=[]
    for first,label in [((OUT.name,PREV[1]),'self-reference'),((PREV[0],'0'*64),'wrong-predecessor-hash')]:
        try:profile(first)
        except ValueError:checks.append(label)
        else:raise ValueError('invalid input profile accepted')
    old,prior,p,q=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==45 and q['independentOracleVectors']==4,'genuine same-source independently qualified chain')
    require(p['tests']==4 and p['suites']==1 and set(p['fullSourceUnits'])==NAMES and not NAMES&set(old['fullSourceUnits']) and p['singleSession'] is True and p['crcMismatch']==p['forbiddenProductProbeHits']==0,'four new measured Sources, exact six cases')
    require(p['allMeasuredApplicableCountersCovered'] is True and p['strictFour100GateExit']==1 and p['targetUnitFour100'] is False and p['pureCapturedTerminalFlagOnly'] is True and p['actualAdminMutationOrAuthorization'] is p['actualBusinessProviderInvoked'] is p['actualThrowableGraphTraversal'] is False,'mixed natural-B0/one strict-four, pure values only')
    m=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==4 and not before&added and all(v['result']=='PASS' for v in p['cases']),'new quality identities only')
    units=m['fullSourceUnits']
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==[name] and u['threeCounter100'] is True and (u['four100'] is False and u['branchNaturallyZero'] is True),'exact source closure/categories')
        units[name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(len(p['owners'])==1,'four target Main owners')
    for path,owner in p['owners'].items():
        require(owner['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(owner[k]==v for k,v in canonical(path,logical).items()) and owner['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','exact approved original owner/cost pair, not change owner')
        require(path not in m['owners'],'four new scope owner references only');m['owners'][path]=copy.deepcopy(owner)
    require(QUALITY not in m['owners'] and q['originalTestSourceHashes'][QUALITY]==QUALITY_SHA==data.sha((data.ROOT/QUALITY).read_bytes()),'quality path separate')
    m['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=4,newExecs=1,newSourceNames=sorted(NAMES),existingSourceNames=[],qualityToolPath=QUALITY,qualityToolSha256=QUALITY_SHA,qualityToolNotCanonicalArtifact=True,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    m['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=4,suites=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    cases=before|added;physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=m['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'disjoint complete source closures')
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=len(checks),registryInputNegativeLabels=checks,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+4,uniqueProductMethodDelta=4,newTestIds=4,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(not added&ordinary and len(cases&ordinary)==2806 and len(cases-ordinary)==153,'six quality not ordinary progress')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=153);m['currentOrdinaryTestDeclarationReference']=decl
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']),m['measuredSourcePrograms'],m['measuredPhysical'],m['executablePhysical'],m['four100SourcePrograms'],m['four100Physical'],m['four100ExecutablePhysical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'],m['incompleteSourcePrograms'])==(2959,443,232,3114,155,71,7,642,1083,884,330,482,456,209,227,80),'current technical scope, no acceptance or old-source transfer')
    require(m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':577,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':236,'UNKNOWN':302},'no guessed owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','owners','fullSourceUnits','additionalScopeReferences','originalPostReferences','currentOrdinaryTestDeclarationReference','lastUpdateKind'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(units[n]==v for n,v in old['fullSourceUnits'].items()) and all(m['owners'][n]==v for n,v in old['owners'].items()),'all old source proofs, histories, repeats, costs and authority unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
