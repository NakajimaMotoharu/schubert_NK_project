"""Classify only observed signals with identical freshly compiled synthetic bytes."""

from collections import Counter
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import runpy
import subprocess
from tempfile import TemporaryDirectory


INPUT = Path(__file__).parent
history = runpy.run_path(str(INPUT / '5365_g07_public_history_utc42.py'))
unit = runpy.run_path(str(INPUT / '5393_f02_protocol_serialization.py'))
C, H, V, R = (unit[key] for key in ('C', 'H', 'V', 'R'))
OPS, pin, git, read, digest = (history[key] for key in ('OPS', 'pin', 'git', 'read', 'digest'))
EXPECTED = {40624: 1, 40626: 10, 40630: 2, 40632: 11}


def compile_fixture(root, number):
    src = root / 'src'
    sources = []
    if number in {40624, 40626, 40632}:
        sources += unit['PREVIOUS']['fixtures'](src)
    if number in {40630, 40632}:
        sources += [C['write_fixture'](src, origin, f'public {target} field;')
                    for _, origin, target, _ in unit['CASES']]
    if number in {40624, 40630}:
        sources += [C['write_fixture'](src, unit['P'] + module + '.Anchor', C['MARKER'])
                    for module in H['MODULES']]
    else:
        sources += (C['inputs'](src) + R['additional_sources'](src)
                    + V['fixture_sources'](src) + unit['SUPPORT']['fixture'](src))
    output = root / 'classes'
    command = [H['JAVA'].with_name('javac'), '--release', '25', '-Xlint:all', '-Werror',
               '-proc:none', '-d', output, *sources]
    compiled = subprocess.run(command, capture_output=True, timeout=30)
    assert compiled.returncode == 0 and not compiled.stdout and not compiled.stderr
    return {f.relative_to(output).as_posix().removesuffix('.class').replace('/', '.'): digest(f.read_bytes())
            for f in output.rglob('*.class')}


def main():
    original = next(OPS.glob('PG40652-*')) / 'manifest.json'
    raw = read(original)
    before = raw['scans']['textCommitDiffs']
    assert before['actualExit'] == raw['actualExit'] == 1
    assert before['rules'] == {'generic-api-key': 24}
    assert raw['scans']['gzipPublicStreams']['actualExit'] == 0
    assert not raw['gzipVersions'] and not raw['binaryMetadataOnly']
    signals = {row['start'] for row in before['signalLocations']}
    assert len(signals) == 24 and all(row['start'] == row['end'] for row in before['signalLocations'])
    scanned, projection = io.BytesIO(), io.BytesIO()
    counts, classified = Counter(), []
    with TemporaryDirectory(dir='/dev/shm', prefix='pgpt-current-synthetic-digest-') as work:
        for commit in raw['commits']:
            parent = git('rev-parse', commit + '^').decode().strip()
            inventory = git('diff', '--no-renames', '--numstat', '-z', parent, commit)
            for item in filter(None, inventory.split(b'\0')):
                added, deleted, path = item.decode().split('\t', 2)
                assert (added, deleted) != ('-', '-')
                patch = git('diff', '--no-ext-diff', '--no-textconv', '--text', '--no-renames',
                            '--unified=0', parent, commit, '--', path)
                header = path + ' ' + commit
                low, high = history['add'](scanned, header, patch)
                local = sorted(line - low for line in signals if low <= line <= high)
                if local:
                    filename = Path(path)
                    number = int(filename.parent.name.split('-', 1)[0].removeprefix('PG'))
                    assert number in EXPECTED and counts[number] == 0
                    assert filename.name == 'manifest.json' and filename.is_relative_to(OPS) and deleted == '0'
                    body = git('show', commit + ':' + path)
                    fixture = json.loads(body)
                    assert fixture['productTests'] == fixture.get('productJars', fixture.get('actualProductJars')) == 0
                    assert fixture['receipts']['compile-fixture']['actualExit'] == 0
                    expected = fixture['inputPhysical']
                    rebuilt = compile_fixture(Path(work) / str(number), number)
                    assert expected and all(rebuilt[key] == value for key, value in expected.items())
                    lines = patch.split(b'\n')
                    for line in local:
                        marker = re.fullmatch(rb'\+\s*"([^"]+)": "([0-9a-f]{64})",?', lines[line])
                        assert marker is not None
                        key, value = (part.decode() for part in marker.groups())
                        assert expected[key] == value
                        lines[line] = lines[line].replace(marker[2], b'VERIFIED_CHECKSUM')
                    patch = b'\n'.join(lines)
                    counts[number] = len(local)
                    classified.append(dict(path=path, sourceCommit=commit, sha256=digest(body),
                                           provenDigests=len(local), fixtureClasses=len(expected)))
                history['add'](projection, header, patch)
    assert digest(scanned.getvalue()) == before['sha256'] and counts == EXPECTED
    scanner = Path(raw['tool']['path'])
    assert pin(scanner) == raw['tool']
    checks = history['scan'](scanner, {'checksumVerifiedText': projection})['checksumVerifiedText']
    assert checks['actualExit'] == 0 and not checks['signalLocations']
    out = OPS / 'PG40654-g07-current-compiler-evidence-delta-independent-v1'
    out.mkdir()
    manifest = out / 'manifest.json'
    with manifest.open('x') as output:
        json.dump(dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                       source=raw['source'], productionCore=raw['productionCore'],
                       previousCursor=raw['previousCursor'], newCursor=raw['source'],
                       first=pin(original), tool=raw['tool'], verificationEvidence=classified,
                       syntheticClassShaSignals=24, syntheticCompileOnly=4, secretFindings=0,
                       projectedTextCheck=checks, rawSecretsStored=0, productTestsExecuted=0,
                       gitCommitCount=len(raw['commits']), textPathVersions=len(raw['textPathVersions']),
                       wholeG07=False, whole451=False), output, indent=2)
        output.write('\n')
    print(pin(manifest))


if __name__ == '__main__':
    main()
