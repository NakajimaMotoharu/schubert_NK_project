"""Overinclusive public enum lexical candidates only, never secret classification or class execution."""
from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import re
import subprocess

import g07_old_host_inputs as inputs
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX, captures

C = inputs.common
ROOT = C.ROOT
SOURCE = '21d7c30425e7aa9ce435e808035a94fa4d75c93b'
OUT = C.BASE/'PG9896-g07-enum-preselection-v1'


def select_occurrences(pending, selected):
    by_key = defaultdict(deque)
    for row in pending:
        by_key[C.key(row)].append(row)
    result = []
    for row in selected:
        remaining = by_key[C.key(row)]
        if not remaining:
            raise ValueError('selected occurrence not available in original multiset')
        result.append(remaining.popleft())
    if Counter(C.key(r) for r in result) != Counter(C.key(r) for r in selected):
        raise ValueError('selected occurrence multiset differs')
    return result


def selection_vectors():
    row = dict(path='public',ruleId='generic',startLine=1,endLine=1,inputSha256='metadata')
    first, second = dict(row,ordinal=1), dict(row,ordinal=2)
    assert select_occurrences([first,second],[row,row]) == [first,second]
    assert select_occurrences([first,second],[row]) == [first]
    for pending, selected in (([],[row]),([first],[row,row])):
        try:
            select_occurrences(pending,selected)
        except ValueError:
            pass
        else:
            raise AssertionError('missing or excess occurrence must be refused')
    return 4


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    previous = C.read_checked(C.BASE/'PG9888-g07-capture-shape-v1/manifest.json',
        '6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb')
    shapes = C.read_checked(C.BASE/'PG9888-g07-capture-shape-v1/residual-metadata-shapes.json',
        previous['residualMetadataSha256'])
    selected = [row for row in shapes if row['shape'] == 'MIXED_OR_OTHER']
    assert len(shapes) == 4493 and len(selected) == 220
    value = inputs.inputs()
    vector_count = selection_vectors()
    selected = select_occurrences(value['pending'],selected)
    raw_paths = subprocess.check_output(['git','ls-tree','-r','--name-only',SOURCE,'--','src'],cwd=ROOT)
    paths = [p for p in raw_paths.decode().splitlines() if '/src/main/java/' in p and p.endswith('.java')]
    symbols = set()
    enum_sources = []
    for path in paths:
        raw = subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT)
        assert (ROOT/path).read_bytes() == raw
        tokens = [m.group() for m in LEX.finditer(raw.decode()) if not m.group().startswith(('//','/*','"',"'"))]
        if 'enum' not in tokens:
            continue
        names = {token for token in tokens if re.fullmatch('[A-Z][A-Z0-9_]*',token)}
        symbols.update(names)
        enum_sources.append(dict(path=path,sha256=C.sha(raw),candidateIdentifierCount=len(names)))
    patterns = {name:re.compile(rule['regex'],re.ASCII) for name,rule in value['rules'].items()}
    cache = {}
    results = []
    matches = Counter()
    for row in selected:
        if row['path'] not in cache:
            text = C.finding_text(row,value['inventory'])
            assert not any(ch in text for ch in '\v\f\r\x1c\x1d\x1e\x85\u2028\u2029')
            cache[row['path']] = text.splitlines(keepends=True)
        exact = captures(cache[row['path']],row,patterns[row['ruleId']])
        candidate = exact & symbols
        possible_closure = bool(candidate) and all(v in symbols or v in value['oldProofs'] for v in exact)
        key = {k:row[k] for k in ('path','ruleId','startLine','endLine','inputSha256')}
        results.append(dict(**key,enumCandidateCaptureCount=len(candidate),exactCaptureCount=len(exact),
            allCapturesCandidateOrPreviouslyProven=possible_closure,disposition='UNCLASSIFIED'))
        matches['findingsWithCandidate'] += bool(candidate)
        matches['possibleClosureFindings'] += possible_closure
    assert Counter(C.key(r) for r in results) == Counter(C.key(r) for r in selected)
    verify(invocation)
    OUT.mkdir()
    C.write(OUT/'candidate-metadata.json',results)
    result = dict(actualExit=0,source=SOURCE,historicalScanSource=C.HISTORICAL,classificationContextSource=C.SOURCE,
        invocation=invocation,previousManifestSha256=C.sha((C.BASE/'PG9888-g07-capture-shape-v1/manifest.json').read_bytes()),
        selectedFindings=220,enumSourceCount=len(enum_sources),enumSources=enum_sources,
        candidateIdentifierCount=len(symbols),candidateCounts=dict(matches),
        selectionMetadataVectors=vector_count,
        originalFailure=dict(actualExit=1,stage='original unique-key assertion before candidate selection',
            toolSha256='b4c776c5aed3fe0c6f56133203b317c3ef0a9b78d250c311e6ebda52691f193a',
            bugs=['BUG1776'],horizontal=['YKT1527']),
        candidateMetadataSha256=C.sha((OUT/'candidate-metadata.json').read_bytes()),
        candidateSetIsOverinclusiveNotProof=True,additionalFalsePositives=0,remainingUnclassified=4493,
        capturedValuesWritten=False,captureValueHashesWritten=False,actualSecretCount=None,
        productTestsExecuted=0,scannerExecuted=False,externalActions=0,heldValidationRetried=False,
        formalUpdated=False,newAccepted=0,effortPercent=None)
    C.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,selected=220,enumSources=len(enum_sources),candidates=dict(matches),
        classified=0,remaining=4493,manifestSha256=C.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
