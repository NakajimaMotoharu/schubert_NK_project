"""Reconcile committed inventory checksums and scope the two offline JaCoCo files."""

from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import runpy


HERE = Path(__file__).resolve()
H = runpy.run_path(str(HERE.with_name('5365_g07_public_history_utc42.py')))
OPS, git, pin, read, sha = (H[name] for name in ('OPS', 'git', 'pin', 'read', 'digest'))
TOOLS = Path('tools/quality')
strict_exec = runpy.run_path(str(TOOLS/'jacoco_readonly_exec_subset.py'))['decode']
public_counts = runpy.run_path(str(TOOLS/'public_jacoco_exec_format_v1.py'))['parse']
COMPARATOR = 'dev/codex/schubert/characterization/ArtifactComparator'


def analyze_binaries(rows):
    result = []
    assert len(rows) == 2
    for ref in rows:
        path = Path(ref['path'])
        assert path.name == 'jacoco.exec' and path.is_relative_to(OPS)
        assert path.parent.name.startswith(('PG40656-', 'PG40658-'))
        published = git('show', ref['commit'] + ':' + ref['path'])
        assert len(published) == ref['bytes'] and sha(published) == ref['sha256']
        unit = read(path.with_name('manifest.json'))
        assert unit['actualNkChr'] == unit['actualProductTests'] == 0
        parse = strict_exec(published, {COMPARATOR, COMPARATOR+'$ComparisonResult'})
        public = public_counts(published)
        assert public['sessions'] == public['orderedSessions'] == public['asciiSessions'] == 1
        assert public['headers'] == 1 and public['bytes'] == public['consumedBytes']
        assert public['classes'] == parse['totalClassRecords'] and public['unusedPaddingSetBits'] == 0
        assert parse['sessions'][0]['labelBytesHex'] == unit['session'].encode('ascii').hex()
        result.append(dict(path=ref['path'], sha256=ref['sha256'], testScope='offline local JUnit',
                           source=unit['source'], proof=pin(path.with_name('manifest.json')),
                           headerRecords=public['headers'], sessions=public['sessions'],
                           recognizedComparatorTypes=len(parse['classes']), actualNative=False))
    return result


def main():
    receipt_path = next(OPS.glob('PG40676-*/manifest.json'))
    receipt = read(receipt_path)
    report = receipt['scans']['textCommitDiffs']
    assert report['actualExit'] == 1 and report['rules'] == {'generic-api-key': 43}
    assert receipt['scans']['gzipPublicStreams']['actualExit'] == 0
    assert not receipt['scans']['gzipPublicStreams']['signalLocations'] and len(receipt['gzipVersions']) == 9
    found = {row['start'] for row in report['signalLocations']}
    assert len(found) == 43
    preflight = next(OPS.glob('PG40674-*/manifest.json'))
    stage = read(preflight)
    core = stage['productionCore']
    expected_paths = {row['gitInput'] for row in stage['independentlyVerifiedGitInputDigests']}
    assert len(expected_paths) == 43 and stage['secretFindings'] == 0
    raw, checked = io.BytesIO(), io.BytesIO()
    seen = set()
    for commit in receipt['commits']:
        parent = git('rev-parse', commit+'^').decode().strip()
        for row in filter(None, git('diff', '--no-renames', '--numstat', '-z', parent, commit).split(b'\0')):
            added, deleted, path = row.decode().split('\t', 2)
            if (added, deleted) == ('-', '-'):
                continue
            args = ['--no-ext-diff', '--no-textconv', '--text', '--no-renames', '--unified=0',
                    parent, commit, '--', path]
            content = git('diff', *args)
            header = path+' '+commit
            first, last = H['add'](raw, header, content)
            masked = sorted(line-first for line in found if first <= line <= last)
            if masked:
                expected_inventory = next(OPS.glob('PG40670-*/main-inventory.json'))
                assert path == str(expected_inventory) and deleted == '0'
                inventory = read(expected_inventory)
                assert git('show', commit+':'+path) == expected_inventory.read_bytes()
                lines = content.split(b'\n')
                for index in masked:
                    check = re.fullmatch(rb'\+\s*"([^\"]+)": "([0-9a-f]{64})",?', lines[index])
                    assert check is not None
                    name, digest = (part.decode() for part in check.groups())
                    assert name not in seen and digest == inventory[name] == sha(git('show', f'{core}:{name}'))
                    seen.add(name)
                    lines[index] = lines[index].replace(check.group(2), b'VERIFIED_CHECKSUM')
                content = b'\n'.join(lines)
            H['add'](checked, header, content)
    assert seen == expected_paths and sha(raw.getvalue()) == report['sha256']
    scanner = Path(receipt['tool']['path'])
    assert pin(scanner) == receipt['tool']
    final = H['scan'](scanner, {'checksumVerifiedText': checked})['checksumVerifiedText']
    assert final['actualExit'] == 0 and not final['signalLocations']
    binaries = analyze_binaries(receipt['binaryMetadataOnly'])
    out = OPS/'PG40678-g07-reactor-a02-public-independent-v1'
    out.mkdir()
    manifest = out/'manifest.json'
    with manifest.open('x') as stream:
        json.dump(dict(actualExit=0, source=receipt['source'], productionCore=core,
                       previousCursor=receipt['previousCursor'], newCursor=receipt['source'],
                       terminalAtUTC=datetime.now(timezone.utc).isoformat(), first=pin(receipt_path),
                       tool=receipt['tool'], prepublicationGitProof=pin(preflight),
                       publicTextFiles=len(receipt['textPathVersions']), publicGzipVersions=9,
                       gitCommits=len(receipt['commits']), gitInputDigestSignals=len(seen),
                       examinedBinaries=binaries, secretFindings=0, secretValuesStored=0,
                       projectedTextCheck=final, productTestsExecuted=0, wholeG07=False, whole451=False),
                  stream, indent=2)
        stream.write('\n')
    print(pin(manifest))


if __name__ == '__main__':
    main()
