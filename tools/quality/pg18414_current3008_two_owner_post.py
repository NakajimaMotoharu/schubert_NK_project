"""Independent whole-registry comparison: exact two owner corrections, no case or runtime delta."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
REG=('PG18412-current3008-two-owner-correction-v1','48d59ab03dc8b6ae3ba9bbc2ebe9e9fc03dfc362485ec46449883fb4e3548d05')
PREV=('PG18388-current3008-weblog-claim-registry-v1','f561fa5e450285c6811f195c5a68670f1ddd090ef8782ce2a0815e6b1766b2b6')
PREV_POST=('PG18390-current3008-weblog-claim-registry-post-v1','a99dc83c54be418b7ee45846dae92f7e746a224ae30d6c885311d14507cd98f1')
QUAL=('PG18410-explicit-user-query-owner-v1','847c9b714d2da7d5ba12aac72298104f45940aa421b22ee0ff223b1258f5a128')
OUT=data.BASE/'PG18414-current3008-two-owner-post-v1'
SCOPE='EXPLICIT_EXISTING_USER_QUERY_TEST_OWNERS_NO_RUNTIME_OR_ACCEPTANCE_TRANSFER'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,q,m=[read(p) for p in [PREV,PREV_POST,QUAL,REG]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,q,m]) and prior['registryManifestSha256']==PREV[1] and q['qualifiedToolVectors']==14,'same current technical source and qualified tool')
    rows=data.read_checked(data.BASE/QUAL[0]/'owner-bridges.json',q['ownerBridgesSha256'])
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json',q['normalManifestSha256'])
    prefix='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
    exact={prefix+'UserQueryCanonicalCoreTest.java':('bff3bdd906735fc3b2b49d52f7a00ac7f1dad8a2ae515535eee09cb2660b42a1','EXPLICIT_2012_CORE001_004_AND_2014_SAME_BYTE_USER_QUERY_P01001'),prefix+'UserQueryResponseBoundaryTest.java':('72a9ccd0477fd81896d59d24224f14fb9e261ca9ad6a23a1d8e992ae8e93a1a1','EXPLICIT_2008_VAL001_004_AND_2014_SAME_BYTE_USER_QUERY_P01001')}
    require(len(rows)==2 and {r['path'] for r in rows}==set(exact),'exact two, not all UNKNOWN or class-name inference')
    expected=copy.deepcopy(old);changes=[];case_set={(c['classname'],c['name']) for c in old['cases']}
    for row in rows:
        path=row['path'];pin,basis=exact[path]
        require(data.sha((data.ROOT/path).read_bytes())==pin==normal['begin']['inputHashes'][path]==row['sha256'],'normal/full current bytes')
        require(row['previousOwner']==old['owners'][path] and row['previousOwner']['ownershipStatus']=='UNKNOWN','old exact UNKNOWN rows retained')
        resolved=dict(canonicalOwner='WBS-P010-01',canonicalCostOwner='WBS-P010-01',ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis=basis)
        require(row['resolvedOwner']==resolved and row['originalExplicitOwner']=='WBS-P010-01' and row['oldRuntimeTransferred'] is False and row['additionalSharedCostPp']==0 and row['actualAllocatedPp'] is None,'original explicit candidate not current acceptance/cost')
        classname=path.split('/java/',1)[1][:-5].replace('/','.')
        require(len(row['currentDeclaredMethods'])==4 and all((classname,n) in case_set for n in row['currentDeclaredMethods']),'existing current cases only, not new execution')
        after=dict(sha256=pin,**resolved);expected['owners'][path]=after
        changes.append(dict(path=path,previous=copy.deepcopy(old['owners'][path]),current=after,methodTestIds=row['methodTestIds'],independentSpecification=row['independentSpecification'],originalExplicitRegistrySha256=q['originalExplicitRegistrySha256'],oldRuntimeTransferred=False))
    expected['additionalScopeReferences'].append(dict(name=QUAL[0],sha256=QUAL[1],scope=SCOPE,ownerCorrections=changes,newTests=0,newExecs=0,newSourceNames=[],existingSourceNames=[],additionalSharedCostPp=0,actualAllocatedPp=None,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False,oldRuntimeTransferred=False))
    expected.update(invocation=m['invocation'],previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=0,registryInputNegativeLabels=[],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in expected['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in expected['owners'].values()),lastUpdateKind=SCOPE)
    require(expected['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':238,'UNKNOWN':300},'only two candidates; all others unchanged')
    def contract(v):require(wire(v)==wire(expected),'all exact owner corrections and old technical/acceptance/cost fields')
    contract(m);labels=[]
    keys=['source','tests','suites','totalProductExecs','totalMethodExecutions','totalRepeatedOriginalMethods','necessaryJointRepeatedMethods','cases','suiteNames','fullSourceUnits','metadataClasses','measuredSourcePrograms','measuredPhysical','executablePhysical','four100SourcePrograms','four100Physical','naturalZeroBranchPhysical','incompleteSourcePrograms','ownerStatusCounts','unknownOwnerPaths','owners','additionalScopeReferences','jointQualificationReferences','qualificationReplacedUnitHistory','resourceOnlyReferences','javascriptResourceDomain','currentOrdinaryTestDeclarationReference','newAccepted','formalUpdated','effortPercent','sourceProgramDelta','newTestIds','uniqueProductMethodDelta','lastUpdateKind']
    for key in keys:
        bad=copy.deepcopy(m);old_value=bad[key]
        bad[key]=not old_value if type(old_value) is bool else None if old_value is not None else 1
        require(wire(bad)!=wire(m),'nondegenerate '+key)
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false registry '+key)
    boundary=[]
    for label,change in [('baseline-promotion',lambda v:v['owners'][next(iter(exact))].update(ownershipStatus='BASELINE_LOGICAL_REFERENCE')),('cost-reassignment',lambda v:v['owners'][next(iter(exact))].update(canonicalCostOwner='WBS-F03')),('old-qualification-transfer',lambda v:v['additionalScopeReferences'][-1].update(oldRuntimeTransferred=True)),('new-exec',lambda v:v['additionalScopeReferences'][-1].update(newExecs=1))]:
        bad=copy.deepcopy(m);change(bad)
        try:contract(bad)
        except ValueError:boundary.append(label)
        else:raise ValueError('false boundary '+label)
    def input_ref(pair):require(pair==REG,'exact immutable registry input, not output or alternate source')
    input_ref(REG);inputs=[]
    for pair in [(OUT.name,REG[1]),(REG[0],'0'*64)]:
        try:input_ref(pair)
        except ValueError:inputs.append(pair[0])
        else:raise ValueError('false registry input')
    for value in [old,prior,q,m]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,registryManifestSha256=REG[1],summary={k:m[k] for k in prior['summary']},metadataNegativeVectors=len(labels),negativeLabels=labels,replacementBoundaryNegativeVectors=len(boundary),replacementBoundaryNegativeLabels=boundary,registryInputNegativeVectors=len(inputs),newSourcePrograms=0,singleExecSourceReplacements=0,previousSourceProofsNotReplaced=True,previousProofsPreservedInHistory=True,originalMethodsReexecutedByRegistry=0,coverageExecUnion=False,currentOrdinaryTestDeclarationReference=m['currentOrdinaryTestDeclarationReference'],existingOwnerCandidatesResolved=2,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print(len(labels))
if __name__=='__main__':main()
