"""Independent snapshot/source binding and sanitizer golden/negative checks; no scan rerun."""
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
from host_tool_invocation import capture, verify
from public_blob_scan import sanitize, sha

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
RAW = BASE / 'PG8968-public-blob-scan-v1'
OUT = BASE / 'PG8970-public-blob-scan-post-v1'
SLOT = ROOT.parent / 'pgpt-runs/PG379/pg8968-public-blob-scan-v1'
CONTENT = '05d73a7974da8df92228160b96d91e7a006768f3'
SOURCE = 'fb9fce0f91de3d9fdfa634fe277592700f915e45'


def load(path):
    return json.loads(path.read_bytes())


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    record = load(RAW / 'manifest.json')
    assert record['actualExit'] == 0 and record['source'] == SOURCE and record['contentCommit'] == CONTENT
    assert record['inventorySha256'] == sha((RAW / 'inventory.json').read_bytes())
    assert record['findingsSha256'] == sha((RAW / 'findings.json').read_bytes())
    assert sha((SLOT / 'canary.safe.json').read_bytes()) == record['canarySha256']
    canary = load(SLOT / 'canary.safe.json')
    assert canary['actualExit'] == 0 and canary['vendorExit'] == 1
    assert all(canary[key] for key in ('positiveDetected', 'inlineAllowIgnored', 'projectConfigIgnored', 'hiddenAndGitignoredFixturesDetected', 'safeFixtureUnflagged'))
    assert canary['rawOutputPersisted'] is False
    inventory = load(RAW / 'inventory.json')
    rows = {row['path']: row for row in inventory['rows']}
    assert len(rows) == len(inventory['rows']) == record['trackedBlobs']
    tree = subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', CONTENT], cwd=ROOT)
    observed = {}
    unsupported = []
    for item in tree.split(b'\0'):
        if not item:
            continue
        meta, path = item.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        name = path.decode()
        if kind == 'blob':
            observed[name] = (mode, oid)
        else:
            unsupported.append(name)
    assert set(observed) == set(rows)
    assert sorted(unsupported) == sorted(row['path'] for row in inventory['unsupported'])
    for name, row in rows.items():
        assert observed[name] == (row['gitMode'], row['gitObject'])
        path = SLOT / 'tracked' / name
        assert path.is_file() and not path.is_symlink()
        data = path.read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        assert row['lines'] == data.count(b'\n') + 1
    assert sum(row['bytes'] for row in rows.values()) == record['bytes']
    findings = load(RAW / 'findings.json')
    expected_keys = {'ruleId', 'path', 'startLine', 'endLine', 'inputSha256'}
    assert all(set(row) == expected_keys and row['path'] in rows and row['inputSha256'] == rows[row['path']]['sha256'] for row in findings)
    assert len(findings) == record['findings']
    terminal = load(SLOT / 'public-terminal.safe.json')
    process = load(SLOT / 'public-process.safe.json')
    assert terminal == record['terminal'] and terminal['actualExit'] in (0, 1)
    assert (terminal['actualExit'] == 0) == (len(findings) == 0)
    assert process['command'] == record['command'] and process['binarySha256'] == record['binarySha256']
    assert process['source'] == SOURCE and process['contentCommit'] == CONTENT
    assert process['cwd'] == str(SLOT) and process['pid'] == process['pgid'] and int(process['startTicks']) > 0
    assert record['maximumArchiveDepth'] == record['maximumDecodeDepth'] == 0
    assert record['rawOutputPersisted'] is record['formalUpdated'] is record['whole451SecretGateAccepted'] is False
    assert record['unsupportedNotPassed'] is True
    assert subprocess.check_output(['git', 'diff', '--name-only', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT) == b''
    # Independent literal oracle: sensitive/extra fields must not survive serialization.
    root = Path('/synthetic-public')
    known = {'sample.txt': {'sha256': '0' * 64, 'lines': 4}}
    row = dict(RuleID='aws-access-token', File='/synthetic-public/sample.txt', StartLine=2, EndLine=3,
               Secret='FICTITIOUS-SECRET-MUST-NOT-LEAK', Match='FICTITIOUS-CONTEXT',
               Entropy=9.99, Fingerprint='FICTITIOUS-FINGERPRINT', Author='PRIVATE-AUTHOR', Extra={'nested': 'PRIVATE'})
    result = sanitize(json.dumps([row]), known, root)
    assert result == [dict(ruleId='aws-access-token', path='sample.txt', startLine=2, endLine=3, inputSha256='0' * 64)]
    assert not any(value in json.dumps(result) for value in ('FICTITIOUS', 'PRIVATE', 'Secret', 'Match', 'Entropy', 'Fingerprint', 'Author', 'Extra'))
    cases = {
        'unknown-file': {'File': 'other.txt'}, 'parent-path': {'File': '../sample.txt'},
        'external-absolute': {'File': '/other/sample.txt'}, 'control-path': {'File': 'sample.txt\n'},
        'invalid-rule': {'RuleID': 'NOT A RULE'}, 'missing-rule': {'RuleID': None},
        'zero-line': {'StartLine': 0}, 'bool-line': {'StartLine': True},
        'reversed-lines': {'StartLine': 3, 'EndLine': 2}, 'past-eof': {'EndLine': 5},
        'missing-file': {'File': None}}
    rejected = []
    for name, delta in cases.items():
        changed = copy.deepcopy(row); changed.update(delta)
        try:
            sanitize(json.dumps([changed]), known, root)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError('unsafe metadata accepted')
    for name, raw in (('object-not-array', '{}'), ('array-member-not-object', '[null]'), ('invalid-json', '{')):
        try:
            sanitize(raw, known, root)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError('unsafe report accepted')
    assert sanitize('[]', known, root) == sanitize('null', known, root) == []
    verify(invocation)
    OUT.mkdir()
    value = dict(actualExit=0, timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(), source=SOURCE,
           contentCommit=CONTENT, scanManifestSha256=sha((RAW / 'manifest.json').read_bytes()),
           invocation=invocation, trackedBlobsRehashed=len(rows), bytes=record['bytes'],
           findings=record['findings'], scannerVendorExit=terminal['actualExit'],
           sanitizerGoldenCases=3, rejectedMetadataCases=rejected, canary=canary,
           fixedSnapshotBindingConfirmed=True, rawFindingFieldsAbsent=True, scannerRerun=False,
           findingsClassified=False, binaryOrContainerLimitedCount=record['binaryOrContainerLimitedCount'],
           historicalCommitsScanned=False, whole451SecretGateAccepted=False,
           productTestsExecuted=0, productCoverage=None, formalUpdated=False, newAccepted=0)
    with (OUT / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2); stream.write('\n')
    print(json.dumps({key: value[key] for key in ('actualExit', 'trackedBlobsRehashed', 'findings', 'sanitizerGoldenCases', 'binaryOrContainerLimitedCount')}))


if __name__ == '__main__':
    main()
