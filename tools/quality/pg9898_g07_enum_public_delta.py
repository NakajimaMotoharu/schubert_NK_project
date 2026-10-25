"""Explicit G07 public text delta only; held unverified witness files are not opened."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG9898-g07-enum-public-delta-v1'
HELD = {'tools/quality/architecture/SnapshotKeyCloseWitness.java','tools/quality/pg9892_snapshot_key_close_witness.py'}
RULES = {
    'PRIVATE_KEY_PEM': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'GITHUB_CREDENTIAL': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b'),
    'AWS_ACCESS_KEY_ID': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')}


def main():
    assert not OUT.exists()
    raw = subprocess.check_output(['git','diff','--name-only','-z','5bfa3f761','--'],cwd=ROOT)
    raw += subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT)
    assert raw.endswith(b'\0')
    names = set(raw.decode().split('\0')[:-1])-HELD
    rows, findings = [], []
    for name in sorted(names):
        path = ROOT/name
        assert name.startswith(('documents/','evidence/01_PT/','tools/quality/pg9896_','tools/quality/pg9898_'))
        assert '/private' not in name and not path.is_symlink() and path.is_file()
        content = path.read_bytes()
        assert b'\0' not in content
        content.decode('utf-8')
        rows.append(dict(path=name,sha256=hashlib.sha256(content).hexdigest()))
        for rule, pattern in RULES.items():
            findings.extend(dict(path=name,rule=rule,line=content[:m.start()].count(b'\n')+1) for m in pattern.finditer(content))
    assert rows
    value = dict(actualExit=1 if findings else 0,files=rows,findings=findings,
        scope='EXPLICIT_G07_PUBLIC_TEXT_DELTA_THREE_FORMAT_PATTERNS_NOT_WHOLE_G07',
        heldFilesNotRead=sorted(HELD),wholeWorktreeCleanClaim=False,actualSecretCount=None,
        originalEntryFailure=dict(actualExit=1,reason='missing pyflakes import before scanner main; no files scanned'),
        sharedRunnerNotUsed='its all-untracked scope would include held WIP; no shared-runner main executed',
        testsExecuted=0,externalActions=0,formalUpdated=False)
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=value['actualExit'],files=len(rows),findings=len(findings),
        manifestSha256=hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest())))
    raise SystemExit(value['actualExit'])

if __name__ == '__main__':
    main()
