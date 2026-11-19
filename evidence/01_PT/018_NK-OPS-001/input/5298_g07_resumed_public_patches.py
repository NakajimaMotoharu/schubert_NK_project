"""Run the pinned redacted scanner only on a fixed, small, published text patch range."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess

D = next(Path('documents/400_PGPT/470_PMO').glob('601_*'))
E = Path('evidence/01_PT/018_NK-OPS-001/evidence')
ALLOWED = (
    'documents/400_PGPT/450_品質/',
    'documents/400_PGPT/470_PMO/',
    'documents/900_OTHER/910_台帳/',
    'evidence/01_PT/018_NK-OPS-001/',
)
TOOLS = frozenset({
    'tools/quality/architecture/ModuleDependencyAudit.java',
    'tools/quality/jacoco_readonly_exec_subset.py',
    'tools/quality/jacoco_readonly_exec_subset_encoding_test.py',
})


def git(*args):
    return subprocess.check_output(['git', *args], timeout=20)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main(start_pattern='638_G07*', expected_commits=10, expected_files=67, added_line_limit=4000):
    start = json.loads(next(D.glob(start_pattern)).read_bytes())['values']
    first, last = start['fromCommit'], start['source']
    assert last == git('rev-parse', 'HEAD').decode().strip()
    chain = git('rev-list', '--reverse', f'{first}..{last}').decode().splitlines()
    assert len(chain) == expected_commits
    file_set = set()
    lines = 0
    for commit in chain:
        assert len(git('rev-list', '--parents', '-n', '1', commit).split()) == 2
        changes = git('diff-tree', '--no-commit-id', '-r', '-z', '--numstat', '--no-renames', commit)
        for change in changes.split(b'\0')[:-1]:
            added, removed, raw = change.decode().split('\t', 2)
            assert added.isdecimal() and removed.isdecimal()
            assert raw in TOOLS or raw.startswith(ALLOWED)
            file_set.add(raw)
            lines += int(added)
    assert len(file_set) == expected_files and lines <= added_line_limit
    tool, = start['oracleReferences']
    assert sha(Path(tool['path']).read_bytes()) == tool['sha256']
    command = [
        tool['path'], 'git', '--no-banner', '--no-color', '--redact=100', '--ignore-gitleaks-allow',
        '--gitleaks-ignore-path=/dev/null', '--report-format=json', '--report-path=-', '--timeout=45',
        '--log-opts=--no-merges --no-renames ' + first + '..' + last, '.',
    ]
    env = {k: v for k, v in os.environ.items() if not k.startswith('GITLEAKS_')}
    scanned = subprocess.run(command, capture_output=True, env=env, timeout=55, check=False)
    assert scanned.returncode in (0, 1)
    payload = json.loads(scanned.stdout) if scanned.stdout.strip() else []
    assert isinstance(payload, list)
    coordinates = [
        dict(commit=r['Commit'], file=r['File'], rule=r['RuleID'], startLine=r['StartLine'], endLine=r['EndLine'],
             startColumn=r['StartColumn'], endColumn=r['EndColumn'])
        for r in payload
    ]
    assert all(r['commit'] in chain and r['file'] in file_set for r in coordinates)
    assert (scanned.returncode == 0) == (not coordinates)
    result = dict(actualExit=scanned.returncode, start=first, source=last, commits=len(chain), distinctFiles=len(file_set),
                  addedLinesAcrossCommits=lines, candidates=coordinates, found=len(coordinates),
                  confirmedSecrets=0 if not coordinates else None, unresolved=len(coordinates),
                  command=command, rawMatchPublished=False, binaryArtifactsInRange=0,
                  coveredSlice='Committed text patches only', fullTreeOrHistoryScan=False,
                  archiveExpansion=False, wholeG07Accepted=False, whole451Accepted=False,
                  productTests=0, newFormalAcceptance=0,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = E / start['run']
    out.mkdir()
    file = out / 'manifest.json'
    file.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(dict(proof=str(file), sha256=sha(file.read_bytes()), actualExit=result['actualExit'],
               found=result['found'], files=result['distinctFiles']))


if __name__ == '__main__':
    main()
