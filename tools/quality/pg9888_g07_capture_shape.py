"""Fixed public residual metadata/shape counts only; no captured values or their hashes emitted."""
from collections import Counter
import json
from pathlib import Path
import re
import g07_old_host_inputs as inputs
from public_java_digest_provenance import captures
from host_tool_invocation import capture, verify

C = inputs.common
ROOT = C.ROOT
SOURCE = '21d7c30425e7aa9ce435e808035a94fa4d75c93b'
OUT = C.BASE/'PG9888-g07-capture-shape-v1'
SOURCE_KEYS = frozenset(('source','productionSource','sourceSnapshot','artifactSource','operatorHead','commit','gitHead'))
FIELD = re.compile(r'"(source|productionSource|sourceSnapshot|artifactSource|operatorHead|commit|gitHead|sha256|archiveSha256|manifestSha256|sourceSha256|execSha256|logSha256|payloadSha256)"\s*:\s*"([a-f0-9]{40}|[a-f0-9]{64})"')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    value = inputs.inputs()
    previous_sha = '7cb508e23ab7f35e07ed82271885bae50d2ab2c8a07b97a7295f189fbc899c79'
    previous = C.read_checked(C.BASE/'PG9572-g07-old-host-main-class-provenance-v1/manifest.json',previous_sha)
    updates = C.read_checked(C.BASE/'PG9572-g07-old-host-main-class-provenance-v1/updates.json',previous['updatesSha256'])
    done = Counter(map(C.key,updates))
    pending = []
    for row in value['pending']:
        if done[C.key(row)]:
            done[C.key(row)] -= 1
        else:
            pending.append(row)
    assert len(pending) == 4493 and not sum(done.values())
    patterns = {name:re.compile(rule['regex'],re.ASCII) for name,rule in value['rules'].items()}
    cache = {}
    rows = []
    shapes,lengths,rules,contexts = Counter(),Counter(),Counter(),Counter()
    all_source40 = []
    for row in pending:
        path = row['path']
        if path not in cache:
            text = C.finding_text(row,value['inventory'])
            fields = {}
            for match in FIELD.finditer(text):
                fields.setdefault(match.group(2),set()).add(match.group(1))
            lines = None if any(ch in text for ch in '\v\f\r\x1c\x1d\x1e\x85\u2028\u2029') else text.splitlines(keepends=True)
            cache[path] = (lines,fields)
        lines,fields = cache[path]
        exact = set() if lines is None else captures(lines,row,patterns[row['ruleId']])
        kinds = Counter(('HEX40' if re.fullmatch('[a-fA-F0-9]{40}',v) else
            'HEX64' if re.fullmatch('[a-fA-F0-9]{64}',v) else 'OTHER') for v in exact)
        shape = 'UNSUPPORTED_LINE_SEPARATOR' if lines is None else 'NO_EXACT_CAPTURE' if not exact else \
            'ALL_HEX40' if set(kinds)=={'HEX40'} else 'ALL_HEX64' if set(kinds)=={'HEX64'} else 'MIXED_OR_OTHER'
        full_source40_context = bool(exact) and set(kinds)=={'HEX40'} and all(fields.get(v,set()) & SOURCE_KEYS for v in exact)
        key = {k:row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')}
        rows.append(dict(**key,shape=shape,uniqueExactCaptureCount=len(exact),captureLengths=sorted(map(len,exact)),
            allCapturesHaveSource40FieldContextCandidate=full_source40_context,disposition='UNCLASSIFIED'))
        if full_source40_context:
            all_source40.append(key)
        shapes[shape] += 1
        rules[row['ruleId']] += 1
        lengths.update(map(str,map(len,exact)))
        for v in exact:
            for label in fields.get(v,set()):
                contexts[label] += 1
    assert len(rows) == sum(shapes.values()) == sum(rules.values()) == 4493
    assert Counter(C.key(r) for r in rows) == Counter(C.key(r) for r in pending)
    verify(invocation)
    OUT.mkdir()
    C.write(OUT/'residual-metadata-shapes.json',rows)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,historicalScanSource=C.HISTORICAL,contentCommit=C.CONTENT,
        previousClassificationManifestSha256=previous_sha,remainingFindings=4493,distinctPublicInputPaths=len(cache),
        byRule=dict(rules),byFindingShape=dict(shapes),uniqueCaptureOccurrencesPerFindingByLength=dict(lengths),
        literalMetadataFieldContextOccurrencesNotProven=dict(contexts),allSource40ContextCandidateFindings=len(all_source40),
        allSource40ContextCandidateKeys=all_source40,residualMetadataSha256=C.sha((OUT/'residual-metadata-shapes.json').read_bytes()),
        capturedValuesWritten=False,captureValueHashesWritten=False,sourceContextIsNotArtifactProof=True,
        additionalFalsePositives=0,remainingUnclassified=4493,actualSecretCount=None,scannerExecuted=False,historyExpanded=False,
        privateRawRead=False,productTestsExecuted=0,newAccepted=0,formalUpdated=False,currentSourceWholeG07Qualified=False,effortPercent=None)
    C.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,findings=4493,shape=dict(shapes),lengths=dict(lengths),
        source40Candidates=len(all_source40),manifestSha256=C.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
