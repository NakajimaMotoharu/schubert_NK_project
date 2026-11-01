"""Independent five resource owner references and one noncanonical trace, with whole registry equality."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
REG=('PG18472-current3008-resource-owner-domains-v1','51a94c21c7ef67d0ff4254cc071abaf18d18b65884b31601ec6d77eda3863c1f')
PREV=('PG18454-current3008-latest270-owner-correction-v1','0662e8e2912f48ef1d5619199a22edd1bbef34dcb45c7ef69b278936b7a40d51')
PREV_POST=('PG18456-current3008-latest270-owner-post-v1','17fde5da39646600b827b3c3c86d251ed58b8983e0633586e96f235a1e4c6518')
PROOF=('PG18470-residual-five-owner-and-tool-domain-v1','88aa11960f85ffc1dce95c29e465b3db1b4319b1cce9412b16cb9bc568df3e18')
OUT=data.BASE/'PG18474-current3008-resource-owner-domains-post-v1'
SCOPE='FIVE_RESOURCE_OWNER_CANDIDATES_ONE_NONCANONICAL_QUALITY_TRACE_NO_PT_OR_COVERAGE_CHANGE'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,m=[read(pair) for pair in [PREV,PREV_POST,PROOF,REG]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,m]) and prior['registryManifestSha256']==PREV[1] and p['previousRegistrySha256']==PREV[1],'same current source')
    rows=data.read_checked(data.BASE/PROOF[0]/'resource-owner-candidates.json',p['resourceCandidatesSha256']);quality=data.read_checked(data.BASE/PROOF[0]/'noncanonical-quality-source.json',p['qualityTraceSha256'])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json',p['normalManifestSha256'])
    expected=copy.deepcopy(old);changes=[];expected_paths=set()
    stems=['log-search-validation','operation-post-submit','question-input-validation','search-speaker-submit']
    for row in rows:
        path=row['path'];expected_paths.add(path)
        require(row['previousOwner']==old['owners'][path] and old['owners'][path]['ownershipStatus']=='UNKNOWN' and data.sha((data.ROOT/path).read_bytes())==normal['begin']['inputHashes'][path]==row['sha256'],'all exact resource source bytes')
        if path.endswith('.test.cjs'):
            stem=path.rsplit('/',1)[1].removesuffix('.test.cjs');require(stem in stems,'exact four JS resources')
            subject='src/schubert-nk-web/src/main/resources/static/js/'+stem+'.js'
            text=(data.ROOT/path).read_text();require('const script = path.resolve(__dirname, "../../main/resources/static/js/'+stem+'.js");' in text and 'const source = fs.readFileSync(script, "utf8");' in text,'direct fixed source reference')
            require(subject==row['subject'] and logical[subject]['owner']==logical[subject]['costOwner']=='WBS-P016-25' and row['originalLogicalSubject']==logical[subject],'explicit original shared JS responsibility')
            require(data.sha((data.ROOT/subject).read_bytes())==normal['begin']['inputHashes'][subject]==row['currentSubjectSha256'],'current main JS bytes')
            resolved=dict(canonicalOwner='WBS-P016-25',canonicalCostOwner='WBS-P016-25',ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='EXACT_FIXED_JS_ASSET_REFERENCE_ORIGINAL_941_P01625')
        else:
            require(path=='src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt','one fixed golden only')
            consumer='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshotTest.java';subject='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.java'
            require(row['consumer']==consumer and row['subject']==subject and logical[subject]['owner']==logical[subject]['costOwner']=='WBS-P004-04','actual consumer and original Main, not unrelated UnitStateParser')
            text=(data.ROOT/consumer).read_text();require('getResourceAsStream("/inspector/unit-golden.txt")' in text and '2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6' in text and len((data.ROOT/path).read_bytes())==373,'fixed independent golden')
            require(data.sha((data.ROOT/consumer).read_bytes())==normal['begin']['inputHashes'][consumer]==row['currentConsumerSha256']==row['originalConsumerRecord']['sha256'] and row['originalConsumerRecord']['canonicalOwner']==row['originalConsumerRecord']['canonicalCostOwner']=='WBS-P004-04','current exact consumer evidence')
            resolved=dict(canonicalOwner='WBS-P004-04',canonicalCostOwner='WBS-P004-04',ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='EXACT_373_BYTE_INSPECTOR_GOLDEN_CONSUMER_AND_ORIGINAL_MAIN_P00404')
        require(row['resolvedCandidate']==resolved and row['oldRuntimeTransferred'] is False,'independent owner reconstruction, not SUT expected')
        after=dict(sha256=row['sha256'],**resolved);expected['owners'][path]=after
        changes.append(dict(path=path,previous=copy.deepcopy(old['owners'][path]),current=copy.deepcopy(after),subject=row['subject'],oldRuntimeTransferred=False))
    tool='tools/quality/architecture/ProtocolCarrierBoundaryTest.java'
    require(len(rows)==len(expected_paths)==5 and tool==quality['path'] and quality['previousCanonicalTableRow']==old['owners'][tool] and quality['sha256']==data.sha((data.ROOT/tool).read_bytes()),'all six trace paths')
    require(quality['role']=='QUALITY_TEST_SOURCE_NOT_LOGICAL_ARTIFACT' and quality['canonicalOwner'] is quality['canonicalCostOwner'] is None and quality['casesRemoved']==quality['physicalClassesRemoved']==quality['coverageExclusionsAdded']==0,'not a scope/coverage exclusion or assigned canonical owner')
    require(tool not in logical and tool not in normal['begin']['inputHashes'] and old['owners'][tool]['basis']=='EXACT_NEW_TOOL_PT_NOT_LOGICAL_ARTIFACT_NO_OWNER_INFERENCE','already explicit noncanonical source')
    require(quality['existingCases']==[r for r in old['cases'] if r['classname']=='dev.codex.schubert.nk.protocol.layout.ProtocolCarrierBoundaryTest'] and quality['testId']=='PT-OPS-2789','all original quality cases remain')
    expected['owners'].pop(tool)
    expected['additionalScopeReferences'].append(dict(name=PROOF[0],sha256=PROOF[1],scope=SCOPE,ownerCorrections=changes,nonCanonicalQualityTrace=quality,canonicalOwnerRowsBefore=len(old['owners']),canonicalOwnerRowsAfter=len(expected['owners']),allTraceRowsRetainedAcrossDomains=True,newTests=0,newExecs=0,newSourceNames=[],existingSourceNames=[],additionalSharedCostPp=0,actualAllocatedPp=None,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False,oldRuntimeTransferred=False))
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=0,registryInputNegativeLabels=[],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),lastUpdateKind=SCOPE)
    require(len(expected['owners'])==1122 and set(expected['owners'])|{tool}==set(old['owners']) and expected['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':537} and expected['unknownOwnerPaths']==0,'denominator1122 plus separate quality1, not six new owners')
    def contract(v):require(wire(v)==wire(expected),'all exact resource owner corrections and every old PT/scope/cost/acceptance field')
    contract(m);labels=[]
    keys=['source','tests','suites','totalProductExecs','totalMethodExecutions','totalRepeatedOriginalMethods','necessaryJointRepeatedMethods','cases','suiteNames','fullSourceUnits','metadataClasses','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','owners','additionalScopeReferences','jointQualificationReferences','qualificationReplacedUnitHistory','resourceOnlyReferences','javascriptResourceDomain','currentOrdinaryTestDeclarationReference','newAccepted','formalUpdated','effortPercent','sourceProgramDelta','newTestIds','uniqueProductMethodDelta','lastUpdateKind']
    for key in keys:
        bad=copy.deepcopy(m);value=bad[key];bad[key]=not value if type(value) is bool else None if value is not None else 1
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false metadata '+key)
    boundary=[]
    for label,change in [('quality-trace-erased',lambda v:v['additionalScopeReferences'][-1].update(nonCanonicalQualityTrace={})),('quality-as-production',lambda v:v['owners'].update({tool:dict(sha256=quality['sha256'],canonicalOwner='WBS-F03',canonicalCostOwner='WBS-F03',ownershipStatus='BASELINE_LOGICAL_REFERENCE',basis='WRONG')})),('wrong-resource-cost',lambda v:v['owners'][next(iter(expected_paths))].update(canonicalCostOwner='WBS-F03')),('coverage-exclusion',lambda v:v['additionalScopeReferences'][-1]['nonCanonicalQualityTrace'].update(coverageExclusionsAdded=1))]:
        bad=copy.deepcopy(m);change(bad)
        try:contract(bad)
        except ValueError:boundary.append(label)
        else:raise ValueError('false boundary '+label)
    def ref(pair):require(pair==REG,'exact new registry input')
    ref(REG);inputs=[]
    for pair in [(OUT.name,REG[1]),(REG[0],'0'*64)]:
        try:ref(pair)
        except ValueError:inputs.append(pair[0])
        else:raise ValueError('false input')
    for value in [old,prior,p,m]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=REG[1],summary={k:m[k] for k in prior['summary']},metadataNegativeVectors=len(labels),negativeLabels=labels,replacementBoundaryNegativeVectors=len(boundary),replacementBoundaryNegativeLabels=boundary,registryInputNegativeVectors=len(inputs),newSourcePrograms=0,singleExecSourceReplacements=0,previousSourceProofsNotReplaced=True,previousProofsPreservedInHistory=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,currentOrdinaryTestDeclarationReference=m['currentOrdinaryTestDeclarationReference'],resourceOwnerCandidatesResolved=5,nonCanonicalQualityTracePreserved=1,canonicalOwnerRows=1122,allOriginal1123TraceRowsRetained=True,coverageExclusionsAdded=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
