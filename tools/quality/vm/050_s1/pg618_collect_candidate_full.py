"""Fresh changed-source six-module host qualification; never imports deployed/old native exec."""
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

T = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def classes(p):
    with zipfile.ZipFile(p) as z:
        return {n: z.read(n) for n in z.namelist() if n.endswith('.class')}


def verify_sessions(rows, start, end, module):
    # Maven child probes can legitimately snapshot one non-reset agent twice.
    # An ID with a different start, duplicate tuple or out-of-run dump is never admitted.
    topology = {'protocol': (1, 1), 'storage': (1, 1), 'bootstrap': (4, 4),
                'api': (5, 4), 'web': (6, 6), 'batch': (1, 1)}
    if module not in topology or type(rows) is not list or not rows:
        raise ValueError('host session topology')
    seen = {}
    for row in rows:
        if type(row) is not dict or set(row) != {'id', 'start', 'dump'}:
            raise ValueError('host session fields')
        if any(type(row[k]) is not str for k in row) or not row['id'] or len(row['id']) > 128:
            raise ValueError('host session data')
        if not all(re.fullmatch('[0-9]{1,19}', row[k]) for k in ('start', 'dump')):
            raise ValueError('host session time')
        begin, dump = int(row['start']), int(row['dump'])
        if not start * 1000 - 1000 <= begin <= dump <= end * 1000 + 1000:
            raise ValueError('host session window')
        if row['id'] in seen:
            prior_start, prior_dump = seen[row['id']]
            if begin != prior_start or dump <= prior_dump:
                raise ValueError('host session continuation')
        seen[row['id']] = (begin, dump)
    if (len(rows), len(seen)) != topology[module]:
        raise ValueError('host session topology')
    return {'dumpRecords': len(rows), 'distinctSessions': len(seen)}


def main(source, selector='PG618'):
    os.umask(0o077)
    assert re.fullmatch('[0-9a-f]{40}', source)
    profiles = {
        'PG618': ('pg618-exporter-candidate-six-host-v1', 'pg617-export-component-v3',
                  '1262c1f28e80ba739388d97d7f5c1d03bb0e71a514013d76435cba19812c47d3',
                  3466, 276, 'BUG-892 typed metadata fixture values; FES0 is not that acceptance'),
        'PG620': ('pg620-typed-oracle-six-host-v1', 'pg619-typed-exporter-component-v1',
                  'c04a2ef7c704a22202f145048b328c7e8a811d0da2600fbd1443b64138d4d04f',
                  3467, 277, None),
        'PG630': ('pg630-retention-factory-six-host-v1', 'pg628-retention-factory-component-v1',
                  'e5ab539ed7e48de9889f6acbe28a8e2f71b3d20a633714ea6b548fc0ca3340b8',
                  3468, 277, None),
    }
    assert selector in profiles
    run_name, selected_name, selected_sha, expected_tests, expected_bootstrap, hold = profiles[selector]
    run = W / run_name
    assert (run/'source').read_text().strip() == source and (run/'exit').read_bytes() == b'0\n'
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=T)
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T).decode().strip()
    entries = [l.split('  ', 1) for l in (run/'source-files.sha256').read_text().splitlines()]
    # Offline recollection binds the immutable run to its original Git source, not newer tools.
    # The runner already enforced before/after clean sourceguard at actual exit0.
    raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=T,
                                 input=''.join(source+':'+p+'\n' for _, p in entries).encode())
    offset = 0
    for expected, path in entries:
        end = raw.index(b'\n', offset)
        header = raw[offset:end].split()
        assert len(header) == 3 and header[1] == b'blob'
        size = int(header[2]); offset = end+1
        assert hashlib.sha256(raw[offset:offset+size]).hexdigest() == expected
        assert raw[offset+size:offset+size+1] == b'\n'
        offset += size+1
    assert offset == len(raw)
    log = (run/'build.private.log').read_text()
    assert log.count('BUILD SUCCESS') == 1 and 'BUILD FAILURE' not in log
    start = datetime.datetime.fromisoformat((run/'started').read_text().strip()).timestamp()
    end = datetime.datetime.fromisoformat((run/'completed').read_text().strip()).timestamp()
    selected = W/selected_name
    assert sha(selected/'manifest.safe.json') == selected_sha
    old = W/('pg620-typed-oracle-six-host-v1'if selector=='PG630'else'pg599-candidate-bootstrap-six-host-v1')
    expected_old = 'e83d2c34652b8c2bea5c1b9c02f00e9b757b88b5de6b1fb45e79b615ec003b57'if selector=='PG630'else'cdd971634fe0f5acabe091db476f25838a55730172d3cc07244180e708f4e47d'
    assert sha(old/'manifest.safe.json') == expected_old
    old_record = json.loads((old/'manifest.safe.json').read_bytes())
    results = {}; total_classes = tests = suites = 0
    for module in MODULES:
        base = run/module; current = T/'src'/('schubert-nk-'+module)/'target'
        name = 'schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'
        actual = classes(base/name)
        assert actual == classes(current/name)
        selected_module = 'batch'if selector=='PG630'else'bootstrap'
        reference = selected/name if module == selected_module else old/module/name
        assert actual == classes(reference) and actual
        if module != selected_module:
            assert sha(old/module/name) == old_record['moduleResults'][module]['jarSha256']
        total_classes += len(actual)
        sums = {k: 0 for k in ('tests', 'failures', 'errors', 'skipped')}; hashes = {}
        reports = sorted((base/'surefire-reports').glob('TEST-*.xml')); assert reports
        for p in reports:
            original = current/'surefire-reports'/p.name
            assert sha(p) == sha(original) and start <= original.stat().st_mtime <= end+1
            root = ET.parse(p).getroot(); cases = root.findall('testcase')
            assert len(cases) == int(root.get('tests')) > 0
            assert all(not any(c.find(k) is not None for k in (
                'failure', 'error', 'skipped', 'flakyFailure', 'flakyError',
                'rerunFailure', 'rerunError')) for c in cases)
            for k in sums:
                sums[k] += int(root.get(k, '0'))
            hashes[p.name] = sha(p)
        assert sum(sums[k] for k in ('failures', 'errors', 'skipped')) == 0
        assert not ET.parse(base/'spotbugsXml.xml').getroot().findall('.//BugInstance')
        assert sha(base/'jacoco.xml') == sha(current/'site/jacoco/jacoco.xml')
        root = ET.parse(base/'jacoco.xml').getroot(); sessions = root.findall('sessioninfo')
        topology = verify_sessions([dict(s.attrib) for s in sessions], start, end, module)
        counts = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))}
                  for c in root.findall('counter')}
        results[module] = {'tests': sums['tests'], 'suites': len(reports), 'FESFlakyNotRun': 0,
                           'staticIssues': 0, 'hostCounters': counts, 'xmlHashes': hashes,
                           'jarSha256': sha(base/name), 'execSha256': sha(base/'jacoco.exec'),
                           'coverageSha256': sha(base/'jacoco.xml'),
                           'staticSha256': sha(base/'spotbugsXml.xml'),
                           'sessions': [s.attrib for s in sessions], 'sessionTopology': topology}
        tests += sums['tests']; suites += len(reports)
    assert tests == expected_tests and suites == 512 and total_classes == 1605
    assert results['bootstrap']['tests'] == expected_bootstrap
    remaining = {k: sum(m['hostCounters'][k]['missed'] for m in results.values())
                 for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')}
    result = {'actualExit': 0, 'run': run.name, 'candidateSource': source,
              'collectorOperator': operator, 'sameFrozenRunRecollection': True,
              'knownOracleHold': hold,
              'installedVmSource': '72fb7440697ee1048a5c0145055dc1cc3c577914'if selector=='PG630'else'23b14a44b10504172e030bbd6625926bf049fb5c',
              'candidateNotDeployed': True, 'sourceQualification': 'FRESH_SIX_HOST_ONLY',
              'tests': tests, 'suites': suites, 'mainClasses': total_classes,
              'allMainBytesEqualSelectedCandidate': True, 'FESFlakyNotRunIndicators': 0,
              'staticModules': 6, 'staticIssues': 0, 'moduleResults': results,
              'remainingHostOnly': remaining, 'oldNativeStreamsNotImported': True,
              'global100': all(v == 0 for v in remaining.values()), 'formalAccepted': False,
              'wholeWbsAccepted': False, 'rawExported': False,
              'started': (run/'started').read_text().strip(),
              'completed': (run/'completed').read_text().strip(), 'elapsedSeconds': end-start,
              'logSha256': sha(run/'build.private.log'),
              'sourceFilesSha256': sha(run/'source-files.sha256'), 'collectorSha256': sha(pathlib.Path(__file__))}
    with (run/'manifest.safe.json').open('x') as f:
        json.dump(result, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'actualExit': 0, 'tests': tests, 'suites': suites, 'staticIssues': 0,
                      'candidateMainClasses': total_classes, 'remainingHostOnly': remaining,
                      'manifestSha256': sha(run/'manifest.safe.json'), 'formalAccepted': False}))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else 'PG618')
