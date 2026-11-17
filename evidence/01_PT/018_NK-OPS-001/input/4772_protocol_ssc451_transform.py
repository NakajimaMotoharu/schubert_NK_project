"""SSC451 bounded source rewrite; parse-only javac case inventory is the independent input.

No production definition/execution, private reflection, test expected-value generation or exclusions.
"""
from pathlib import Path
import base64, hashlib, json, re, subprocess

r = Path.cwd()
b = r / 'evidence/01_PT/018_NK-OPS-001'
out = b / 'evidence/PG37588-ssc451-before-and-rewrite-v3'
assert not out.exists()
out.mkdir()
root = r / 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol'
dec = lambda s: base64.b64decode(s).decode()
rows = []
for line in Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg37582-protocol-dispatch-syntax/switches.tsv').read_text().splitlines():
    a = line.split('\t')
    if a[0] == 'SW':
        rows.append(dict(path=str((r / dec(a[1])).resolve()), start=int(a[2]), end=int(a[3]), parent=a[4], variable=dec(a[5]), selector=dec(a[6]), cases=[]))
    elif a[0] == 'CASE':
        rows[-1]['cases'].append(dict(labels=dec(a[1]).splitlines(), kind=a[2], body=dec(a[3])))
assert len(rows) == 17
paths = {root / n for n in ['codec/FieldCodec.java', 'file/LargeResultRecordCodec.java', 'file/MediaDescriptorValidator.java', 'layout/PayloadSemanticValidator.java']}
paths.update(Path(x['path']) for x in rows)
assert len(paths) == 7
originals = {p: p.read_text() for p in paths}
for p, text in originals.items():
    dest = out / p.relative_to(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)

for p in paths:
    s = originals[p]
    own = [x for x in rows if Path(x['path']) == p]
    for n, row in reversed(list(enumerate(own))):
        cases = row['cases']
        string = any(c['labels'] and c['labels'][0].startswith(('"', 'LITERAL_')) for c in cases)
        selector = row['selector'][1:-1]  # javac includes mandatory parentheses
        enum = 'MediaType' if p.stem == 'MediaDescriptorValidator' else 'Presence' if selector == 'presence' else 'WireType'
        type_ = 'String' if string else enum
        variable = 'dispatchValue' + str(n)
        lines = [f'final {type_} {variable} = java.util.Objects.requireNonNull({selector});']
        assignment = row['variable'].rsplit(' ', 1)[-1]
        for i, c in enumerate(cases):
            labels = c['labels']
            fallback = not labels or (not string and i == len(cases) - 1)
            if fallback:
                head = 'else'
            else:
                condition = ' || '.join(f'{label}.equals({variable})' if string else f'{variable} == {enum}.{label}' for label in labels)
                head = ('if' if i == 0 else 'else if') + f' ({condition})'
            body = c['body']
            if row['parent'] == 'RETURN':
                if c['kind'] == 'BLOCK':
                    body = re.sub(r'\byield\b', 'return', body)[1:-1]
                elif c['kind'] != 'THROW':
                    body = 'return ' + body + ';'
            elif row['parent'] == 'VARIABLE':
                if c['kind'] == 'BLOCK':
                    body = re.sub(r'\byield\b', assignment + ' =', body)[1:-1]
                elif c['kind'] != 'THROW':
                    body = assignment + ' = ' + body + ';'
            elif c['kind'] == 'BLOCK':
                body = body[1:-1]
            lines.append(head + ' {\n' + body + '\n}')
        replacement = '{\n' + '\n'.join(lines) + '\n}'
        if row['parent'] == 'VARIABLE':
            replacement = row['variable'] + ';\n' + replacement
        s = s[:row['start']] + replacement + s[row['end']:]
    p.write_text(s)

companions = []
for name, rel in [('FieldCodec', 'codec'), ('LargeResultRecordCodec', 'file'), ('MediaDescriptorValidator', 'file'), ('PayloadSemanticValidator', 'layout')]:
    p = root / rel / (name + '.java')
    s = p.read_text()
    s = s.replace('public final class ' + name + ' {', 'public interface ' + name + ' {', 1)
    ctor = re.search(r'  private ' + name + r'\(\) \{\}\n', s)
    assert ctor
    opening = s.index('public interface ' + name + ' {') + len('public interface ' + name + ' {')
    fields = s[opening:ctor.start()]
    assert not fields.strip() or fields.lstrip().startswith('private static final')
    s = s[:opening] + '\n' + s[ctor.end():]
    if fields.strip():
        companion = name + 'Rules'
        names = re.findall(r'private static final [^=;]+?\b(\w+)\s*=', fields)
        assert names
        package = 'dev.codex.schubert.nk.protocol.' + rel
        imports = ''.join('import static ' + package + '.' + companion + '.' + field + ';\n' for field in names)
        s = s.replace('package ' + package + ';', 'package ' + package + ';\n\n' + imports, 1)
        original_imports = '\n'.join(line for line in originals[p].splitlines() if line.startswith('import '))
        new = p.with_name(companion + '.java')
        assert not new.exists()
        new.write_text('package ' + package + ';\n\n' + original_imports + '\n\n/** Immutable non-public grammar cache. Trace: SSC451, SS322/323/333. */\ninterface ' + companion + ' {\n' + fields.replace('private static final ', '') + '\n}\n')
        companions.append(str(new.relative_to(r)))
    p.write_text(s)

manifest = dict(actualExit=0, operation='SOURCE_REWRITE_NOT_TEST_PASS', sourceBefore=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), switches=rows, originalSources={str(p.relative_to(r)): hashlib.sha256(v.encode()).hexdigest() for p,v in originals.items()}, companionSources=companions, privateReflection=False, meaningfulInstanceCreated=False, original152ExpectedChanged=False, testsExecuted=0, newAcceptance=0)
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(dict(rewrittenMain=7, companions=len(companions), switchStatements=len(rows), testsExecuted=0))
