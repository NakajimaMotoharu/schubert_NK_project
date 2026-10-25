"""Four public analysis-library candidates only; never a new scanner or a secret-value report."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_old_host_inputs as inputs
from public_java_digest_provenance import captures
from host_tool_invocation import capture, verify

C = inputs.common
ROOT = C.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OUT = C.BASE/'PG9860-g07-library-digest-preflight-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    value = inputs.inputs()  # Frozen historical public source/proofs, not current-source qualification.
    previous = C.read_checked(C.BASE/'PG9572-g07-old-host-main-class-provenance-v1/manifest.json',
        '7cb508e23ab7f35e07ed82271885bae50d2ab2c8a07b97a7295f189fbc899c79')
    updates = C.read_checked(C.BASE/'PG9572-g07-old-host-main-class-provenance-v1/updates.json',previous['updatesSha256'])
    prior_proofs = C.read_checked(C.BASE/'PG9572-g07-old-host-main-class-provenance-v1/public-old-main-class-proofs.json',previous['registrySha256'])
    known = set(value['oldProofs']) | {r['sha256'] for r in prior_proofs}
    done = Counter(map(C.key,updates))
    pending = []
    for row in value['pending']:
        if done[C.key(row)]:
            done[C.key(row)] -= 1
        else:
            pending.append(row)
    assert len(pending) == 4493 and not sum(done.values())
    library_sha = '4159dc3dda26a447e147b3c689de36e2052662fada0d9a87374a5fec4b208bed'
    manifest = C.read_checked(ROOT/'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9842-protocol-switchmap-review-v2/manifest.json',library_sha)
    assert manifest['actualExit'] == 0 and manifest['source'] == SOURCE
    libraries = manifest['libraryHashes']
    assert len(libraries) == 4
    prefix = ROOT.parent/'toolchain/m2/repository'
    for name,digest in libraries.items():
        path = Path(name)
        assert path.resolve() == path and not path.is_symlink() and path.is_file()
        assert path.is_relative_to(prefix) and path.suffix == '.jar' and C.sha(path.read_bytes()) == digest
    candidate_values = set(libraries.values()) - known
    patterns = {name:re.compile(rule['regex'],re.ASCII) for name,rule in value['rules'].items()}
    cache = {}
    candidates = []
    reasons = Counter()
    intersections = 0
    for row in pending:
        path = row['path']
        if path not in cache:
            text = C.finding_text(row,value['inventory'])
            cache[path] = None if any(ch in text for ch in '\v\f\r\x1c\x1d\x1e\x85\u2028\u2029') else text.splitlines(keepends=True)
        if cache[path] is None:
            reasons['UNSUPPORTED_LINE_SEPARATOR'] += 1
            continue
        exact = captures(cache[path],row,patterns[row['ruleId']])
        if exact & candidate_values:
            intersections += 1
        if exact and exact <= known | candidate_values and exact & candidate_values:
            candidates.append({k:row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')})
        else:
            reasons['NO_EXACT_CAPTURE' if not exact else 'ALL_CAPTURES_NOT_PROVED_OR_NO_NEW_LIBRARY'] += 1
    assert len(candidates) + sum(reasons.values()) == 4493
    verify(invocation)
    OUT.mkdir()
    C.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        historicalScanSource=C.HISTORICAL,contentCommit=C.CONTENT,priorClassificationContextSource=C.SOURCE,
        priorUnclassified=4493,publicLibraryManifestSha256=library_sha,libraryCandidates=4,
        freshCandidateDigests=len(candidate_values),findingsIntersectingCandidates=intersections,
        candidateFullyBoundFindings=len(candidates),candidateFindings=candidates,noncandidateReasons=dict(reasons),
        libraryArtifactProvenanceQualified=False,additionalFalsePositives=0,remainingUnclassified=4493,
        actualSecretCount=None,scannerExecuted=False,historyExpanded=False,privateRawRead=False,
        productTestsExecuted=0,newAccepted=0,formalUpdated=False,currentSourceWholeG07Qualified=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,candidates=4,intersections=intersections,fullyBound=len(candidates),classified=0,
        manifestSha256=C.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
