"""Correct only two evidenced existing Test-owner candidates, preserving all PT and old proof history."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
import trace_owner_explicit_query_v2 as rules
from host_tool_invocation import capture,verify

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18388-current3008-weblog-claim-registry-v1','f561fa5e450285c6811f195c5a68670f1ddd090ef8782ce2a0815e6b1766b2b6')
PREV_POST=('PG18390-current3008-weblog-claim-registry-post-v1','a99dc83c54be418b7ee45846dae92f7e746a224ae30d6c885311d14507cd98f1')
QUAL=('PG18410-explicit-user-query-owner-v1','847c9b714d2da7d5ba12aac72298104f45940aa421b22ee0ff223b1258f5a128')
OUT=data.BASE/'PG18412-current3008-two-owner-correction-v1'
SCOPE='EXPLICIT_EXISTING_USER_QUERY_TEST_OWNERS_NO_RUNTIME_OR_ACCEPTANCE_TRANSFER'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,q=[read(p) for p in [PREV,PREV_POST,QUAL]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,q]) and prior['registryManifestSha256']==PREV[1] and q['previousTechnicalRegistrySha256']==PREV[1] and q['qualifiedToolVectors']==14,'exact old technical and new tool qualification')
    rows=data.read_checked(data.BASE/QUAL[0]/'owner-bridges.json',q['ownerBridgesSha256'])
    require({r['path'] for r in rows}==set(rules.RULES) and len(rows)==2,'exact two old candidate paths')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    m=copy.deepcopy(old);changes=[]
    for row in rows:
        path=row['path'];require(m['owners'][path]==row['previousOwner'] and data.sha((data.ROOT/path).read_bytes())==row['sha256'],'same-byte original UNKNOWN')
        new=rules.canonical(path,logical,row['sha256']);require(new==row['resolvedOwner'],'same qualified rule')
        after=dict(sha256=row['sha256'],**new);before=copy.deepcopy(m['owners'][path]);m['owners'][path]=after
        changes.append(dict(path=path,previous=before,current=copy.deepcopy(after),methodTestIds=row['methodTestIds'],independentSpecification=row['independentSpecification'],originalExplicitRegistrySha256=q['originalExplicitRegistrySha256'],oldRuntimeTransferred=False))
    m['additionalScopeReferences'].append(dict(name=QUAL[0],sha256=QUAL[1],scope=SCOPE,ownerCorrections=changes,newTests=0,newExecs=0,newSourceNames=[],existingSourceNames=[],additionalSharedCostPp=0,actualAllocatedPp=None,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False,oldRuntimeTransferred=False))
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=0,registryInputNegativeLabels=[],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    require(m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':238,'UNKNOWN':300} and m['unknownOwnerPaths']==300,'two only candidate corrections')
    allowed={'owners','ownerStatusCounts','unknownOwnerPaths','additionalScopeReferences','invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','lastUpdateKind'}
    require(all(wire(m[k])==wire(v) for k,v in old.items() if k not in allowed) and set(m)==set(old),'all cases/source/counters/costs/formal/acceptance/history preserved')
    require(all(m['owners'][p]==v for p,v in old['owners'].items() if p not in rules.RULES),'all other 1121 owner rows unchanged')
    for v in [old,prior,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
