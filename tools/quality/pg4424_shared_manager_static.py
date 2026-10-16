"""Pinned diagnostic with exact current six-module ABI; not F03 acceptance."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import copy, run
import pg3970_current_main_static as previous
from pg4420_shared_manager_full import SOURCE, ROOT, W

MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')


def require(value, why):
    if not value:
        raise ValueError(why)


def current_auxiliary(old, qualified):
    """Keep every third-party byte, replace exactly the six project Jars."""
    from pathlib import PurePosixPath
    modules = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
    require(set(qualified) == set(modules), 'exact six independently qualified module hashes')
    result = {}; seen = set()
    for name, digest in old.items():
        leaf = PurePosixPath(name).name
        hits = [m for m in modules if leaf == 'schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar']
        if hits:
            module = hits[0]
            require(module not in seen, 'one old project Jar per module')
            seen.add(module)
            name = '/home/mini/schubert-nk-pgpt/source-full-PG4420/src/schubert-nk-' + module + '/target/' + leaf
            digest = qualified[module]
        else:
            require(not leaf.startswith('schubert-nk-'), 'unknown project auxiliary refused')
        require(name not in result, 'unique auxiliary paths')
        result[name] = digest
    require(seen == set(modules) and len(result) == len(old), 'all six replaced, all third-party retained')
    return result


def pmd_source():
    raw = previous.pmd_source()
    old = "old=json.loads(old_path.read_bytes());rules="
    new = "old=json.loads(old_path.read_bytes());old['auxJarSha256']=current_auxiliary(old['auxJarSha256'],data['qualifiedJars']);rules="
    require(raw.count(old) == 1, 'one original diagnostic auxiliary binding boundary')
    return raw.replace(old, new, 1)


def prepare(data):
    import hashlib
    import json
    from pathlib import Path
    import shutil
    base = Path('/home/mini/schubert-nk-pgpt'); source = base / 'source-full-PG4420'
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    actual = {str(p.relative_to(source)): sha(p) for p in source.glob('src/*/src/main/java/**/*.java')}
    require(len(actual) == 849 and actual == data['sourceSha256'], 'all current849 source bytes')
    out = base / ('runs/' + data['candidateJob']); out.mkdir()
    candidate = out / 'candidate'; candidate.mkdir()
    for name in actual:
        target = candidate / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source / name, target)
    require({str(p.relative_to(candidate)): sha(p) for p in candidate.glob('src/*/src/main/java/**/*.java')} == actual, 'exact readonly copy')
    receipt = out / 'manifest.safe.json'
    receipt.write_text(json.dumps({'productionSource': data['source'], 'sourceFiles': 849, 'allMainSha256': actual,
                                   'copyOnly': True, 'vmActions': 0}, sort_keys=True))
    data['candidateManifestSha256'] = sha(receipt)


def server_source(data):
    raw = inspect.getsource(previous.server)
    changes = {
        'source-full-PG3966': 'source-full-PG4420',
        'runs/PG3958-literal-candidate-static-v1/manifest.safe.json': 'runs/PG3970-current-main-static-v1/manifest.safe.json',
        'actualRuleCountDeltaFromLiteralCandidate': 'actualRuleCountDeltaFromOld7bb',
        'Original pinned typed auxiliaries for fixed diagnostic; compile-time constants and immutable guard change do not change ABI. Not a new Main build/native/coverage qualification.': 'All six project auxiliaries are exact PG4420 independently qualified current Jars; every pinned third-party auxiliary unchanged. No old ABI equivalence assumption. Not F03/native/coverage acceptance.',
        'PG3952 typed full proof for71 literal files; PG3962/3964 identical independent7-case before/after for CleanupWorkerRequest; whole PG3966 separate.': 'PG4428 original4422 exact payload, all3721 identities,1644 Main and all849 source; SSC295 four logical families/two relocations/one fixed enum; no old native imported.'}
    for old, new in changes.items():
        require(raw.count(old) == 1, 'exact diagnostic template boundary: ' + old)
        raw = raw.replace(old, new, 1)
    marker = "result.pop('wholeTypedBindingEquivalenceRef', None)"
    require(raw.count(marker) == 1, 'one final report boundary')
    raw = raw.replace(marker, marker + "\n    result['auxJarSha256'] = current_auxiliary(old['auxJarSha256'], data['qualifiedJars'])\n    result['sameCurrentSixJarAbi'] = True", 1)
    # previous.server's `old` is the same original PG3422 manifest.
    return '\n'.join([inspect.getsource(require), inspect.getsource(previous.verify_maps), inspect.getsource(current_auxiliary), inspect.getsource(prepare), pmd_source(), raw,
                      'server(' + repr(data) + ')\n'])


def main():
    require(not subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT), 'fixed candidate source')
    qualified = json.loads((W / 'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())
    require(qualified['actualExit'] == 0 and qualified['result']['productionSource'] == SOURCE
            and qualified['result']['tests'] == 3721 and qualified['result']['mainClasses'] == 1644, 'genuine same-source independent full first')
    prior = json.loads((W / 'pg3970-current-main-static-v1/manifest.safe.json').read_bytes())['result']
    data = {'source': SOURCE, 'head': SOURCE, 'candidateJob': 'PG4424-shared-manager-static-input-v1',
            'staticJob': 'PG4424-shared-manager-static-v1', 'includeCheckstyle': False,
            'qualifiedJars': qualified['result']['jarHashes'],
            'originalStaticManifestSha256': hashlib.sha256((W / 'pg3422-candidate-static-v1/manifest.safe.json').read_bytes()).hexdigest(),
            'priorStaticManifestSha256': prior['serverManifestSha256'],
            'sourceSha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw = server_source(data)
    from pyflakes.api import check
    require(check(raw, '<pinned same-ABI static>') == 0, 'all emitted static0')
    compile(raw, '<pinned same-ABI static>', 'exec')
    os.umask(0o077); out = W / 'pg4424-shared-manager-static-v1'; out.mkdir(mode=0o700)
    script = out / 'static.private.py'; script.write_text(raw)
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG4424-shared-manager-static-v1'
    status, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG4424-shared-manager-static-v1 && test ! -e /home/mini/schubert-nk-pgpt/runs/PG4424-shared-manager-static-input-v1 && mkdir -m700 ' + destination, timeout=30)
    require(status == 0, 'new-only static destination, never replay unknown original')
    status, _ = copy(script, destination + '/', timeout=60); require(status == 0, 'exact diagnostic payload transferred')
    status, output = run('python3 -B ' + destination + '/static.private.py', timeout=360)
    (out / 'observer.private.log').write_text(output)
    result = {'actualExit': status, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False, 'vmActions': 0}
    if status == 0:
        result['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    print(json.dumps({k: v for k, v in result.items() if k != 'result'}))
    if status == 0:
        print(json.dumps({k: result['result'][k] for k in ['pmd', 'checkstyle', 'actualRuleCountDeltaFromOld7bb', 'serverManifestSha256']}))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
