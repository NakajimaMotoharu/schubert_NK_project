"""Fixed analyzers on frozen seven-bb Main; no whole replay, VM or source mutation."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import copy, run
from pg3958_literal_candidate_static import pmd_source
from pg3966_literal_invariant_full_six import ROOT, W, SOURCE, require


def verify_maps(expected, actual):
    require(len(expected) == 849 and expected == actual, 'exact complete current849 Main bytes')


def prepare(data):
    import hashlib
    import json
    from pathlib import Path
    import shutil
    b = Path('/home/mini/schubert-nk-pgpt')
    source = b / 'source-full-PG3966'
    files = sorted(source.glob('src/*/src/main/java/**/*.java'))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    verify_maps(data['sourceSha256'], {str(p.relative_to(source)): sha(p) for p in files})
    out = b / ('runs/' + data['candidateJob']); out.mkdir()
    candidate = out / 'candidate'; candidate.mkdir()
    for p in files:
        target = candidate / p.relative_to(source); target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target)
    verify_maps(data['sourceSha256'], {str(p.relative_to(candidate)): sha(p) for p in candidate.glob('src/*/src/main/java/**/*.java')})
    receipt = out / 'manifest.safe.json'
    receipt.write_text(json.dumps({'productionSource': data['source'], 'sourceSnapshot': data['head'], 'sourceFiles': 849,
                                   'allMainSha256': data['sourceSha256'], 'copyOnly': True, 'vmActions': 0}, sort_keys=True))
    data['candidateManifestSha256'] = sha(receipt)


def server(data):
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E
    prepare(data)
    result = pmd(data)
    b = Path('/home/mini/schubert-nk-pgpt'); out = b / ('runs/' + data['staticJob'])
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    fixed = json.loads((b / 'runs/PG3382-static-gate-v1/result/manifest.safe.json').read_bytes())
    old = json.loads((b / 'runs/PG3422-candidate-static-v1/manifest.safe.json').read_bytes())
    rules = b / 'runs/PG3382-static-gate-v1/result/source/tools/quality/static'
    jar = b / 'runs/PG3382-static-gate-v1/checkstyle-14.3.0-all.jar'
    require(sha(rules / 'checkstyle.xml') == old['ruleSha256']['checkstyle.xml'] and sha(jar) == old['pinnedToolSha256']['checkstyle-14.3.0-all.jar'], 'same fixed Checkstyle/rules')
    argv = list(fixed['checkstyle']['argv']); argv[argv.index('-c') + 1] = str(rules / 'checkstyle.xml')
    argv[argv.index('-o') + 1] = str(out / 'checkstyle.xml'); argv[-1] = '@' + str(out / 'all-java.txt')
    checked = subprocess.run(argv, capture_output=True, timeout=90)
    (out / 'checkstyle.private.log').write_bytes(checked.stdout + checked.stderr)
    errors = E.parse(out / 'checkstyle.xml').getroot().findall('.//error')
    require(checked.returncode == len(errors) % 256, 'actual Checkstyle status and XML agree')
    candidate = b / ('runs/' + data['candidateJob'] + '/candidate')
    source = b / 'source-full-PG3966'
    for root in [candidate, source]:
        verify_maps(data['sourceSha256'], {str(p.relative_to(root)): sha(p) for p in root.glob('src/*/src/main/java/**/*.java')})
    prior = b / 'runs/PG3958-literal-candidate-static-v1/manifest.safe.json'
    require(sha(prior) == data['priorStaticManifestSha256'], 'original isolated literal diagnostic')
    before = json.loads(prior.read_bytes())['pmd']
    counts = result['pmd']['ruleCounts']; old_counts = before['ruleCounts']
    delta = {k: counts.get(k, 0) - old_counts.get(k, 0) for k in set(counts) | set(old_counts) if counts.get(k, 0) != old_counts.get(k, 0)}
    result.pop('wholeTypedBindingEquivalenceRef', None)
    result.update(checkstyle={'actualExit': checked.returncode, 'findings': len(errors), 'reportSha256': sha(out / 'checkstyle.xml')},
                  allMainSha256=data['sourceSha256'], mainGitSource=data['source'], all849AppliedSourceExact=True,
                  actualRuleCountDeltaFromLiteralCandidate=delta, priorStaticManifestSha256=sha(prior),
                  auxMeaning='Original pinned typed auxiliaries for fixed diagnostic; compile-time constants and immutable guard change do not change ABI. Not a new Main build/native/coverage qualification.',
                  semanticEvidence='PG3952 typed full proof for71 literal files; PG3962/3964 identical independent7-case before/after for CleanupWorkerRequest; whole PG3966 separate.',
                  F03Accepted=False, formalAccepted=False, staticGatePassed=not counts and not errors,
                  endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True))
    result['serverManifestSha256'] = sha(out / 'manifest.safe.json'); print(json.dumps(result))


def payload(data):
    return '\n'.join([inspect.getsource(require), inspect.getsource(verify_maps), inspect.getsource(prepare), pmd_source(), inspect.getsource(server), 'server(' + repr(data) + ')\n'])


def main():
    require(not subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=ROOT), 'frozen final Main and Tests unchanged')
    full = json.loads((W / 'pg3966-server-six-v1/begin.safe.json').read_bytes())
    require(full['productionSource'] == SOURCE and full['expectedTests'] == 3717, 'existing frozen campaign, not a new whole')
    prior = json.loads((W / 'pg3958-literal-candidate-static-v1/manifest.safe.json').read_bytes())['result']
    data = {'source': SOURCE, 'head': full['snapshot'], 'candidateJob': 'PG3970-current-main-static-input-v1', 'staticJob': 'PG3970-current-main-static-v1',
            'includeCheckstyle': False, 'originalStaticManifestSha256': hashlib.sha256((W / 'pg3422-candidate-static-v1/manifest.safe.json').read_bytes()).hexdigest(),
            'priorStaticManifestSha256': prior['serverManifestSha256'],
            'sourceSha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    verify_maps(data['sourceSha256'], data['sourceSha256'])
    os.umask(0o077); out = W / 'pg3970-current-main-static-v1'; out.mkdir()
    script = out / 'static.private.py'; script.write_text(payload(data)); compile(script.read_text(), '<fixed current Main diagnostic>', 'exec')
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG3970-current-main-static-v1'
    status, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3970-current-main-static-v1 && test ! -e /home/mini/schubert-nk-pgpt/runs/PG3970-current-main-static-input-v1 && mkdir -m700 ' + destination, timeout=30)
    require(status == 0, 'new-only static destination')
    status, _ = copy(script, destination + '/', timeout=60); require(status == 0, 'fixed diagnostic payload transferred')
    status, output = run('python3 -B ' + destination + '/static.private.py', timeout=360); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'formalAccepted': False, 'vmActions': 0}
    if status == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if status == 0:
        result = value['result']; print(json.dumps({k: result[k] for k in ['pmd', 'checkstyle', 'actualRuleCountDeltaFromLiteralCandidate', 'serverManifestSha256', 'F03Accepted']}))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
