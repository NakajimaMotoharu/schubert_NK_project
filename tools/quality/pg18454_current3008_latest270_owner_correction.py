"""Apply only24 qualified same-byte historical candidate-owner mappings; all runtime facts unchanged."""
import collections
import copy
import json
import g07_host_class_provenance_inputs as data
import trace_owner_latest_primary_v4 as resolver
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18434-current3008-owner24-correction-v1','598adca1e798cc76c586096744efd66337cd9c5c5b6e03382ec78503f3bfa1d3')
PREV_POST=('PG18436-current3008-owner24-post-v1','f0f3039f0cf46f7682c9d26c94122bee0374c6901e77fe8230a6a489d01b51a1')
PREFLIGHT=('PG18450-latest-explicit270-owner-preflight-v1','d6df2f07c40985094c229bf407b47e3601a5253fca370c5d2b97a6fb8ccad769')
QUAL=('PG18452-latest-primary-rules270-qualified-v1','1d29bf436618a1e0f5e7d488e40791b799239035d8a7bd1140fd6e88de3ff51a')
OUT=data.BASE/'PG18454-current3008-latest270-owner-correction-v1'
SCOPE='EXPLICIT_LATEST_PRIMARY270_SAME_BYTE_OWNER_CANDIDATES_NO_RUNTIME_TRANSFER'
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    old,prior,p,q=[read(pair) for pair in [PREV,PREV_POST,PREFLIGHT,QUAL]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,prior,p,q]) and prior['registryManifestSha256']==PREV[1] and p['previousTechnicalRegistrySha256']==PREV[1] and q['preflightManifestSha256']==PREFLIGHT[1],'exact current chain')
    require(q['qualifiedCandidatePaths']==270 and q['positiveAndPriorityVectors']==276 and q['negativeAndImmutabilityVectors']==13,'qualified pure metadata resolver')
    rows=data.read_checked(data.BASE/PREFLIGHT[0]/'selected-owner-bridges.json',p['selectedBridgesSha256'])
    blob=(data.BASE/'PG13846-snapshot-program-trace-v1/manifest.json').read_bytes()
    rules=resolver.from_original_bytes(blob,tuple(r['path'] for r in rows))
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    m=copy.deepcopy(old);changes=[]
    for row in rows:
        path=row['path'];require(m['owners'][path]==row['previousUnknownOwner'] and data.sha((data.ROOT/path).read_bytes())==row['sha256'],'all exact current source and UNKNOWN rows')
        resolved=resolver.canonical(path,logical,row['sha256'],rules);require(resolved==row['resolvedCandidate'],'qualified same-byte candidate')
        after=dict(sha256=row['sha256'],**resolved);changes.append(dict(path=path,previous=copy.deepcopy(m['owners'][path]),current=copy.deepcopy(after),originalExplicitBasis=row['originalExplicitRecord']['basis'],originalExplicitRegistrySha256=resolver.REGISTRY_SHA,oldRuntimeTransferred=False));m['owners'][path]=after
    require(len(changes)==270,'only24')
    m['additionalScopeReferences'].append(dict(name=PREFLIGHT[0],sha256=PREFLIGHT[1],qualifiedResolverReference=list(QUAL),scope=SCOPE,ownerCorrections=changes,newTests=0,newExecs=0,newSourceNames=[],existingSourceNames=[],additionalSharedCostPp=0,actualAllocatedPp=None,sourceProgramsAcceptedByThisScope=0,coverageExecUnion=False,oldRuntimeTransferred=False))
    m.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),registryInputNegativeVectors=0,registryInputNegativeLabels=[],uniqueProductMethodDelta=0,newTestIds=0,sourceProgramDelta=0,ownerStatusCounts=dict(collections.Counter(v['ownershipStatus'] for v in m['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in m['owners'].values()),lastUpdateKind=SCOPE)
    require(m['ownerStatusCounts']=={'BASELINE_LOGICAL_REFERENCE':585,'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED':532,'UNKNOWN':6} and m['unknownOwnerPaths']==6,'24 only candidate updates')
    allowed={'owners','ownerStatusCounts','unknownOwnerPaths','additionalScopeReferences','invocation','previousUniqueRegistryReference','previousRegistryPostReference','registryInputNegativeVectors','registryInputNegativeLabels','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','lastUpdateKind'}
    require(set(m)==set(old) and all(wire(m[k])==wire(v) for k,v in old.items() if k not in allowed),'all old PT/counters/source/cost/formal/acceptance facts unchanged')
    changed={r['path'] for r in changes};require(all(m['owners'][k]==v for k,v in old['owners'].items() if k not in changed),'all other owners and first two correction history unchanged')
    for v in [old,prior,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',m);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
