"""Independent metadata qualification; does not launch formatter or Product code."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import platform
import subprocess

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21744-explicit-ordinary-test-format-audit-v1/manifest.json'
m = json.loads(p.read_text())
assert sha(p) == '5a5b61a9975861232c92a4af0759484e5d4fdccb083cc202a7fa7ad9d552b52a'
assert m['actualExit'] == m['stage']['actualExit'] == 0 and not m['stage']['timedOut']
assert m['checkedFiles'] == m['formattedFiles'] == 85 and m['unformattedFiles'] == []
b = m['begin']
assert not b['productExecution'] and not b['sourceMutation']
publisher = r.parent / 'pgpt-runs/PG379/publish_characterization_delta.py'
assert sha(publisher) == b['publisherSha256']
held = set(b['heldNamesExcludedBeforeIO'])
names = {n.value for n in ast.walk(ast.parse(publisher.read_text()))
    if isinstance(n, ast.Constant) and isinstance(n.value, str)
    and n.value.startswith('src/') and '/src/test/java/' in n.value
    and n.value.endswith('.java') and Path(n.value).name not in held}
assert names == set(b['inputHashes']) and len(names) == 85
for n, h in b['inputHashes'].items():
    assert Path(n).name not in held and sha(r / n) == h
    assert hashlib.sha256(subprocess.check_output(['git', 'show', m['source'] + ':' + n])).hexdigest() == h
for n, h in b['toolHashes'].items():
    assert Path(n).name not in held and sha(Path(n)) == h
assert len(b['toolHashes']) == 7
for n, h in m['files'].items():
    assert Path(n).name not in held and sha(p.parent / n) == h
assert json.loads((p.parent / 'begin.json').read_text()) == b
stage = m['stage']
command = stage['command']
i = command.index('--dry-run')
assert command[i:] == ['--dry-run', '--set-exit-if-changed'] + sorted(names)
assert stage['stdoutSha256'] == sha(p.parent / 'format-check.stdout')
assert stage['stderrSha256'] == sha(p.parent / 'format-check.stderr')
assert (p.parent / 'format-check.stdout').read_bytes() == b''
assert (p.parent / 'format-check.stderr').read_bytes() == b''
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21746-explicit-ordinary-format-independent-post-v1'
assert not out.exists()
out.mkdir()
result = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(),
    checkerSource=head, checkerSha256=sha(Path(__file__)), source=m['source'],
    original=dict(path=str(p.relative_to(r)), sha256=sha(p)), checkedFiles=85,
    unformattedFiles=0, inputBytesUnchanged=True, formatterReexecuted=False,
    productTests=0, newMethods=0, newSourceProofs=0, newAcceptance=0,
    wholeF03Accepted=False, whole451Accepted=False, os=platform.platform(), effortRate=None)
(out / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, checkedFiles=85, manifestSha256=sha(out / 'manifest.json'))))
