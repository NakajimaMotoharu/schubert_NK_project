"""Independent exact-set/lineage check. Static inventory is never runtime acceptance."""
import collections
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import wbs_candidate_trace as trace
import pg15918_g13_current_static_descriptor as original

PIN = 'b238136eb4d965b59ea281c3e610d889b18a0c102839ea9e658b2235fea6a05c'
OUT = data.BASE / 'PG15920-g13-current-static-descriptor-post-v1'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def assess(p, rows, refs, inv, blobs):
    prior = {r['path']: r for r in inv['currentPhysicalCandidate']['artifacts']}
    require(p['actualExit'] == 0 and p['source'] == original.SOURCE and p['beforeGit'] == original.BEFORE, 'fixed identity')
    require(p['status'] == 'UNQUALIFIED_STATIC_INVENTORY_NOT_WHOLE_ACCEPTANCE', 'unqualified domain')
    require((p['artifactCount'], p['priorArtifactCount'], p['addedArtifactCount'], p['removedArtifactCount'], p['changedCommonArtifactCount'], p['javaPackageInfo']) == (1065, 943, 122, 0, 24, 37), 'exact counts')
    require(p['kindCounts'] == {'JAVA': 969, 'DEPLOYMENT': 35, 'RESOURCE': 61}, 'path-based kinds')
    require(p['frozenCandidateSource'] == 'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa' and p['diagnosticSha256'] == original.DIAGNOSTIC and p['diagnosticPostSha256'] == original.POST, 'frozen source/diagnostic')
    for key in ('qualifiedCandidateModified', 'wholeWbsGuardRelaxed', 'wholeAuditExecuted', 'exactMethodTestRequirementTraceVerified', 'wholeG13Accepted', 'currentWholeSourceQualified', 'oldRuntimeTransferred', 'formalUpdated', 'privateRawRead'):
        require(p[key] is False, 'no promotion: ' + key)
    for key in ('newAccepted', 'productTestsExecuted', 'productClassesLoaded', 'externalActions'):
        require(type(p[key]) is int and p[key] == 0, 'no new execution/acceptance: ' + key)
    require(p['effortPercent'] is None and p['currentPathsEqualSourceAndTracked'] is p['allCurrentBytesMatchSource'] is True, 'unknown effort/complete static bytes')
    require(len(rows) == len({r['path'] for r in rows}) == 1065 and {r['path'] for r in rows} == set(blobs), 'exact unique set')
    changed = 0
    for row in rows:
        path = row['path']
        require(row['sha256'] == data.sha(blobs[path]), 'source byte')
        expected_kind = 'JAVA' if '/src/main/java/' in path else 'DEPLOYMENT' if path.startswith('src/deployment/') else 'RESOURCE'
        require(row['kind'] == expected_kind, 'path kind')
        require(row['qualification'] == 'UNQUALIFIED_STATIC_ONLY' and row['acceptance'] == 'UNASSESSED' and row['methodTestRequirementTrace'] == 'NOT_VERIFIED' and row['runtimeQualificationTransferred'] is False and type(row['additionalBudgetPp']) is int and row['additionalBudgetPp'] == 0, 'per-row no qualification/fee')
        lineage = row['lineage']
        if path in prior:
            old = prior[path]
            require(row['owner'] == old['owner'] and row['costOwner'] == old['costOwner'], 'original owner/cost')
            different = row['sha256'] != old['sha256']
            require(lineage == dict(domain='FROZEN_CANDIDATE_RESPONSIBILITY_ONLY', source=p['frozenCandidateSource'], path=path, historicalPath=old['historicalPath'], oldSha256=old['sha256'], oldKind=old['kind'], byteChanged=different), 'exact old lineage')
            changed += different
        else:
            stop = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java'
            if path == stop:
                owner = 'WBS-P018-05'
            elif path.startswith('src/deployment/monitoring/'):
                owner = 'WBS-C07'
            else:
                require('/monitoring/' in path and expected_kind == 'JAVA', 'explicit added monitoring family')
                owner = 'WBS-P018-09'
            require(row['owner'] == row['costOwner'] == owner and lineage['domain'] == 'FIXED_15848_ADDED_OWNER_CANDIDATE' and lineage['diagnosticManifestSha256'] == original.DIAGNOSTIC and lineage['ownershipStatus'] == 'NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' and isinstance(lineage['basis'], str) and lineage['basis'], 'explicit additional lineage')
    require(changed == 24 and dict(collections.Counter(r['owner'] for r in rows)) == p['ownerCounts'], 'changed/owner totals')
    owners = {r['owner'] for r in rows}
    require(len(refs) == len(owners) and {r['owner'] for r in refs} == owners, 'unique owner index')
    for row in refs:
        expected = [dict(id=r['id'], source=r['source'], line=r['line'], designTrace=r['designTrace']) for r in inv['requirements'] if r['owner'] == row['owner']]
        require(row['meaning'] == 'OWNER_LEVEL_CANDIDATE_REFERENCE_NOT_ARTIFACT_OR_METHOD_TRACE' and row['exactArtifactMethodTestJoinVerified'] is False and row['requirementCandidates'] == expected, 'not fabricated artifact/method/test trace')

def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(original.OUT / 'manifest.json', PIN)
    rows = data.read_checked(original.OUT / 'artifacts.json', p['artifactsSha256'])
    refs = data.read_checked(original.OUT / 'owner-reference-candidates.json', p['ownerReferenceCandidatesSha256'])
    raw = subprocess.check_output(['git', 'show', original.BEFORE + ':' + original.diagnosis.INV], cwd=data.ROOT)
    require(data.sha(raw) == p['inventorySha256'] and raw == (data.ROOT / original.diagnosis.INV).read_bytes(), 'all original 485 unchanged')
    inv = json.loads(raw)
    paths = {x for x in trace.git_files(original.SOURCE) if ('/src/main/java/' in x and x.endswith('.java')) or '/src/main/resources/' in x or x.startswith('src/deployment/')}
    blobs = trace.git_artifacts(original.SOURCE, sorted(paths))
    require(all(not (data.ROOT / x).is_symlink() and (data.ROOT / x).read_bytes() == blobs[x] for x in paths), 'all current bytes independently read')
    assess(p, rows, refs, inv, blobs)
    negatives = []
    mutations = [(k, v) for k, v in [('source', '0'*40), ('status', 'QUALIFIED'), ('artifactCount', 943), ('addedArtifactCount', 0), ('javaPackageInfo', 0), ('effortPercent', 0), ('newAccepted', True)]]
    mutations += [(k, True) for k in ('qualifiedCandidateModified', 'wholeWbsGuardRelaxed', 'wholeAuditExecuted', 'exactMethodTestRequirementTraceVerified', 'wholeG13Accepted', 'currentWholeSourceQualified', 'oldRuntimeTransferred', 'formalUpdated', 'privateRawRead')]
    for key, value in mutations:
        bad = copy.deepcopy(p)
        bad[key] = value
        try:
            assess(bad, rows, refs, inv, blobs)
        except ValueError:
            negatives.append(key)
        else:
            raise ValueError('unrejected manifest: ' + key)
    variants = [('missing', lambda r, f: r.pop()), ('duplicate', lambda r, f: r.__setitem__(0, r[1])), ('byte', lambda r, f: r[0].update(sha256='0'*64)), ('owner', lambda r, f: r[0].update(owner='WBS-G13.07')), ('cost', lambda r, f: r[0].update(costOwner='WBS-G13.07')), ('row-qualified', lambda r, f: r[0].update(qualification='QUALIFIED')), ('row-accept', lambda r, f: r[0].update(acceptance='PASS')), ('row-fee', lambda r, f: r[0].update(additionalBudgetPp=1)), ('row-trace', lambda r, f: r[0].update(methodTestRequirementTrace='VERIFIED')), ('row-transfer', lambda r, f: r[0].update(runtimeQualificationTransferred=True)), ('old-lineage', lambda r, f: next(x for x in r if 'oldSha256' in x['lineage'])['lineage'].update(oldSha256='0'*64)), ('added-owner', lambda r, f: next(x for x in r if 'ownershipStatus' in x['lineage']).update(owner='WBS-G13.07')), ('missing-owner-ref', lambda r, f: f.pop()), ('exact-trace', lambda r, f: f[0].update(exactArtifactMethodTestJoinVerified=True)), ('requirement-crossproduct', lambda r, f: f[0].update(requirementCandidates=[{}]))]
    for label, mutate in variants:
        rr, ff = copy.deepcopy(rows), copy.deepcopy(refs)
        mutate(rr, ff)
        try:
            assess(p, rr, ff, inv, blobs)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected row: ' + label)
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=original.SOURCE, invocation=invocation,
        parentManifestSha256=PIN, artifactsSha256=p['artifactsSha256'], ownerReferenceCandidatesSha256=p['ownerReferenceCandidatesSha256'],
        independentNegativeVectors=len(negatives), negativeLabels=negatives, artifactCount=1065,
        exactMethodTestRequirementTraceVerified=False, currentWholeSourceQualified=False, wholeG13Accepted=False,
        oldRuntimeTransferred=False, newAccepted=0, formalUpdated=False, effortPercent=None,
        productTestsExecuted=0, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentNegativeVectors=len(negatives), newAccepted=0)))

if __name__ == '__main__':
    main()
