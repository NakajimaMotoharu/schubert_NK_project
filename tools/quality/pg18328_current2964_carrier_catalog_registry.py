"""Add four public stored metadata Sources; no crypto, keyring or DB actions."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18308-current2959-web-terminal-flag-registry-v1','a463cf67fb028fe17452fec23ee2ddbd8cb8a458c6533fa70bae7b0592dc4933')
PREV_POST=('PG18310-current2959-web-terminal-flag-registry-post-v1','2ff8f372674c8d5eec2904da3f9acef8ed9f0fe5dd73241819cffd3d299c9770')
POST=('PG18322-carrier-catalog-five-post-v1','1131d023445e6e2cd2fb62a7976b337ffe92b8c27a41cea975ae4fecad35923b')
INDEPENDENT=('PG18324-carrier-catalog-five-independent-v1','60d67d701392914505d219e6a3d439b0dd2cbf165440ef76cae126069242e39b')
NAMES=set(["dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot","dev/codex/schubert/nk/api/maintenance/InboxMaintenanceException","dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException","dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration"])
CLOSURES={"dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot":["dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot","dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot$Detail","dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot$Inline"],"dev/codex/schubert/nk/api/maintenance/InboxMaintenanceException":["dev/codex/schubert/nk/api/maintenance/InboxMaintenanceException"],"dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException":["dev/codex/schubert/nk/api/logging/LogProjectionDatabaseException"],"dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration":["dev/codex/schubert/nk/web/config/ScenarioLogMvcConfiguration"]}
QUALITY='tools/quality/architecture/ScenarioCarrierSuccessContractTest.java'
QUALITY_SHA='5d3844a638c04c143a729b8e49450dc34db6697778ba7ed4b025a30f716ae28f'
QUALITY_PINS={"tools/quality/architecture/ScenarioCarrierSuccessContractTest.java":"5d3844a638c04c143a729b8e49450dc34db6697778ba7ed4b025a30f716ae28f","tools/quality/architecture/ProjectionFailureValueContractTest.java":"fdccaa0130f6740a1476002fc690f48c1560422b2b956bb4066e950d2999accf","tools/quality/architecture/InboxFailureValueContractTest.java":"72f318b93ec84fc8efdb368fb68d8e54636108ca3b6b64d2a08dd70710bdc52c","tools/quality/architecture/CompositeMvcBeanDeclarationContractTestV2.java":"1ddd5cd868852ec20ee2ac0bea71f0f1107a56067497a8276c89dc7e17ba40e4"}
SCOPE='ONE_EXEC_POSITIVE_CARRIER_CATALOG5_SOURCE4_NO_NULL_OR_CONTEXT_ACCEPTANCE'
OUT=data.BASE/'PG18328-current2964-carrier-catalog-registry-v1'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(value):return json.dumps(value,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    def profile(first):
        require(first==('PG18308-current2959-web-terminal-flag-registry-v1','a463cf67fb028fe17452fec23ee2ddbd8cb8a458c6533fa70bae7b0592dc4933') and all(v[0]!=OUT.name for v in [first,PREV_POST,POST,INDEPENDENT]),'literal independent input/output pairs')
    profile(PREV);checks=[]
    for first,label in [((OUT.name,PREV[1]),'self-reference'),((PREV[0],'0'*64),'wrong-predecessor-hash')]:
        try:profile(first)
        except ValueError:checks.append(label)
        else:raise ValueError('invalid input profile accepted')
    old,prior,p,q=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==51 and q['independentOracleVectors']==5,'genuine same-source independently qualified chain')
    require(p['tests']==5 and p['suites']==4 and set(p['fullSourceUnits'])==NAMES and not NAMES&set(old['fullSourceUnits']) and p['singleSession'] is True and p['crcMismatch']==p['forbiddenProductProbeHits']==0,'four new measured Sources, exact six cases')
    require(p['allMeasuredApplicableCountersCovered'] is True and p['strictFour100GateExit']==1 and p['targetUnitFour100'] is False and p['pureSuccessCarrierAndFixedCatalogOnly'] is True and p['actualAdminMutationOrAuthorization'] is p['actualBusinessProviderInvoked'] is p['actualThrowableGraphTraversal'] is False,'mixed natural-B0/one strict-four, pure values only')
    m=copy.deepcopy(old);before={(v['classname'],v['name']) for v in old['cases']};added={(v['classname'],v['name']) for v in p['cases']}
    require(len(added)==5 and not before&added and all(v['result']=='PASS' for v in p['cases']),'new quality identities only')
    units=m['fullSourceUnits']
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==CLOSURES[name] and u['threeCounter100'] is True and (u['four100'] is False and u['branchNaturallyZero'] is True),'exact source closure/categories')
        units[name]=dict(post=POST[0],postSha256=POST[1],physical=copy.deepcopy(u['physical']),counters=copy.deepcopy(u['totals']),four100=u['four100'],execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=u['branchNaturallyZero'] and u['threeCounter100'])
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    require(len(p['owners'])==4,'four target Main owners')
    for path,owner in p['owners'].items():
        require(owner['sha256']==hashes[path]==data.sha((data.ROOT/path).read_bytes()) and all(owner[k]==v for k,v in canonical(path,logical).items()) and owner['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE','exact approved original owner/cost pair, not change owner')
        require(path not in m['owners'],'four new scope owner references only');m['owners'][path]=copy.deepcopy(owner)
    require(q['originalTestSourceHashes']==QUALITY_PINS and all(path not in m['owners'] and data.sha((data.ROOT/path).read_bytes())==h for path,h in QUALITY_PINS.items()),'all four quality files separate and exact')
    m['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=5,newExecs=1,newSourceNames=sorted(NAMES),existingSourceNames=[],qualityToolPath=QUALITY,qualityToolSha256=QUALITY_SHA,qualityToolSourceHashes=QUALITY_PINS,priorFailedRawReference=['PG18320-carrier-catalog-five-pt-v1','01fd16320e3b840c6f1feed9407c06558f13adae8e09a29a0ce8b78871072fa4'],necessaryUnqualifiedPriorRepeats=4,qualityToolNotCanonicalArtifact=True,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    m['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=5,suites=4,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope=SCOPE))
    interface='dev/codex/schubert/nk/api/application/scenario/ScenarioQuerySnapshot'
    require(p['metadataClasses']==[interface] and interface not in m['metadataClasses'] and p['sourcePhysicalInventory'][interface]['flags']==1537 and p['sourcePhysicalInventory'][interface]['methods']==[],'one genuine empty interface, no Code omitted')
    m['metadataClasses'][interface]=dict(kind='NO_CODE',postSha256=POST[1],sha256=p['physicalClasses'][interface])
    cases=before|added;physical={n for u in units.values() for n in u['physical']};four={n for u in units.values() if u['four100'] for n in u['physical']};natural={n for u in units.values() if u['branchNaturallyZero'] for n in u['physical']};meta=m['metadataClasses']
    require(len(physical)==sum(len(u['physical']) for u in units.values()),'disjoint complete source closures')
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=len(checks),registryInputNegativeLabels=checks,cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+5,uniqueProductMethodDelta=5,newTestIds=5,sourceProgramDelta=4,measuredSourcePrograms=len(units),measuredPhysical=len(physical),metadataPhysical=len(meta),executablePhysical=len(physical-meta.keys()),four100SourcePrograms=sum(u['four100'] for u in units.values()),four100Physical=len(four),four100ExecutablePhysical=len(four-meta.keys()),naturalZeroBranchSourcePrograms=sum(u['branchNaturallyZero'] for u in units.values()),naturalZeroBranchPhysical=len(natural),incompleteSourcePrograms=sum(not(u['four100'] or u['branchNaturallyZero'] or u['metadataOnly']) for u in units.values()),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    decl=copy.deepcopy(old['currentOrdinaryTestDeclarationReference']);catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json']);ordinary={(v['className'],v['method']) for v in bindings}
    require(not added&ordinary and len(cases&ordinary)==2806 and len(cases-ordinary)==158,'six quality not ordinary progress')
    decl.update(ordinaryCaseReferences=2806,ordinaryWithoutCurrentCaseReference=2980,existingQualityFixtureCases=158);m['currentOrdinaryTestDeclarationReference']=decl
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],len(m['jointQualificationReferences']),m['measuredSourcePrograms'],m['measuredPhysical'],m['executablePhysical'],m['four100SourcePrograms'],m['four100Physical'],m['four100ExecutablePhysical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'],m['incompleteSourcePrograms'])==(2964,447,233,3119,155,71,7,646,1089,889,330,482,456,213,233,80),'current technical scope, no acceptance or old-source transfer')
    require(m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':581,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':236,'UNKNOWN':302},'no guessed owner')
    changed={'metadataClasses','metadataPhysical','invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','four100ExecutablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','owners','fullSourceUnits','additionalScopeReferences','originalPostReferences','currentOrdinaryTestDeclarationReference','lastUpdateKind'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(units[n]==v for n,v in old['fullSourceUnits'].items()) and all(m['owners'][n]==v for n,v in old['owners'].items()) and all(m['metadataClasses'][n]==v for n,v in old['metadataClasses'].items()),'all old source proofs, histories, repeats, costs and authority unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
