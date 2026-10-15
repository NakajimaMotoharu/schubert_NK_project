"""Finite isolated original-a9 reproduction; never starts Broker/DB/VM or whole tests."""
import base64
import hashlib
import inspect
import json
import os
from pathlib import Path

import lan_server

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg3404-outbox-cause-before-v2')
PUBLIC = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3404-outbox-cause-before'
SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
CANARY = ROOT / 'tools/quality/static/canaries/OutboxCauseGraphCanary.java'


def server(encoded):
    import base64
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import time
    import xml.etree.ElementTree as E
    import zipfile

    os.umask(0o077)
    p = Path('/home/mini/schubert-nk-pgpt/runs/PG3404-outbox-cause-before-v2')
    p.mkdir()
    original = p.parent / 'PG3372-six-v1'
    whole = json.loads((original / 'manifest.safe.json').read_bytes())
    assert whole['actualExit'] == whole['mavenExit'] == 0 and whole['tests'] == 3706
    xml = original / 'api/surefire-reports/TEST-dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest.xml'
    properties = {a.get('name'): a.get('value') for a in E.parse(xml).findall('./properties/property')}
    cwd = Path(properties['user.dir'])
    assert cwd.is_dir() and cwd.name == 'schubert-nk-api'
    jars = [next((original / name).glob('schubert-nk-*.jar')).resolve()
            for name in ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch']]
    dependencies = []
    for entry in properties['surefire.test.class.path'].split(':'):
        candidate = Path(entry) if Path(entry).is_absolute() else cwd / entry
        if candidate.suffix == '.jar':
            candidate = candidate.resolve(strict=True)
            if candidate.is_relative_to('/home/mini/schubert-nk-pgpt/m2/repository'):
                dependencies.append(candidate)
            else:
                # Original reactor jars are replaced by the immutable run copies.
                assert candidate.is_relative_to('/home/mini/schubert-nk-pgpt/source-full-PG3372/src')
                assert candidate.parent.name == 'target'
                assert candidate.name in {v.name for v in jars} | {'schubert-nk-bootstrap-0.1.0-SNAPSHOT-tests.jar'}
                if not candidate.name.endswith('-tests.jar'):
                    fixed = next(v for v in jars if v.name == candidate.name)
                    assert hashlib.sha256(candidate.read_bytes()).digest() == hashlib.sha256(fixed.read_bytes()).digest()
    classpath = ':'.join(str(v) for v in [*jars, *dependencies])
    java = Path('/home/mini/schubert-nk-pgpt/tools/jdk-25.0.4/bin')
    source = p / 'OutboxCauseGraphCanary.java'
    source.write_bytes(base64.b64decode(encoded, validate=True))
    classes = p / 'classes'; classes.mkdir()
    compile_argv = [str(java / 'javac'), '--release', '25', '-Xlint:all', '-Werror',
                    '-cp', classpath, '-d', str(classes), str(source)]
    compiled = subprocess.run(compile_argv, capture_output=True, timeout=60)
    (p / 'compile.private.log').write_bytes(compiled.stdout + compiled.stderr)
    assert compiled.returncode == 0, 'isolated Java25 strict compile failed'
    cases = {'acyclic': False, 'direct': True, 'cause-cycle': False,
             'mixed-cycle': False, 'alternate-edge': True, 'reachable-through-cycle': True,
             'suppressed-only': False, 'message-only': False}
    results = []
    for name, expected in cases.items():
        argv = [str(java / 'java'), '-cp', str(classes) + ':' + classpath,
                'dev.codex.schubert.nk.api.messaging.outbound.OutboxCauseGraphCanary', name]
        start = time.monotonic()
        child = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        timed_out = False
        try:
            out, err = child.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            timed_out = True
            child.terminate()
            try:
                out, err = child.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill(); child.communicate(timeout=5)
                raise AssertionError('owned child failed ordinary TERM') from None
        lines = out.decode().splitlines()
        assert lines[0] == 'ENTER ' + name and err == b'', 'actual method entry/clean stderr required'
        actual = None if timed_out else lines[1] == 'RESULT true'
        if not timed_out:
            assert child.returncode == 0 and len(lines) == 2 and lines[1] in ['RESULT true', 'RESULT false']
        else:
            assert child.returncode == 143 and len(lines) == 1
        results.append({'case': name, 'expected': expected, 'actual': actual,
                        'timedOut': timed_out, 'exit': child.returncode,
                        'ownedChildReaped': child.poll() is not None,
                        'seconds': time.monotonic() - start,
                        'stdoutSha256': hashlib.sha256(out).hexdigest()})
    assert [r['case'] for r in results if r['timedOut']] == ['cause-cycle', 'mixed-cycle', 'reachable-through-cycle']
    assert [r['case'] for r in results if not r['timedOut'] and r['actual'] != r['expected']] == ['alternate-edge']
    assert all(r['ownedChildReaped'] for r in results)
    with zipfile.ZipFile(jars[3]) as jar:
        original_class = jar.read('dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.class')
    result = {'run': 'PG3404-outbox-cause-before-v2', 'actualExit': 0,
              'interpretation': 'DEFECT_REPRODUCED_NOT_PRODUCTION_PASS', 'productionSource': 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',
              'testId': 'PT-OPS-CAUSE3404-001', 'bug': 'BUG1299', 'ykt': 'YKT1065',
              'originalWholeManifestSha256': hashlib.sha256((original / 'manifest.safe.json').read_bytes()).hexdigest(),
              'originalApiJarSha256': hashlib.sha256(jars[3].read_bytes()).hexdigest(),
              'originalClassSha256': hashlib.sha256(original_class).hexdigest(),
              'canarySourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'compileExit': compiled.returncode, 'cases': results, 'newProductionPtCredit': 0,
              'vmActions': 0, 'brokerActions': 0, 'dbActions': 0, 'formalUpdated': False}
    (p / 'manifest.safe.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


def main():
    os.umask(0o077)
    PRIVATE.mkdir()
    encoded = base64.b64encode(CANARY.read_bytes()).decode()
    payload = inspect.getsource(server) + '\nserver(' + repr(encoded) + ')\n'
    (PRIVATE / 'server.private.py').write_text(payload)
    rc, out = lan_server.run("python3 - <<'REMOTE'\n" + payload + '\nREMOTE', timeout=90)
    (PRIVATE / 'observer.private.log').write_text(out)
    assert rc == 0, 'original finite canary failed; preserve slot, do not replay'
    result = json.loads(out.strip())
    assert result['canarySourceSha256'] == hashlib.sha256(CANARY.read_bytes()).hexdigest()
    PUBLIC.mkdir()
    (PRIVATE / 'manifest.safe.json').write_text(json.dumps(result, indent=2) + '\n')
    (PUBLIC / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'cases': len(result['cases']), 'nonReturning': 3,
                      'missedAlternateDuplicate': 1, 'ownedChildrenReaped': 8,
                      'productionPass': False, 'manifestSha256': hashlib.sha256((PUBLIC / 'manifest.json').read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
