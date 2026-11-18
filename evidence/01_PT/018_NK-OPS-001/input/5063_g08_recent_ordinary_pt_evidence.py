"""Join six already completed ordinary PT receipts to Test IDs and exact public bytes."""
from datetime import datetime, timezone
from pathlib import Path
import gzip
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

BASE = Path('evidence/01_PT')
OPS = BASE / '018_NK-OPS-001'
E = OPS / 'evidence'
OUT = E / 'PG38798-g08-six-current-pt-evidence-v1'
MIG = BASE / '019_NK-MIG-001'
DAT = BASE / '004_NK-DAT-001'
BAT = BASE / '017_NK-BAT-001'
MSG = BASE / '006_NK-MSG-002'

RUNS = {
    38669: (MIG, '004', OPS, '4592', 11),
    38686: (DAT, '447', OPS, '4594', 8),
    38708: (BAT, '703', OPS, '4596', 18),
    38732: (BAT, '703', OPS, '4599', 18),
    38755: (BAT, '699', OPS, '4601', 10),
    38786: (MSG, '001', OPS, '4605', 4),
}
RRF = (
    'literalSqlAndUtcBindings', 'independentBooleanProjections', 'nullTransactionAndInterruptContracts',
    'missingProjectionAndCardinality', 'everySqlFailurePositionClosesOwnedResources',
    'uncheckedAndCloseFailurePrecedence', 'fatalProviderGraphIsNotDiscarded',
    'independentConnectionsCanRunConcurrently',
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text())


def ref(path):
    return {'path': str(path), 'sha256': sha(path.read_bytes())}


def saved(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def find_spec(directory, number):
    files = list(directory.glob(f'{number}_*.md'))
    assert len(files) == 1
    return files[0]


def method_ids_from_bat():
    mapping = {}
    for count, no in ((9, '703'), (9, '705'), (10, '699')):
        raw = find_spec(BAT, no)
        rows = re.findall(r'^\|((?:CLNPORT|CLNQUERY|BKPPORT)\d{3})\|([A-Za-z]+Test\.\w+)\|', raw.read_text(), re.M)
        assert len(rows) == count
        for test, qualified in rows:
            assert qualified not in mapping
            mapping[qualified] = (test, raw)
    return mapping


def test_binding(case, original, amendment, bat):
    owner = case['class'].rsplit('.', 1)[-1]
    name = case['method'].removesuffix('()')
    if owner in ('SchemaHistoryAdmissionTest', 'SchemaHistoryRowValueTest'):
        number = re.match(r'opsSchema(\d{3})', name)[1]
        return 'PT-OPS-SCHEMA' + number, amendment if number == '011' else original
    if owner == 'RunReferenceRepositoryPureJdbcTest':
        test_id = f'RRF-PURE-{RRF.index(name)+1:03d}'
        assert test_id in original.read_text()
        return test_id, original
    if owner == 'InboxOutcomeValueContractTest':
        case_number = int(re.match(r'outcome(\d{3})', name)[1])
        spec = find_spec(OPS, '4385')
        first, last = map(int, re.search(r'PT-IDEM-OUTCOME(\d{3})\.\.(\d{3})', spec.read_text()).groups())
        assert first <= case_number <= last
        return f'PT-IDEM-OUTCOME{case_number:03d}', spec
    return bat[owner + '.' + name]


def run_evidence(number, spec):
    program, canonical_no, rule_dir, rule_no, expected = spec
    original = find_spec(program, canonical_no)
    amendment = find_spec(rule_dir, rule_no)
    path = next(E.glob(f'PG{number}-*/manifest.json'))
    data = load(path)
    unit_path = path.parent / 'unit-manifest.json'
    unit = load(unit_path)
    assert data['actualExit'] == unit['actualExit'] == 0
    assert data['tests'] == unit['tests'] == expected
    assert all(unit[x] == 0 for x in ('failures', 'errors', 'skipped'))
    assert data['source'] == unit['begin']['source'] and data['productionCoreMain'] == unit['begin']['productionCoreMain']
    assert not any((unit['begin']['oldExecUnion'], data['oldExecCombined'], data['manualCoverageExclusions']))
    assert subprocess.run(['git', 'cat-file', '-e', data['source']+'^{commit}']).returncode == 0
    retention = load(path.parent / 'log-retention.json')
    archives = {item['original']['path']: item for item in retention['files']}
    references = []
    actual_cases = set()
    for name, digest in sorted(data['files'].items()):
        original_path = path.parent / name
        if original_path.is_file():
            actual = original_path
            raw = original_path.read_bytes()
            archived = False
        else:
            archived_item = archives[str(original_path)]
            actual = Path(archived_item['archived']['path'])
            assert ref(actual) == archived_item['archived']
            raw = gzip.decompress(actual.read_bytes())
            assert archived_item['original']['sha256'] == digest
            archived = True
        assert sha(raw) == digest
        references.append({'originalName': name, 'originalSha256': digest, 'actual': ref(actual),
                           'losslessGzip': archived})
        if name.startswith('original-TEST-') and name.endswith('.xml'):
            xml = ET.fromstring(raw)
            assert not any(xml.findall('.//' + x) for x in ('failure', 'error', 'skipped', 'system-err', 'system-out'))
            actual_cases.update((case.attrib['classname'], case.attrib['name']) for case in xml.findall('testcase'))
    declared = {
        (c['classname'], c['name']) for c in unit['begin']['expectedCases']
    }
    assert len(actual_cases) == expected and actual_cases == declared
    bat = method_ids_from_bat()
    pin = []
    for cls, method in sorted(actual_cases):
        test_id, spec_path = test_binding({'class': cls, 'method': method}, original, amendment, bat)
        pin.append({'testId': test_id, 'class': cls, 'method': method,
                    'independentSpec': ref(spec_path)})
    assert len({x['testId'] for x in pin}) == expected
    return {'run': data['run'], 'source': data['source'], 'productionCoreMain': data['productionCoreMain'],
            'post': ref(path), 'originalProgram': program.name, 'canonicalReference': ref(original),
            'amendment': ref(amendment), 'cases': pin, 'files': references, 'filesVerified': len(references),
            'archiveItems': sum(x['losslessGzip'] for x in references), 'suiteSelected': expected,
            'currentOnly': True, 'newAcceptance': False, 'noRerun': True}


def main():
    out = [run_evidence(n, scope) for n, scope in RUNS.items()]
    tests = sum(len(r['cases']) for r in out)
    unique = set((r['originalProgram'], x['testId']) for r in out for x in r['cases'])
    assert tests == 69 and len(unique) == 51
    binding = OUT / 'run-program-test-map.json'
    saved(binding, out)
    m = {'actualExit': 0, 'terminalAtUTC': datetime.now(timezone.utc).isoformat(),
         'runs': len(out), 'testExecutionReferences': tests, 'distinctProgramTestIds': len(unique),
         'filesVerified': sum(n['filesVerified'] for n in out), 'archiveItems': sum(n['archiveItems'] for n in out),
         'map': ref(binding), 'newTestsExecuted': 0, 'newAcceptance': 0, 'formalUpdated': False,
         'coverageExecMerged': False, 'nothingInitiallyHeldCompiled': True, 'whole451Accepted': False,
         'firstVerifierCorrection': 'The independent spec declares the OUTCOME ID range rather than enumerating every ID on its own line; match that declared range without replay.'}
    saved(OUT / 'manifest.json', m)
    print(json.dumps({k: m[k] for k in ('runs','testExecutionReferences','distinctProgramTestIds','filesVerified','archiveItems')}))


if __name__ == '__main__':
    main()
