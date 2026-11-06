"""Bind static review to exact existing Main evidence; no JVM/Product/DB operation."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
base = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'
names = [base + 'persistence/' + n + '.java' for n in
    ('UserQueryRepository', 'LogQueryRepository', 'UserQueryException', 'LogQueryException')]
names.append(base + 'database/RequiredColumn.java')
held = {'RootFailedStartRecoveryTest.java', 'RootFailedStartPairRecoveryTest.java',
        'SnapshotKeyCloseWitness.java', 'pg9892_snapshot_key_close_witness.py'}
assert all(Path(n).name not in held for n in names)
normalp = r.parent / 'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json'
assert sha(normalp) == '1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618'
normal = json.loads(normalp.read_text())
assert normal['actualExit'] == 0 and normal['source'] == '4217e14083c6ecac116216e08d57f4361eb2f12d'
inputs = {}
for n in names:
    p = r / n
    h = sha(p)
    assert normal['begin']['inputHashes'][n] == h
    assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + n])).hexdigest() == h
    inputs[n] = h
refs = []
for n, expected in [
    ('evidence/01_PT/018_NK-OPS-001/evidence/PG21706-current4217-main-style-binding-v1/manifest.json', 'e13126918bb2510850c82125826816a4b39fc2c7d0804d4c7c93249dc247ccc0'),
    ('evidence/01_PT/018_NK-OPS-001/evidence/PG21708-current4217-style-binding-independent-v1/manifest.json', '3e94d6d8d907996a783a98bafb9c14713087269b942577997d5e62037fad5c14')]:
    p = r / n
    assert sha(p) == expected and json.loads(p.read_text())['actualExit'] == 0
    refs.append(dict(path=n, sha256=expected))
docs = []
for directory, prefix in [('documents/300_SS', '312_'), ('documents/300_SS', '332_'),
                          ('documents/300_SS', '323_'), ('documents/200_UI', '234_')]:
    p = next((r / directory).rglob(prefix + '*.md'))
    data = subprocess.check_output(['git', 'show', 'origin/main:' + str(p.relative_to(r))])
    text = data.decode()
    lines = [dict(line=i, text=l) for i, l in enumerate(text.splitlines(), 1)
        if ('borrowed repository' in l or 'Statement/ResultSet close' in l
            or '99,999,950' in l or '99,999,900' in l or 'SQL NULL' in l
            or 'wasNull' in l or 'SQLstate' in l or 'UTC' in l
            or '999999' in l or '9001' in l or '50件' in l or '100件' in l)]
    assert lines
    docs.append(dict(path=str(p.relative_to(r)), originMain=subprocess.check_output(['git', 'rev-parse', 'origin/main'], text=True).strip(), sha256=hashlib.sha256(data).hexdigest(), anchors=lines))
spec = r / 'evidence/01_PT/018_NK-OPS-001/3606_UserLog残SQL異常静的レビュー仕様.md'
assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(spec.relative_to(r))])).hexdigest() == sha(spec)
assert hashlib.sha256(subprocess.check_output(['git', 'show', head + ':' + str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG21754-user-log-sql-error-static-review-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0, atJST=datetime.datetime.now().astimezone().isoformat(), source=head,
    productionMainSource=normal['source'], driverSha256=sha(Path(__file__)), inputHashes=inputs,
    normalManifest=dict(path=str(normalp), sha256=sha(normalp)), existingStatic=refs, design=docs,
    specification=dict(path=str(spec.relative_to(r)), sha256=sha(spec)),
    reviewIds=['RV-ADM-SQLERR%03d' % i for i in range(1, 7)],
    productTests=0, productInvocations=0, fixturesCreated=0, newMethods=0,
    newSourceProofs=0, newAcceptance=0, reviewIsExecutedPT=False,
    dynamicHoldMaintained=True, refusalScopeUnresolved=True, ptExemptionGranted=False,
    coverageMeasured=False, coverage=None, effortRate=None)
(out / 'manifest.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(actualExit=0, reviews=6, productTests=0, manifestSha256=sha(out / 'manifest.json'))))
