"""Unqualified current-source static inventory. Never replaces the qualified candidate."""
import collections
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import wbs_candidate_trace as trace
import pg15848_g13_physical_scope_diagnosis as diagnosis

BEFORE = 'c67107a129aded9e945ca6130a3acc35c1dfd20c'
SOURCE = diagnosis.SOURCE
OUT = data.BASE / 'PG15918-g13-current-static-descriptor-v1'
DIAGNOSTIC = 'c3dc199b0393b4aeccd21ec4dc5bacca23e596b8b55f4dd2977af32d985f1468'
POST = '51e3358248219830256033c712189b9a479e63c31353f77322eb825fda79816b'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    raw = subprocess.check_output(['git', 'show', BEFORE + ':' + diagnosis.INV], cwd=data.ROOT)
    require(raw == (data.ROOT / diagnosis.INV).read_bytes(), 'fixed inventory byte')
    inv = json.loads(raw)
    candidate = inv['currentPhysicalCandidate']
    prior = {row['path']: row for row in candidate['artifacts']}
    d = data.read_checked(diagnosis.OUT / 'manifest.json', DIAGNOSTIC)
    post = data.read_checked(data.BASE / 'PG15850-g13-physical-scope-post-v1/manifest.json', POST)
    added = data.read_checked(diagnosis.OUT / 'added-public-artifacts.json', d['addedArtifactsSha256'])
    changed = data.read_checked(diagnosis.OUT / 'changed-common-artifacts.json', d['changedCommonArtifactsSha256'])
    additions = {row['path']: row for row in added}
    require(d['actualExit'] == post['actualExit'] == 0 and post['parentManifestSha256'] == DIAGNOSTIC, 'fixed independent diagnostic')
    paths = diagnosis.eligible(trace.git_files(SOURCE))
    tracked = diagnosis.eligible(subprocess.check_output(['git', 'ls-files', '-z', 'src', 'program/characterization'], cwd=data.ROOT).decode().split('\0')[:-1])
    require(paths == tracked == set(prior) | set(additions) and not set(prior) & set(additions), 'all1065 exact source/tracked/lineage sets')
    blobs = trace.git_artifacts(SOURCE, sorted(paths))
    old_blobs = trace.git_artifacts(candidate['source'], sorted(prior))
    rows = []
    for path in sorted(paths):
        actual = data.ROOT / path
        digest = data.sha(blobs[path])
        require(actual.resolve() == actual and not actual.is_symlink() and data.sha(actual.read_bytes()) == digest, 'fixed public byte: ' + path)
        kind = 'JAVA' if '/src/main/java/' in path else 'DEPLOYMENT' if path.startswith('src/deployment/') else 'RESOURCE'
        common = path in prior
        old = prior[path] if common else None
        if common:
            require(data.sha(old_blobs[path]) == old['sha256'], 'frozen old source byte')
            owner, cost = old['owner'], old['costOwner']
            lineage = dict(domain='FROZEN_CANDIDATE_RESPONSIBILITY_ONLY', source=candidate['source'], path=path,
                           historicalPath=old['historicalPath'], oldSha256=old['sha256'], oldKind=old['kind'],
                           byteChanged=digest != old['sha256'])
        else:
            addition = additions[path]
            require(addition['sha256'] == digest, 'fixed added byte')
            owner, cost = addition['canonicalOwner'], addition['canonicalCostOwner']
            lineage = dict(domain='FIXED_15848_ADDED_OWNER_CANDIDATE', diagnosticManifestSha256=DIAGNOSTIC,
                           ownershipStatus=addition['ownershipStatus'], basis=addition['basis'])
        require(isinstance(owner, str) and owner == cost, 'explicit same responsibility/cost owner')
        rows.append(dict(path=path, sha256=digest, kind=kind, owner=owner, costOwner=cost, lineage=lineage,
                         qualification='UNQUALIFIED_STATIC_ONLY', acceptance='UNASSESSED',
                         methodTestRequirementTrace='NOT_VERIFIED', runtimeQualificationTransferred=False,
                         additionalBudgetPp=0))
    owner_refs = []
    for owner in sorted({row['owner'] for row in rows}):
        refs = [dict(id=r['id'], source=r['source'], line=r['line'], designTrace=r['designTrace'])
                for r in inv['requirements'] if r['owner'] == owner]
        owner_refs.append(dict(owner=owner, meaning='OWNER_LEVEL_CANDIDATE_REFERENCE_NOT_ARTIFACT_OR_METHOD_TRACE',
                               requirementCandidates=refs, exactArtifactMethodTestJoinVerified=False))
    changed_paths = {r['path'] for r in changed}
    require(len(rows) == 1065 and len(prior) == 943 and len(additions) == 122 and
            {r['path'] for r in rows if r['lineage'].get('byteChanged')} == changed_paths, '943/122/24 exact lineage')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'artifacts.json', rows)
    data.write(OUT / 'owner-reference-candidates.json', owner_refs)
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=SOURCE, beforeGit=BEFORE,
        status='UNQUALIFIED_STATIC_INVENTORY_NOT_WHOLE_ACCEPTANCE', inventorySha256=data.sha(raw),
        artifactCount=len(rows), kindCounts=dict(collections.Counter(r['kind'] for r in rows)),
        ownerCounts=dict(collections.Counter(r['owner'] for r in rows)),
        javaPackageInfo=sum(r['path'].endswith('/package-info.java') for r in rows),
        priorArtifactCount=943, addedArtifactCount=122, removedArtifactCount=0, changedCommonArtifactCount=24,
        frozenCandidateSource=candidate['source'], diagnosticSha256=DIAGNOSTIC, diagnosticPostSha256=POST,
        artifactsSha256=data.sha((OUT / 'artifacts.json').read_bytes()),
        ownerReferenceCandidatesSha256=data.sha((OUT / 'owner-reference-candidates.json').read_bytes()),
        currentPathsEqualSourceAndTracked=True, allCurrentBytesMatchSource=True,
        qualifiedCandidateModified=False, wholeWbsGuardRelaxed=False, wholeAuditExecuted=False,
        exactMethodTestRequirementTraceVerified=False, wholeG13Accepted=False, currentWholeSourceQualified=False,
        oldRuntimeTransferred=False, newAccepted=0, formalUpdated=False, effortPercent=None,
        productTestsExecuted=0, productClassesLoaded=0, externalActions=0, privateRawRead=False))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, artifacts=len(rows), kinds=dict(collections.Counter(r['kind'] for r in rows)), newAccepted=0)))

if __name__ == '__main__':
    main()
