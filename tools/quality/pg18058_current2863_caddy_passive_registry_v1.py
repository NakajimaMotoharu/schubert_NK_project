"""Add one existing Source proof from an already-counted single exec; no new tests or executions."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg18050_caddy_exception_passive_post_v1 as measured
SOURCE=measured.SOURCE
PREV=('PG18038-current2863-query-catalogs-registry-v1','47186edd88f768984bd9aa8d946198c2880b84b51903bd023bb6cd7f57c61fc9')
PREV_POST=('PG18040-current2863-query-catalogs-registry-post-v1','07ce8f1563d4db10a61a74f04d58b1446f8b708a1d78bca74e02c702b4d7a685')
POST=('PG18050-caddy-exception-passive-post-v1','44dd5ce1b6c9d4f6eac7ab5044ee9fdff10ea292f825723625a48e3f457f6b30')
INDEPENDENT=('PG18052-caddy-exception-passive-independent-v1','c78ba416730171b13c38379a61c44252acc58c2b52bb14294f6b3effbb1158a5')
OUT=data.BASE/'PG18058-current2863-caddy-passive-registry-v1'
SCOPE='EXISTING_QUALIFIED_SINGLE_EXEC_PASSIVE_ONE_FIXED_EXCEPTION_SOURCE_NO_NEW_TESTS'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def require(ok,why):
    if not ok:raise ValueError(why)
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old,prior,p,q=[read(v) for v in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and q['postSha256']==POST[1] and q['semanticNegativeVectors']==20,'qualified same source lineage')
    require(measured.NAME not in old['fullSourceUnits'] and measured.PATH not in old['owners'],'first measurement existing Source')
    refs=[v for v in old['originalPostReferences'] if v['name']==measured.POST[0]]
    require(len(refs)==1 and refs[0]['sha256']==measured.POST[1] and refs[0]['execSha256']==p['execSha256'] and refs[0]['sessionIdentity']==p['sessionIdentity'],'original exec already counted, never new JVM/case')
    require(p['productTestsExecuted']==p['productTestsReexecuted']==p['newTestIds']==p['newJunitExecutions']==0 and p['targetUnitFour100'] is False and p['strictFour100GateExit']==1,'no replay or natural-zero strict promotion')
    m=copy.deepcopy(old);u=p['fullSourceUnits'][measured.NAME]
    m['fullSourceUnits'][measured.NAME]=dict(post=POST[0],postSha256=POST[1],physical=u['physical'],counters=u['totals'],four100=False,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],metadataOnly=False,branchNaturallyZero=True)
    m['owners'][measured.PATH]=p['owners'][measured.PATH]
    m['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),scope=SCOPE,newTests=0,newExecs=0,newSourceNames=[measured.NAME],existingSourceNames=[],originalAlreadyCountedPost=list(measured.POST),existingSingleExecSha256=p['execSha256'],productTestsReexecuted=0,additionalSharedCostPp=0,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False))
    units=m['fullSourceUnits'];physical={n for v in units.values() for n in v['physical']}
    require(len(physical)==sum(len(v['physical']) for v in units.values()),'disjoint full source closure')
    natural={n for v in units.values() if v['branchNaturallyZero'] for n in v['physical']}
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=2,registryInputNegativeLabels=['already-counted-exec-missing','source-already-measured'],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=1,measuredSourcePrograms=len(units),measuredPhysical=len(physical),executablePhysical=len(physical-m['metadataClasses'].keys()),naturalZeroBranchSourcePrograms=sum(v['branchNaturallyZero'] for v in units.values()),naturalZeroBranchPhysical=len(natural),ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    require((m['tests'],m['suites'],m['totalProductExecs'],m['totalMethodExecutions'],m['totalRepeatedOriginalMethods'],m['necessaryJointRepeatedMethods'],m['measuredSourcePrograms'],m['measuredPhysical'],m['executablePhysical'],m['four100SourcePrograms'],m['four100Physical'],m['naturalZeroBranchSourcePrograms'],m['naturalZeroBranchPhysical'],m['incompleteSourcePrograms'])==(2863,431,220,3018,155,71,597,1030,832,303,448,191,208,80),'actual unchanged test scope, one new natural-zero Source')
    require(m['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=532,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=236,UNKNOWN=302),'original canonical owner')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','measuredSourcePrograms','measuredPhysical','executablePhysical','naturalZeroBranchSourcePrograms','naturalZeroBranchPhysical','ownerStatusCounts','unknownOwnerPaths','lastUpdateKind','fullSourceUnits','owners','additionalScopeReferences'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in changed) and all(m['fullSourceUnits'][k]==v for k,v in old['fullSourceUnits'].items()) and all(m['owners'][k]==v for k,v in old['owners'].items()),'all prior cases/JVM/history/cost/authority unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
