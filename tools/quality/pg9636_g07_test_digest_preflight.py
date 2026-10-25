"""Count metadata-only candidate joins in existing public residual; no classification or tests."""
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import re
import g07_old_host_inputs as inputs
from public_java_digest_provenance import captures
from host_tool_invocation import capture, verify

C = inputs.common
BASE = C.BASE
OUT = BASE / 'PG9636-g07-test-class-digest-preflight-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    value = inputs.inputs()
    previous = C.read_checked(BASE / 'PG9572-g07-old-host-main-class-provenance-v1/manifest.json',
        '7cb508e23ab7f35e07ed82271885bae50d2ab2c8a07b97a7295f189fbc899c79')
    updates = C.read_checked(BASE / 'PG9572-g07-old-host-main-class-provenance-v1/updates.json', previous['updatesSha256'])
    old = C.read_checked(BASE / 'PG9572-g07-old-host-main-class-provenance-v1/public-old-main-class-proofs.json', previous['registrySha256'])
    known = set(value['oldProofs']) | {row['sha256'] for row in old}
    done = Counter(map(C.key, updates))
    pending = []
    for row in value['pending']:
        key = C.key(row)
        if done[key]:
            done[key] -= 1
        else:
            pending.append(row)
    assert len(pending) == 4493 and not sum(done.values())
    graph = value['manifests']['graph']
    metadata = C.read_checked(BASE / C.PINS['graph'][0] / 'test-class-metadata.json', graph['testMetadataSha256'])
    assert len(metadata) == 1910
    candidates = {row['sha256'] for row in metadata} - known
    patterns = {name: re.compile(rule['regex'], re.ASCII) for name, rule in value['rules'].items()}
    cache = {}
    potential = []
    intersects = 0
    reasons = Counter()
    for row in pending:
        path = row['path']
        if path not in cache:
            text = C.finding_text(row, value['inventory'])
            cache[path] = None if any(ch in text for ch in '\v\f\r\x1c\x1d\x1e\x85\u2028\u2029') else text.splitlines(keepends=True)
        if cache[path] is None:
            reasons['UNSUPPORTED_LINE_SEPARATOR'] += 1
            continue
        exact = captures(cache[path], row, patterns[row['ruleId']])
        if exact & candidates:
            intersects += 1
        if exact and exact <= known | candidates and exact & candidates:
            potential.append({key: row[key] for key in ('path', 'ruleId', 'startLine', 'endLine', 'inputSha256')})
        else:
            reasons['NO_EXACT_CAPTURE' if not exact else 'NOT_FULLY_BOUND_TO_EXISTING_OR_CANDIDATE_METADATA'] += 1
    assert len(potential) + sum(reasons.values()) == 4493
    verify(invocation)
    OUT.mkdir()
    C.write(OUT / 'manifest.json', dict(actualExit=0, source=C.SOURCE, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
        invocation=invocation, historicalScanSource=C.HISTORICAL, contentCommit=C.CONTENT,
        existingTestClassMetadata=1910, metadataSha256=graph['testMetadataSha256'], priorUnclassified=4493,
        findingsIntersectingCandidateMetadata=intersects, candidateFullyBoundFindings=len(potential), candidateFindings=potential,
        noncandidateReasons=dict(reasons), physicalTestClassProvenanceQualified=False,
        additionalFalsePositives=0, remainingUnclassified=4493, actualSecretCount=None,
        productTestsExecuted=0, newAccepted=0, coverage=None, formalUpdated=False, effortPercent=None,
        scannerExecuted=False, privateRawRead=False, vmActions=0, currentSourceWholeG07Qualified=False))
    print(json.dumps(dict(actualExit=0, metadataClasses=1910, intersects=intersects, candidateFullyBound=len(potential), classified=0)))
    print('manifestSha256=' + C.sha((OUT / 'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
