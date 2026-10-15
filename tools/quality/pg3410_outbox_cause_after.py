"""Same independent eight graphs against the genuinely related-tested candidate API Jar."""
import base64
import hashlib
import inspect
import json
import os
from pathlib import Path

from lan_server import run

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
CANARY = ROOT / 'tools/quality/static/canaries/OutboxCauseGraphCanary.java'


def server(data):
    import base64
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E
    import zipfile

    os.umask(0o077)
    base = Path('/home/mini/schubert-nk-pgpt')
    source = base / 'source-PG3408-related-v1'
    output = base / 'runs/PG3410-outbox-cause-after-v1'; output.mkdir()
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    original = base / 'runs/PG3409-related-qualified-v1/manifest.safe.json'
    assert sha(original) == data['relatedManifestSha256']
    related = json.loads(original.read_bytes())
    assert related['actualExit'] == related['mavenExit'] == 0 and related['tests'] == 60
    assert related['candidateSource'] == data['candidateSource']
    jars = [source / ('src/schubert-nk-' + m + '/target/schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar')
            for m in related['modules']]
    for module, jar in zip(related['modules'], jars, strict=True):
        assert sha(jar) == related['modules'][module]['jarSha256']
    xml = source / 'src/schubert-nk-api/target/surefire-reports/TEST-dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest.xml'
    properties = {p.get('name'): p.get('value') for p in E.parse(xml).findall('./properties/property')}
    cwd = Path(properties['user.dir']); assert cwd == source / 'src/schubert-nk-api'
    dependencies = []
    for item in properties['surefire.test.class.path'].split(':'):
        p = Path(item) if Path(item).is_absolute() else cwd / item
        p = p.resolve(strict=True)
        if p.suffix == '.jar' and p.is_relative_to(base / 'm2/repository'):
            dependencies.append(p)
        else:
            assert p.is_relative_to(source)
    cp = ':'.join(map(str, [*jars, *dependencies]))
    helper = output / 'OutboxCauseGraphCanary.java'
    helper.write_bytes(base64.b64decode(data['canaryBase64'], validate=True))
    assert sha(helper) == data['beforeCanarySha256']
    classes = output / 'classes'; classes.mkdir()
    java = base / 'tools/jdk-25.0.4/bin'
    compile_argv = [str(java / 'javac'), '--release', '25', '-Xlint:all', '-Werror', '-cp', cp,
                    '-d', str(classes), str(helper)]
    compiled = subprocess.run(compile_argv, capture_output=True, timeout=60)
    (output / 'compile.private.log').write_bytes(compiled.stdout + compiled.stderr)
    assert compiled.returncode == 0
    expected = {'acyclic': False, 'direct': True, 'cause-cycle': False, 'mixed-cycle': False,
                'alternate-edge': True, 'reachable-through-cycle': True,
                'suppressed-only': False, 'message-only': False}
    results = []
    for case, value in expected.items():
        # subprocess.run reaps only its own fork even on the bounded timeout failure.
        actual = subprocess.run([str(java / 'java'), '-cp', str(classes) + ':' + cp,
                                 'dev.codex.schubert.nk.api.messaging.outbound.OutboxCauseGraphCanary', case],
                                capture_output=True, timeout=5)
        assert actual.returncode == 0 and actual.stderr == b''
        assert actual.stdout.decode().splitlines() == ['ENTER ' + case, 'RESULT ' + str(value).lower()]
        results.append({'case': case, 'expected': value, 'actual': value, 'exit': 0,
                        'ownedChildReaped': True, 'stdoutSha256': hashlib.sha256(actual.stdout).hexdigest()})
    api = source / 'src/schubert-nk-api/target/schubert-nk-api-0.1.0-SNAPSHOT.jar'
    with zipfile.ZipFile(api) as jar:
        class_sha = hashlib.sha256(jar.read('dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.class')).hexdigest()
    assert class_sha != data['beforeApiClassSha256']
    assert sha(original) == data['relatedManifestSha256']
    for module, jar in zip(related['modules'], jars, strict=True):
        assert sha(jar) == related['modules'][module]['jarSha256']
    result = {'actualExit': 0, 'run': 'PG3410-outbox-cause-after-v1', 'candidateSource': data['candidateSource'],
              'tests': 8, 'newJUnitCredit': 0, 'cases': results, 'compileExit': compiled.returncode,
              'sourceSnapshot': related['sourceSnapshot'], 'relatedManifestSha256': sha(original),
              'beforePublicManifestSha256': data['beforeManifestSha256'], 'sameCanarySha256': sha(helper),
              'beforeApiClassSha256': data['beforeApiClassSha256'], 'afterApiClassSha256': class_sha,
              'afterApiJarSha256': sha(api), 'javaVersion': properties['java.version'],
              'os': properties['os.name'] + ' ' + properties['os.version'],
              'compileLogSha256': sha(output / 'compile.private.log'), 'vmActions': 0,
              'oldNativeImported': False, 'formalUpdated': False}
    (output / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    print(json.dumps(result))


def main():
    related = json.loads((W / 'pg3409-related-qualified-v1/manifest.safe.json').read_bytes())
    before_path = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3404-outbox-cause-before/manifest.json'
    before = json.loads(before_path.read_bytes())
    assert related['actualExit'] == before['actualExit'] == 0
    data = {'candidateSource': related['result']['candidateSource'],
            'relatedManifestSha256': related['result']['serverManifestSha256'],
            'beforeManifestSha256': hashlib.sha256(before_path.read_bytes()).hexdigest(),
            'beforeApiClassSha256': before['originalClassSha256'],
            'beforeCanarySha256': before['canarySourceSha256'],
            'canaryBase64': base64.b64encode(CANARY.read_bytes()).decode()}
    assert hashlib.sha256(CANARY.read_bytes()).hexdigest() == data['beforeCanarySha256']
    os.umask(0o077); out = W / 'pg3410-outbox-cause-after-v1'; out.mkdir()
    payload = inspect.getsource(server) + '\nserver(' + repr(data) + ')\n'
    (out / 'after.private.py').write_text(payload)
    rc, text = run("python3 -B - <<'AFTER'\n" + payload + '\nAFTER', timeout=120)
    (out / 'observer.private.log').write_text(text)
    assert rc == 0, 'after not qualified; preserve slot'
    result = json.loads(text.strip())
    public = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3410-outbox-cause-after'
    public.mkdir()
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    path = public / 'manifest.json'; path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actualExit': 0, 'sameCases': 8, 'nonReturning': 0, 'mismatches': 0,
                      'candidateSource': result['candidateSource'], 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
