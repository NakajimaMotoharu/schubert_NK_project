"""Resolve staged scanner signals exclusively against the qualified Git input inventory."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


OPS = Path('evidence/01_PT/018_NK-OPS-001/evidence')
SCANNER = (Path.cwd().parent/'toolchain/gitleaks-8.30.1-linux-x64/gitleaks').resolve()


def git(*args):
    return subprocess.check_output(['git', *args])


def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()


def scan(data):
    with TemporaryDirectory(dir='/dev/shm', prefix='pgpt-main-inventory-scan-') as tmp:
        report = Path(tmp)/'signals.json'
        child = subprocess.run([SCANNER, 'stdin', '--redact=100', '--no-banner', '--no-color',
                                '--report-format=json', '--report-path', report],
                               input=data, capture_output=True, timeout=30)
        hits = json.loads(report.read_bytes()) if report.is_file() else []
        return child.returncode, hits


def main():
    unit = next(OPS.glob('PG40670-*'))
    proof = next(OPS.glob('PG40672-*/manifest.json'))
    independent = json.loads(proof.read_bytes())
    assert independent['actualExit'] == 0 and independent['inputFileCount'] == 1035
    core = independent['productionCore']
    inventory_file = unit/'main-inventory.json'
    inventory = json.loads(inventory_file.read_bytes())
    assert git('show', ':' + inventory_file.as_posix()) == inventory_file.read_bytes()
    tree = git('write-tree').decode().strip()
    patch = git('diff', '--cached', '--no-ext-diff', '--unified=0')
    before, signals = scan(patch)
    assert before == 1 and len(signals) == 43
    assert all(hit['RuleID'] == 'generic-api-key' and hit['StartLine'] == hit['EndLine']
               for hit in signals)
    hits = {hit['StartLine'] for hit in signals}
    rewritten, rows = [], []
    current = None
    for number, line in enumerate(patch.split(b'\n'), 1):
        if line.startswith(b'+++ b/'):
            current = line[6:].decode()
        if number in hits:
            assert current == inventory_file.as_posix()
            result = re.fullmatch(rb'\+\s*"([^\"]+)": "([0-9a-f]{64})",?', line)
            assert result is not None
            source, value = (group.decode() for group in result.groups())
            assert inventory[source] == value == hash_bytes(git('show', f'{core}:{source}'))
            line = line.replace(result.group(2), b'VERIFIED_CHECKSUM')
            rows.append(dict(line=number, gitInput=source))
        rewritten.append(line)
    assert len(rows) == len(hits) == 43
    checked, unresolved = scan(b'\n'.join(rewritten))
    assert checked == 0 and not unresolved
    out = OPS/'PG40674-f02-current-main-inventory-publication-v1'
    out.mkdir()
    manifest = out/'manifest.json'
    with manifest.open('x') as stream:
        json.dump(dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       source=independent['source'], productionCore=core, stagedTree=tree,
                       scannedStageSha256=hash_bytes(patch), initialScannerExit=before,
                       independentlyVerifiedGitInputDigests=rows, secretFindings=0,
                       reconciledScannerExit=checked, recordedSecretValues=0, dynamicTestsRun=0,
                       wholeG07=False), stream, indent=2)
        stream.write('\n')
    print(str(manifest), hash_bytes(manifest.read_bytes()))


if __name__ == '__main__':
    main()
