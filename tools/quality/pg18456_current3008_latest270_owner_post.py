"""Independent24 ownership reconciliation; complete old runtime/counter/cost facts remain byte-equal."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
REG=('PG18454-current3008-latest270-owner-correction-v1','0662e8e2912f48ef1d5619199a22edd1bbef34dcb45c7ef69b278936b7a40d51')
PREV=('PG18434-current3008-owner24-correction-v1','598adca1e798cc76c586096744efd66337cd9c5c5b6e03382ec78503f3bfa1d3')
PREV_POST=('PG18436-current3008-owner24-post-v1','f0f3039f0cf46f7682c9d26c94122bee0374c6901e77fe8230a6a489d01b51a1')
PREFLIGHT=('PG18450-latest-explicit270-owner-preflight-v1','d6df2f07c40985094c229bf407b47e3601a5253fca370c5d2b97a6fb8ccad769')
QUAL=('PG18452-latest-primary-rules270-qualified-v1','1d29bf436618a1e0f5e7d488e40791b799239035d8a7bd1140fd6e88de3ff51a')
ORIGINAL=('PG13846-snapshot-program-trace-v1','f075dc40f990fb89f449d6da6a58d50dd4a129cb2bc2b619f30d7d3b51d8c107')
OUT=data.BASE/'PG18456-current3008-latest270-owner-post-v1'
SCOPE='EXPLICIT_LATEST_PRIMARY270_SAME_BYTE_OWNER_CANDIDATES_NO_RUNTIME_TRANSFER'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q,m,original=[read(pair) for pair in [PREV,PREV_POST,PREFLIGHT,QUAL,REG,ORIGINAL]]
    require(all(v['actualExit']==0 for v in [old,prior,p,q,m,original]) and all(v['source']==SOURCE for v in [old,prior,p,q,m]) and original['source']=='0061d178cda80c2ce3926290619c64db125dbcfc','old/current domains separate')
    require(prior['registryManifestSha256']==PREV[1] and q['preflightManifestSha256']==PREFLIGHT[1] and q['positiveAndPriorityVectors']==276 and q['negativeAndImmutabilityVectors']==13,'qualified exact references')
    rows=data.read_checked(data.BASE/PREFLIGHT[0]/'selected-owner-bridges.json',p['selectedBridgesSha256'])
    deferred=data.read_checked(data.BASE/PREFLIGHT[0]/'deferred-owner-reasons.json',p['deferredReasonsSha256'])
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json',p['normalManifestSha256'])
    original_rows={r['path']:r for r in original['sourceRows']};selected={r['path'] for r in rows}
    require(len(rows)==len(selected)==270 and len(deferred)==6 and len({r['path'] for r in deferred})==6 and not selected&{r['path'] for r in deferred},'complete disjoint300')
    require(selected|{r['path'] for r in deferred}=={path for path,r in old['owners'].items() if r['ownershipStatus']=='UNKNOWN'},'all original unknown scope accounted')
    require(collections.Counter(r['reason'] for r in deferred)=={'NOT_IN_FIXED_ORIGINAL_REGISTRY':6},'no hidden held success or guesses for missing/changed evidence')
    expected=copy.deepcopy(old);changes=[]
    for r in rows:
        path=r['path'];require(not any(s in path for s in ['RootFailed','/private/','.private.','SnapshotKeyCloseWitness','pg9892_']),'bounded names first')
        previous=original_rows[path]
        require(wire(previous)==wire(r['originalExplicitRecord']) and previous['sha256']==normal['begin']['inputHashes'][path]==data.sha((data.ROOT/path).read_bytes())==r['sha256'],'original complete record/current exact bytes')
        require(previous['canonicalOwner']==previous['canonicalCostOwner'] and previous['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED','explicit candidate only')
        require((previous.get('currentSourcePtQualificationInferred') is None or previous.get('currentSourcePtQualificationInferred') is False) and previous['historicalCostsReallocated'] is previous['historicalRunReassigned'] is False and previous['additionalSharedCostPp']==0 and previous['actualAllocatedPp'] is None,'no runtime/cost transfer')
        require(r['previousUnknownOwner']==old['owners'][path] and old['owners'][path]['ownershipStatus']=='UNKNOWN','exact previous owner')
        resolved=dict(canonicalOwner=previous['canonicalOwner'],canonicalCostOwner=previous['canonicalCostOwner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='EXPLICIT_CURRENT_PRIMARY_13846_SAME_BYTE_ONLY:'+previous['basis'])
        require(r['resolvedCandidate']==resolved,'independent candidate reconstruction, not resolver result as expected')
        after=dict(sha256=r['sha256'],**resolved);expected['owners'][path]=after
        changes.append(dict(path=path,previous=copy.deepcopy(old['owners'][path]),current=copy.deepcopy(after),originalExplicitBasis=previous['basis'],originalExplicitRegistrySha256=ORIGINAL[1],oldRuntimeTransferred=False))
    expected['additionalScopeReferences'].append(dict(name=PREFLIGHT[0],sha256=PREFLIGHT[1],qualifiedResolverReference=list(QUAL),scope=SCOPE,ownerCorrections=changes,newTests=0,newExecs=0,newSourceNames=[],existingSourceNames=[],additionalSharedCostPp=0,actualAllocatedPp=None,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False,oldRuntimeTransferred=False))
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=0,registryInputNegativeLabels=[],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),lastUpdateKind=SCOPE)
    require(expected['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':532,'UNKNOWN':6},'24 only, no baseline/acceptance change')
    def contract(v):require(wire(v)==wire(expected),'all exact current owner corrections and every old technical/cost field')
    contract(m);labels=[]
    keys=['source','tests','suites','totalProductExecs','totalMethodExecutions','totalRepeatedOriginalMethods','necessaryJointRepeatedMethods','cases','suiteNames','fullSourceUnits','metadataClasses','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','owners','additionalScopeReferences','jointQualificationReferences','qualificationReplacedUnitHistory','resourceOnlyReferences','javascriptResourceDomain','currentOrdinaryTestDeclarationReference','newAccepted','formalUpdated','effortPercent','sourceProgramDelta','newTestIds','uniqueProductMethodDelta','lastUpdateKind']
    for key in keys:
        bad=copy.deepcopy(m);value=bad[key];bad[key]=not value if type(value) is bool else None if value is not None else 1
        require(wire(bad)!=wire(m),'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false metadata '+key)
    boundary=[]
    for label,change in [('baseline-promotion',lambda v:v['owners'][next(iter(selected))].update(ownershipStatus='BASELINE_LOGICAL_REFERENCE')),('cost-reassignment',lambda v:v['owners'][next(iter(selected))].update(canonicalCostOwner='WBS-F03')),('old-runtime-transfer',lambda v:v['additionalScopeReferences'][-1].update(oldRuntimeTransferred=True)),('new-exec',lambda v:v['additionalScopeReferences'][-1].update(newExecs=1))]:
        bad=copy.deepcopy(m);change(bad)
        try:contract(bad)
        except ValueError:boundary.append(label)
        else:raise ValueError('false boundary '+label)
    def input_ref(pair):require(pair==REG,'immutable exact registry input')
    input_ref(REG);inputs=[]
    for pair in [(OUT.name,REG[1]),(REG[0],'0'*64)]:
        try:input_ref(pair)
        except ValueError:inputs.append(pair[0])
        else:raise ValueError('false input profile')
    for value in [old,prior,p,q,m,original]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=REG[1],summary={k:m[k] for k in prior['summary']},metadataNegativeVectors=len(labels),negativeLabels=labels,replacementBoundaryNegativeVectors=len(boundary),replacementBoundaryNegativeLabels=boundary,registryInputNegativeVectors=len(inputs),newSourcePrograms=0,singleExecSourceReplacements=0,previousSourceProofsNotReplaced=True,previousProofsPreservedInHistory=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,currentOrdinaryTestDeclarationReference=m['currentOrdinaryTestDeclarationReference'],existingOwnerCandidatesResolved=270,deferredUnknown=6,deferredExistingEvidenceMissing=6,deferredCurrentBytesDiffer=0,originalQualificationFlagUnknownCount=5,qualificationOfThoseRecordsInferred=False,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
