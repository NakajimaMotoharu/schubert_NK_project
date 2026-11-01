"""Resolve five resource duties and retain one explicitly noncanonical quality source separately."""
import collections
import copy
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18454-current3008-latest270-owner-correction-v1','0662e8e2912f48ef1d5619199a22edd1bbef34dcb45c7ef69b278936b7a40d51')
PREV_POST=('PG18456-current3008-latest270-owner-post-v1','17fde5da39646600b827b3c3c86d251ed58b8983e0633586e96f235a1e4c6518')
PROOF=('PG18470-residual-five-owner-and-tool-domain-v1','88aa11960f85ffc1dce95c29e465b3db1b4319b1cce9412b16cb9bc568df3e18')
OUT=data.BASE/'PG18472-current3008-resource-owner-domains-v1'
SCOPE='FIVE_RESOURCE_OWNER_CANDIDATES_ONE_NONCANONICAL_QUALITY_TRACE_NO_PT_OR_COVERAGE_CHANGE'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):
    import json
    return json.dumps(v,sort_keys=True)
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p=[read(v) for v in [PREV,PREV_POST,PROOF]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p]) and prior['registryManifestSha256']==PREV[1] and p['previousRegistrySha256']==PREV[1],'exact same current chain')
    rows=data.read_checked(data.BASE/PROOF[0]/'resource-owner-candidates.json',p['resourceCandidatesSha256']);quality=data.read_checked(data.BASE/PROOF[0]/'noncanonical-quality-source.json',p['qualityTraceSha256'])
    m=copy.deepcopy(old);changes=[]
    for row in rows:
        path=row['path'];require(m['owners'][path]==row['previousOwner'] and data.sha((data.ROOT/path).read_bytes())==row['sha256'],'exact current resource bytes and old owner')
        after=dict(sha256=row['sha256'],**row['resolvedCandidate']);changes.append(dict(path=path,previous=copy.deepcopy(m['owners'][path]),current=copy.deepcopy(after),subject=row['subject'],oldRuntimeTransferred=False));m['owners'][path]=after
    path=quality['path'];require(m['owners'][path]==quality['previousCanonicalTableRow'] and data.sha((data.ROOT/path).read_bytes())==quality['sha256'],'quality source still retained exact')
    m['owners'].pop(path)
    m['additionalScopeReferences'].append(dict(name=PROOF[0],sha256=PROOF[1],scope=SCOPE,ownerCorrections=changes,nonCanonicalQualityTrace=quality,canonicalOwnerRowsBefore=len(old['owners']),canonicalOwnerRowsAfter=len(m['owners']),allTraceRowsRetainedAcrossDomains=True,newTests=0,newExecs=0,newSourceNames=[],existingSourceNames=[],additionalSharedCostPp=0,actualAllocatedPp=None,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False,oldRuntimeTransferred=False))
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=0,registryInputNegativeLabels=[],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    require(len(old['owners'])==1123 and len(m['owners'])==1122 and len(changes)==5 and set(m['owners'])|{path}==set(old['owners']),'one canonical-domain correction, all trace paths preserved')
    require(m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':537} and m['unknownOwnerPaths']==0,'five owner candidates, one separate quality trace, not six assigned owners')
    allowed={'owners','ownerStatusCounts','unknownOwnerPaths','additionalScopeReferences','invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','lastUpdateKind'}
    require(set(m)==set(old) and all(wire(m[k])==wire(v) for k,v in old.items() if k not in allowed),'every PT/case/physical/counter/source/cost/formal field unchanged')
    changed={r['path'] for r in changes}|{path};require(all(m['owners'][p]==v for p,v in old['owners'].items() if p not in changed),'all other owner rows unchanged')
    for v in [old,prior,p]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
