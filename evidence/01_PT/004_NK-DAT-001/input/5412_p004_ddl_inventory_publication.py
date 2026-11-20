"""Verify the staged DDL checksums identified by the redacted publication scan."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import runpy


ROOT = Path('evidence/01_PT')
G = runpy.run_path(str(ROOT/'018_NK-OPS-001/input/5409_f02_main_inventory_prepublication.py'))
git, sha, scan = (G[key] for key in ('git', 'hash_bytes', 'scan'))
DATA = ROOT/'004_NK-DAT-001/evidence'


def main():
    root = next(DATA.glob('PG40680-*'))
    inventory = root/'ddl-inventory.json'
    core = json.loads((root/'manifest.json').read_bytes())['productionCore']
    body = inventory.read_bytes()
    assert git('show', ':'+inventory.as_posix()) == body
    checksums = json.loads(body)['migrationSha256']
    patch = git('diff', '--cached', '--no-ext-diff', '--unified=0')
    exit_code, signals = scan(patch)
    assert exit_code == 1 and len(signals) == 2
    assert all(row['RuleID'] == 'generic-api-key' and row['StartLine'] == row['EndLine'] for row in signals)
    slots = {row['StartLine'] for row in signals}
    projected, resolved = [], []
    current = None
    for i, line in enumerate(patch.split(b'\n'), 1):
        if line.startswith(b'+++ b/'):
            current = line[6:].decode()
        if i in slots:
            assert current == str(inventory)
            raw = re.fullmatch(rb'\+\s*"([^\"]+)": "([0-9a-f]{64})",?', line)
            assert raw is not None
            name, digest = (part.decode() for part in raw.groups())
            assert checksums[name] == digest == sha(git('show', f'{core}:{name}'))
            resolved.append(name)
            line = line.replace(raw[2], b'VERIFIED_CHECKSUM')
        projected.append(line)
    assert len(set(resolved)) == 2
    final, remainder = scan(b'\n'.join(projected))
    assert final == 0 and not remainder
    out = DATA/'PG40682-p004-ddl-publication-independent-v1'
    out.mkdir()
    manifest = out/'manifest.json'
    with manifest.open('x') as stream:
        json.dump(dict(actualExit=0, productionCore=core, checkedStageSha256=sha(patch),
                       scannedTree=git('write-tree').decode().strip(), initialScannerExit=1,
                       identifiedAsGitSqlDigests=resolved, reconciledScannerExit=0, secretFindings=0,
                       filesOrDbRuntimeExecuted=0, terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  stream, indent=2)
        stream.write('\n')
    print(str(manifest), sha(manifest.read_bytes()))


if __name__ == '__main__':
    main()
