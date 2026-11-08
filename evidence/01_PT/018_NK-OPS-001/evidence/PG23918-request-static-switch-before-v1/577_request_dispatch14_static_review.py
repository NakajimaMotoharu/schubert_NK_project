"""Read two explicitly pinned Main sources as text; no compiler, fixture or product execution."""
from pathlib import Path
from copy import deepcopy
import datetime
import hashlib
import json
import re
import subprocess

R = Path(__file__).resolve().parents[4]
B = R / 'evidence/01_PT/018_NK-OPS-001'
C = B / 'input/575_request_dispatch14_static_scope.json'
O = B / 'evidence/PG23912-request-dispatch14-static-design-v1'
load = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def branches(text, method):
    # These two pinned methods contain no braces inside literals/comments.
    start = text.index('public ', text.index('public final class'))
    mark = re.search(r'public [^\n]+ ' + method + r'\(', text[start:])
    assert mark
    start += mark.start()
    first = text.index('{', start)
    depth = 1
    pos = first + 1
    while depth:
        depth += (text[pos] == '{') - (text[pos] == '}')
        pos += 1
    body = text[first + 1:pos - 1]
    matches = list(re.finditer(r'case ([A-Z]+(?:, [A-Z]+)*) ->', body))
    result = {}
    for i, match in enumerate(matches):
        segment = body[match.end():matches[i + 1].start() if i + 1 < len(matches) else body.index('\n    };', match.end())]
        for kind in match[1].split(', '):
            assert kind not in result
            result[kind] = segment
    return body, result


def main():
    assert not O.exists()
    cfg = load(C)
    assert cfg['actualOperationsAuthorized'] is False and cfg['expectedDynamicTests'] == 0
    normal = R / cfg['normalIndex']['path']
    assert sha(normal) == cfg['normalIndex']['sha256']
    index = load(normal)
    for ref in cfg['authority']:
        path = R / ref['path']
        assert sha(path) == ref['sha256']
        assert path.read_bytes() == subprocess.check_output(['git', 'show', 'origin/main:' + ref['path']], cwd=R)
    bodies = {}
    for ref in cfg['sources']:
        path = R / ref['path']
        assert sha(path) == ref['sha256']
        # Index sha256 means compiled physical class bytes, not Java source bytes.
        # Bind source independently to the frozen Main commit; retain all physical members.
        assert hashlib.sha256(subprocess.check_output(
            ['git', 'show', cfg['source'] + ':' + ref['path']], cwd=R)).hexdigest() == ref['sha256']
        physical = [v for v in index.values() if v['path'] == ref['path']]
        assert physical and all(isinstance(v['crc64'], str) for v in physical)
        text = path.read_text()
        query, query_cases = branches(text, 'query')
        canonical, canonical_cases = branches(text, 'canonical')
        decoded = dict(re.findall(r'case "([A-Z0-9]{8})" -> Kind\.([A-Z]+);', text))
        for arg in ('repository', 'connection', 'actor'):
            assert f'Objects.requireNonNull({arg}, "{arg}");' in query.split('return switch')[0]
        assert not re.search(r'\b(commit|rollback|close|getConnection|createConnection|executeQuery|executeUpdate)\s*\(', query)
        assert 'catch (' not in query and 'catch(' not in query
        assert 'Long.toString(actor.userId())' in canonical and '"001"' in canonical
        assert '"REQUEST:" + values.layoutId().value()' in canonical
        assert 'return retainedHeader;' in text
        bodies[ref['domain']] = (ref, text, query_cases, canonical_cases, decoded)
    output = []
    for case in cfg['cases']:
        ref, text, queries, canonical, decoded = bodies[case['domain']]
        assert decoded[case['layout']] == case['kind']
        query = queries[case['kind']]
        assert re.findall(r'repository\.(\w+)\(', query) == [case['repositoryMethod']]
        compact = re.sub(r'\s+', '', query)
        args = 'connection,actor'
        if case['requestDto']:
            args += ',(' + case['requestDto'] + ')values.data()'
        assert 'repository.' + case['repositoryMethod'] + '(' + args + ')' in compact
        projection = case['projection']
        if projection in ('Inline', 'Detail'):
            assert compact.startswith('newScenarioQuerySnapshot.' + projection + '(')
        elif projection == 'PRESENT_OPTIONAL':
            assert compact.startswith('Optional.of(')
        else:
            assert projection == 'DIRECT_OPTIONAL' and compact.startswith('repository.')
        declaration = canonical[case['kind']]
        fields = re.findall(r'(text|number)\(\s*("[^"\n]+"|LITERAL_GAMECODE)\s*,', declaration)
        observed = [(name.strip('"') if name != 'LITERAL_GAMECODE' else 'gameCode') + ('/X1' if kind == 'text' else '/N1') for kind, name in fields]
        expected = [v.removesuffix('?') for v in case['canonicalOrderedFields']]
        assert observed == expected
        result = deepcopy(case)
        result.update(staticReviewStatus='STATIC_PT_DESIGN_REVIEW_COMPLETE',
                      sourceReference=ref, querySnippetSha256=hashlib.sha256(query.encode()).hexdigest(),
                      canonicalSnippetSha256=hashlib.sha256(declaration.encode()).hexdigest(),
                      responseLayout=case['layout'].replace('REQ', 'RSP'),
                      plannedNegativeCases=['null repository', 'null connection', 'null actor', 'repository SQL/Runtime/Error propagation', 'no borrowed connection lifecycle transfer'],
                      dynamicExceptionBehaviorProven=False, actualDbProven=False, ptPass=False,
                      residualRisk='Actual SQL/driver rows/transaction/null/failure graph/concurrency/resend and response publication remain NOT_EXECUTED_HOLD; static dispatch matching is not dynamic acceptance.')
        output.append(result)
    assert len(output) == len({v['id'] for v in output}) == 14
    for domain, (ref, text, query, canonical, decode) in bodies.items():
        expected = {v['kind'] for v in cfg['cases'] if v['domain'] == domain}
        assert set(query) == set(canonical) == set(decode.values()) == expected
    O.mkdir()
    (O / 'static-case-designs.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    manifest = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=cfg['source'],
                    observerHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip(),
                    config=dict(path=str(C.relative_to(R)), sha256=sha(C)),
                    cases=dict(path=str((O / 'static-case-designs.json').relative_to(R)), sha256=sha(O / 'static-case-designs.json')),
                    sourceFiles=2, staticDesignCases=14, scenarioCases=6, mediaCases=8,
                    dynamicStatus='NOT_EXECUTED_HOLD', staticReviewStatus='STATIC_PT_DESIGN_REVIEW_COMPLETE',
                    sourceMutation=False, productTestsExecuted=0, compilerOrJvmExecuted=False,
                    actualBackendActions=0, heldFourInitializations=0, refusalRetry=False,
                    newAcceptance=0, formalUpdated=False, effortRate=None, whole451Accepted=False,
                    ptExecutionExempt=False, measuredCoverage=None,
                    tool=dict(path=str(Path(__file__).relative_to(R)), sha256=sha(Path(__file__))))
    (O / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(actualExit=0, staticDesignCases=14, dynamicTests=0, manifestSha256=sha(O / 'manifest.json'))))


if __name__ == '__main__':
    main()
