"""Read-only exact current eighteen cached streams with new Test-only host counters; no VM reads."""
import hashlib
import inspect
import json
import os
import shlex
import subprocess
import tarfile
import pg3892_current_two_cohort_native as previous
from pg3274_header_group_full_six import rebase
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require
from lan_server import copy, run

OUT = W / 'pg3938-current-boundary-native-qualified-v1'


def server():
    raw = rebase(previous.server(), 'PG3892', 'PG3938', 3714, 3716)
    raw = raw.replace('PG3734', 'PG3928').replace('qualified3734Tests', 'qualified3928Tests')
    extractor = previous.previous.transport.prior.previous.entry().__globals__['coordinates']
    raw = 'import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\n' + inspect.getsource(extractor) + '\n' + raw
    from pyflakes.api import check
    require(check('ARCHIVE_SHA=""\n' + raw, '<same current Main old18/new host3716>') == 0, 'complete namespace')
    compile(raw, '<same current Main old18/new host3716>', 'exec')
    return raw


def inputs(full, historical, native):
    require(full['actualExit'] == historical['actualExit'] == native['actualExit'] == 0, 'all genuine independent successes')
    q, old, n = full['result'], historical['result'], native['result']
    require(q['productionSource'] == old['productionSource'] == native['productionSource'] == SOURCE, 'all same current Main source')
    require((q['tests'], q['suites'], q['mainClasses'], q['FESFlakyNotRun'], q['staticSixModules']) == (3716, 545, 1643, 0, 0), 'exact fresh whole3716')
    require(q['allPhysicalMainSha256'] == old['allPhysicalMainSha256'] and not q['changedClasses'], 'all1643 actual physical CRC/debug identity; no foreign source credit')
    require(n['currentNativeStreams'] == 18 and n['validatedNativePoints'] == 20 and n['classByteMismatch'] == 0 and n['productionSource'] == SOURCE and not n['oldNativeImported'] and not n['historicalSourceNativeImported'], 'only original eligible same-source20points/18latest')
    original = W / 'pg3892-current-two-cohort-native-v1'
    data = json.loads((original / 'input.safe.json').read_bytes())
    require(data['qualifiedFull'] == old and data['productionSource'] == SOURCE and len(data['selected']) == 20, 'original immutable cohort authority')
    for name, digest in data['files'].items():
        require('/' not in name and name not in {'.', '..'} and hashlib.sha256((original / name).read_bytes()).hexdigest() == digest, 'actual retained input blob unchanged')
    return {**data, 'qualifiedFull': q}, original


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed reader')
    full = json.loads((W / 'pg3930-current-boundary-whole-qualified-v1/manifest.safe.json').read_bytes())
    old = json.loads((W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes())
    native = json.loads((W / 'pg3892-current-two-cohort-native-v1/manifest.safe.json').read_bytes())
    data, original = inputs(full, old, native)
    require(not subprocess.check_output(['git', 'diff', full['result']['sourceSnapshot'], 'HEAD', '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT), 'all qualified Main/Test/settings unchanged')
    os.umask(0o077); OUT.mkdir(mode=0o700)
    input_path = OUT / 'input.safe.json'; input_path.write_text(json.dumps(data, sort_keys=True))
    archive = OUT / 'input.private.tar'
    with tarfile.open(archive, 'x:') as t:
        t.add(input_path, arcname='input.safe.json')
        for name in data['files']:
            t.add(original / name, arcname=name)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    code = 'ARCHIVE_SHA=' + repr(digest) + '\n' + server()
    payload = OUT / 'qualify.private.py'; payload.write_text(code)
    base = '/home/mini/schubert-nk-pgpt'
    status, _ = run(f'test ! -e {base}/runs/PG3938-native-v1 && test ! -e {base}/transfer/PG3938-native-input-v1.tar && test ! -e {base}/transfer/PG3938-qualify.py', timeout=30)
    require(status == 0, 'new-only cached qualification, no overwrite')
    for p, destination in [(archive, base + '/transfer/PG3938-native-input-v1.tar'), (payload, base + '/transfer/PG3938-qualify.py')]:
        status, _ = copy(p, destination, timeout=120); require(status == 0, 'exact private fixed transfer')
    status, output = run('python3 -B ' + shlex.quote(base + '/transfer/PG3938-qualify.py'), timeout=240)
    (OUT / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(code.encode()).hexdigest(),
             'originalCohortReceiptSha256': hashlib.sha256((original / 'manifest.safe.json').read_bytes()).hexdigest(),
             'sourceAndCohortsUnchanged': True, 'newVmOperations': 0, 'formalAccepted': False}
    if status == 0:
        v = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
        value.update(v)
    (OUT / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if status == 0:
        r = value['result']; print(json.dumps({'actualExit': 0, 'currentNativeStreams': r['currentNativeStreams'], 'validatedNativePoints': r['validatedNativePoints'], 'remaining': {k: sum(v[k]['missed'] for v in r['moduleCounters'].values()) for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']}}))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
