"""G13 source-only exact physical scope reconciliation; old whole qualification is not rebound."""
import collections
import hashlib
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_current12_v3 import canonical
import wbs_candidate_trace as trace

OUT=data.BASE/'PG15848-g13-physical-scope-diagnosis-v1'
BEFORE='f55a72c458626bbdaeebe9bfcc4c39a3103dc15a'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
INV='documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
def require(ok,message):
    if not ok:raise ValueError(message)
def eligible(paths):
    return {p for p in paths if ('/src/main/java/' in p and p.endswith('.java')) or '/src/main/resources/' in p or p.startswith('src/deployment/')}
def git(*args):
    return subprocess.check_output(['git',*args],cwd=data.ROOT)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    raw=git('show',BEFORE+':'+INV);require(raw==(data.ROOT/INV).read_bytes(),'fixed live inventory byte')
    inv=json.loads(raw);candidate=inv['currentPhysicalCandidate'];old={v['path']:v for v in candidate['artifacts']}
    require(len(inv['artifacts'])==941 and len(old)==len(candidate['artifacts'])==943 and candidate['source']=='e7d64fda2453e906ee6ccc5fe718e5c29841e4aa','frozen 941/943 source')
    current=eligible(trace.git_files(SOURCE));prior=eligible(trace.git_files(candidate['source']))
    tracked=eligible(git('ls-files','-z','src','program/characterization').decode().split('\0')[:-1])
    require(prior==set(old) and current==tracked and len(current)==1065 and current-prior and not prior-current,'exact old candidate/new Production/tracked scopes')
    blobs=trace.git_artifacts(SOURCE,sorted(current));prior_blobs=trace.git_artifacts(candidate['source'],sorted(prior))
    require(all(sha(prior_blobs[p])==old[p]['sha256'] for p in prior),'frozen original candidate hashes')
    for path in sorted(current):
        actual=data.ROOT/path
        require(actual.resolve()==actual and not actual.is_symlink() and sha(actual.read_bytes())==sha(blobs[path]),'current full physical byte equals fixed Production: '+path)
    logical={r['path']:r for r in inv['artifacts']}
    rows=[]
    for path in sorted(current-prior):
        rows.append(dict(path=path,sha256=sha(blobs[path]),kind='JAVA' if '/src/main/java/' in path else 'DEPLOYMENT' if path.startswith('src/deployment/') else 'RESOURCE',**canonical(path,logical),additionalBudgetPp=0,accepted=False,currentRuntimeQualification=False))
    counts=dict(collections.Counter(r['kind'] for r in rows));owners=dict(collections.Counter(str(r['canonicalOwner']) for r in rows))
    changed=[dict(path=p,oldSha256=old[p]['sha256'],currentSha256=sha(blobs[p]),historicalSource=candidate['source'],productionSource=SOURCE,oldQualificationTransferred=False) for p in sorted(prior&current) if sha(blobs[p])!=old[p]['sha256']]
    verify(invocation);OUT.mkdir()
    data.write(OUT/'added-public-artifacts.json',rows);data.write(OUT/'changed-common-artifacts.json',changed)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,beforeGit=BEFORE,inventorySha256=sha(raw),historicalLogicalArtifacts=941,frozenCandidateSource=candidate['source'],frozenCandidateArtifacts=943,currentProductionArtifacts=len(current),currentTrackedArtifacts=len(tracked),candidateEqualsItsOwnGit=True,currentTrackedEqualsProductionGit=True,allCurrentPhysicalBytesMatchProduction=True,addedArtifacts=len(rows),removedArtifacts=0,addedKinds=counts,addedCanonicalCandidateOwners=owners,unknownAddedCanonicalOwners=sum(r['canonicalOwner'] is None for r in rows),changedCommonArtifacts=len(changed),addedArtifactsSha256=sha((OUT/'added-public-artifacts.json').read_bytes()),changedCommonArtifactsSha256=sha((OUT/'changed-common-artifacts.json').read_bytes()),oldInventoryAndCandidateModified=False,canonicalRuleAppliedWithoutProductExecution=True,currentWholeSourceQualified=False,wholeWbsScopeGuardRelaxed=False,wholeWbsAuditRerun=False,wholeG13Accepted=False,sourceScopeDifferenceExplainsExistingAuditHold=True,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None,oldNativeTransferred=False,externalActions=0,privateRawRead=False))
    print(sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,added=len(rows),removed=0,changedCommon=len(changed),addedKinds=counts,owners=owners,wholeG13Accepted=False)))
if __name__=='__main__':main()
