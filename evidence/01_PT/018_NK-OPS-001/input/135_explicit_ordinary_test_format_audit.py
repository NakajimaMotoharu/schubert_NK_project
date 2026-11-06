"""Read-only formatter audit of the already explicitly published ordinary Test allowlist."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import shutil
import subprocess
import pg9666_pagination_static as c

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
publisher = r.parent / 'pgpt-runs/PG379/publish_characterization_delta.py'
tree = ast.parse(publisher.read_text())
held = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java',
        'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}
names = sorted({n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)
    and isinstance(n.value, str) and n.value.startswith('src/')
    and '/src/test/java/' in n.value and n.value.endswith('.java')
    and Path(n.value).name not in held})
assert len(names) == 85
assert all(Path(n).name not in held for n in names)
inputs = {}
for n in names:
    p = r / n
    assert p.is_file() and not p.is_symlink()
    inputs[n] = sha(p)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
spec = r / 'evidence/01_PT/018_NK-OPS-001/3604_通常明示85Test整形監査仕様.md'
assert spec.is_file()
for p in [Path(__file__), spec]:
    assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(p.relative_to(r))])).hexdigest() == sha(p)
oldp = r / 'evidence/01_PT/016_NK-WEB-002/evidence/PG21660-business-mvc-format-v1/manifest.json'
old = json.loads(oldp.read_text())
for n, h in old['toolHashes'].items():
    assert sha(Path(n)) == h
cmd = old['stages']['check']['command']
cmd = cmd[:cmd.index('--dry-run')] + ['--dry-run', '--set-exit-if-changed'] + names
slot = r.parent / 'pgpt-runs/PG379/pg21744-explicit-ordinary-test-format-audit-v1'
assert not slot.exists()
slot.mkdir()
c.SLOT = slot
begin = dict(source=head, inputHashes=inputs, publisherSha256=sha(publisher),
    toolHashes=old['toolHashes'], driverSha256=sha(Path(__file__)),
    specSha256=sha(spec), startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    productExecution=False, sourceMutation=False, heldNamesExcludedBeforeIO=sorted(held))
(slot / 'begin.json').write_text(json.dumps(begin, indent=2) + '\n')
stage = c.step('format-check', cmd, r, timeout=120)
assert not stage['timedOut'] and stage['actualExit'] in (0, 1)
assert all(sha(r / n) == h for n, h in inputs.items())
out = (slot / 'format-check.stdout').read_text().splitlines()
assert not (slot / 'format-check.stderr').read_text().strip()
findings = sorted(set(x.strip() for x in out if x.strip()))
assert set(findings) <= set(names)
assert bool(findings) == (stage['actualExit'] == 1)
pub = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21744-explicit-ordinary-test-format-audit-v1'
assert not pub.exists()
pub.mkdir()
files = {}
for p in slot.iterdir():
    if p.is_file():
        shutil.copyfile(p, pub / p.name)
        files[p.name] = sha(pub / p.name)
m = dict(atJST=datetime.datetime.now().astimezone().isoformat(), actualExit=stage['actualExit'],
    inspectionCompleted=True, source=head, begin=begin, stage=stage, files=files,
    checkedFiles=len(names), unformattedFiles=findings, formattedFiles=len(names)-len(findings),
    sourceBytesUnchanged=True, productTests=0, newMethods=0, newAcceptance=0,
    wholeF03Accepted=False, whole451Accepted=False, effortRate=None)
(pub / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=m['actualExit'], checked=85, findings=len(findings),
    manifestSha256=sha(pub / 'manifest.json'), unformattedFiles=findings)))
