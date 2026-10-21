"""Exact source-only catch inventory; hints are not accepted fixes or non-applicability."""
import hashlib
import json
import os
import re
from collections import Counter
from pg5940_private_lock_compile import ROOT, W, BASE, sha

SOURCE = '1b663c1b0271c3e9318701a16e12b378e1ffaa5d'
LEX = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][A-Za-z0-9_$]*|[^\s]')


def balanced(tokens, at, opening, closing):
    if at >= len(tokens) or tokens[at][0] != opening:
        raise ValueError('explicit opening delimiter')
    depth = 1
    for end in range(at+1, len(tokens)):
        if tokens[end][0] == opening: depth += 1
        elif tokens[end][0] == closing: depth -= 1
        if depth == 0: return end
    raise ValueError('complete closed Java catch delimiters')


def sites(text):
    tokens = [(('LITERAL' if m.group().startswith(('"', "'")) else m.group()), m.start())
              for m in LEX.finditer(text) if not m.group().startswith(('//', '/*'))]
    rows = []
    for at, (value, offset) in enumerate(tokens):
        if value != 'catch': continue
        parameter_end = balanced(tokens, at+1, '(', ')')
        header = [t for t, _ in tokens[at+2:parameter_end]]
        if 'SQLException' not in header: continue
        end = balanced(tokens, parameter_end+1, '{', '}')
        body = [t for t, _ in tokens[parameter_end+2:end]]
        variable = header[-1]
        guarded = any(body[i:i+4] == ['preserveFatal', '(', variable, ')'] for i in range(len(body)-3))
        kind = ('GUARDED_REVIEW' if guarded else 'SQLSTATE_REVIEW' if 'getSQLState' in body
                else 'TRANSLATION_REVIEW' if 'new' in body else 'RETHROW_OR_ATTACH_REVIEW')
        rows.append(dict(beginLine=text.count('\n', 0, offset)+1, catchVariable=variable,
            parameterTokens=header, category=kind,
            bodyTokenSha256=hashlib.sha256(json.dumps(body).encode()).hexdigest(),
            reviewStatus='PENDING_EXACT_APPLICABILITY_AND_PREVENTION_EVIDENCE'))
    return rows


def main():
    qp = BASE/'PG6540-jdbc-graph-qualification-v1/manifest.json'
    if sha(qp) != '34fa4259f6c8a0ab250c1aba63b2e03346dd5d75364f9d5f4ce41bb4f4255222':
        raise ValueError('immutable current23 qualification')
    q = json.loads(qp.read_bytes()); pp = W/'pg6540-jdbc-graph-qualification-v1/manifest.safe.json'
    if sha(pp) != q['privateManifestSha256'] or q['source'] != SOURCE or q['actualExit'] != 0:
        raise ValueError('qualified Main source and original receipt')
    proof = json.loads(pp.read_bytes())
    current = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(current) != 851 or current != proof['allSourceHashes']:
        raise ValueError('all851 current Main bytes frozen before inventory')
    rows = []
    for path, digest in sorted(current.items()):
        if path.split('/')[1] not in ('schubert-nk-api', 'schubert-nk-web'): continue
        for value in sites((ROOT/path).read_text()):
            rows.append(dict(siteId='SQLCATCH-'+str(len(rows)+1).zfill(3), sourcePath=path,
                             sourceSha256=digest, **value))
    counts = Counter(r['category'] for r in rows)
    if len(rows) != 113 or counts != Counter(GUARDED_REVIEW=15, TRANSLATION_REVIEW=34,
            SQLSTATE_REVIEW=3, RETHROW_OR_ATTACH_REVIEW=61):
        raise ValueError('explicit113 before-fix lexical scope; unexpected scope requires review')
    out = BASE/'PG6542-jdbc-catch-inventory-v1'; os.umask(0o077); out.mkdir()
    with (out/'sites.json').open('x') as f:
        json.dump(rows, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    value = dict(actualExit=0, source=SOURCE, inputQualificationSha256=sha(qp), sites=113,
        categoryCounts=dict(counts), inventorySha256=sha(out/'sites.json'), scope='API_WEB_EXPLICIT_SQL_EXCEPTION_CATCH_ONLY',
        nonSqlBroadCatchesNotAutomaticallyCovered=True, acceptedSites=0, closedBugs=0,
        testsExecuted=0, vmActions=0, formalAccepted=False, ptAlternativeCompleted=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, sites=113, counts=dict(counts), acceptedSites=0, manifestSha256=sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
