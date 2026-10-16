"""Unchanged pinned PMD/Checkstyle on proven private-constant candidate; no apply or runtime action."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import run, copy
import pg3696_hygiene_pmd_diagnosis as previous
from pg3928_current_boundary_full_six import ROOT, W, SOURCE, require


def pmd_source():
    raw = inspect.getsource(previous.server)
    end = "(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(value))"
    require(raw.count(end) == 1, 'exact final receipt boundary; no intermediate success manifest')
    raw = raw.replace('def server(data):', 'def pmd(data):', 1).replace(end, 'return value')
    compile(raw, '<same pinned PMD phase no premature success>', 'exec')
    return raw


def server(data):
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E
    result = pmd(data)
    b = Path('/home/mini/schubert-nk-pgpt'); out = b / 'runs/PG3958-literal-candidate-static-v1'; sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    candidate = b / 'runs/PG3952-literal-candidate-v1/candidate'; proof = json.loads((candidate.parent / 'manifest.safe.json').read_bytes())
    require(proof['actualExit'] == 0 and proof['sourceFiles'] == 849 and proof['proposedConstants'] == proof['requestedFindings'] == 187
            and proof['changedFiles'] == 71 and not proof['held'] and proof['allValuesTypedBindingsFullAstAndPublicAbiIdentical'] is True
            and proof['privateCompileTimeStringFieldsOnly'] is True and proof['generated70Unchanged'] is True
            and len(proof['modules']) == 6 and all(m['actualExit'] == 0 for m in proof['modules'].values()), 'complete exact six-module string/value/ABI proof')
    baseline = b / 'runs/PG3730-octal-candidate-static-v1/manifest.safe.json'; require(sha(baseline) == data['baseStaticManifestSha256'], 'original current1840 static authority')
    base = json.loads(baseline.read_bytes()); require(base['pmd']['rawFindings'] == 1840 and base['checkstyle']['findings'] == 0, 'actual current complete static baseline')
    delta = {k: result['pmd']['ruleCounts'].get(k, 0) - base['pmd']['ruleCounts'].get(k, 0) for k in set(result['pmd']['ruleCounts']) | set(base['pmd']['ruleCounts']) if result['pmd']['ruleCounts'].get(k, 0) != base['pmd']['ruleCounts'].get(k, 0)}
    require(delta == {'AvoidDuplicateLiterals': -187} and result['pmd']['rawFindings'] == 1653 and result['pmd']['processingErrors'] == 0, 'actual all187 reduction, every other rule count unchanged')
    fixed = json.loads((b / 'runs/PG3382-static-gate-v1/result/manifest.safe.json').read_bytes()); old = json.loads((b / 'runs/PG3422-candidate-static-v1/manifest.safe.json').read_bytes())
    rules = b / 'runs/PG3382-static-gate-v1/result/source/tools/quality/static'; jar = b / 'runs/PG3382-static-gate-v1/checkstyle-14.3.0-all.jar'
    require(sha(rules / 'checkstyle.xml') == old['ruleSha256']['checkstyle.xml'] and sha(jar) == old['pinnedToolSha256']['checkstyle-14.3.0-all.jar'], 'same pinned Checkstyle/rules')
    args = list(fixed['checkstyle']['argv']); args[args.index('-c') + 1] = str(rules / 'checkstyle.xml'); args[args.index('-o') + 1] = str(out / 'checkstyle.xml'); args[-1] = '@' + str(out / 'all-java.txt')
    checked = subprocess.run(args, capture_output=True, timeout=90); (out / 'checkstyle.private.log').write_bytes(checked.stdout + checked.stderr)
    findings = E.parse(out / 'checkstyle.xml').getroot().findall('.//error'); require(checked.returncode == 0 and not findings, 'unchanged fixed Checkstyle all0')
    files = {str(p.relative_to(candidate)): sha(p) for p in candidate.glob('src/*/src/main/java/**/*.java')}; require(files == data['sourceSha256'], 'all849 candidate bytes unchanged through both analyzers')
    result.update(checkstyle={'actualExit': 0, 'findings': 0, 'reportSha256': sha(out / 'checkstyle.xml')}, all849AppliedSourceExact=False,
                  all849IsolatedCandidateExact=True, mainApplied=False, wholeTypedBindingEquivalenceRef='PG3952 all6 full normalized tree/type/bindings/values/public ABI; private constant fields only',
                  literalDelta={'actualRawReduction': 187, 'ruleCountDeltaFromBase': delta, 'allSourceSha256': files, 'candidateManifestSha256': sha(candidate.parent / 'manifest.safe.json')},
                  auxMeaning='Original fixed typed auxiliaries for API-equivalent source diagnostic only; NOT a new Main build/native/coverage acceptance', F03Accepted=False, formalAccepted=False,
                  endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    result.pop('productionCandidateSource', None)
    result.update(baseProductionSource=data['source'], candidateGitSource=None, candidateSourceMeaning='Isolated uncommitted all849 byte map in literalDelta; baseProductionSource is not the modified candidate identity')
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True)); result['serverManifestSha256'] = sha(out / 'manifest.safe.json'); print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed static operator')
    candidate = json.loads((W / 'pg3952-literal-candidate-v1/manifest.safe.json').read_bytes()); require(candidate['actualExit'] == 0, 'actual all6 candidate proof first')
    base = json.loads((W / 'pg3730-octal-candidate-static-v1/manifest.safe.json').read_bytes())['result']
    original = W / 'pg3422-candidate-static-v1/manifest.safe.json'
    data = {'source': SOURCE, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'candidateJob': 'PG3952-literal-candidate-v1',
            'staticJob': 'PG3958-literal-candidate-static-v1', 'includeCheckstyle': False, 'candidateManifestSha256': candidate['result']['serverManifestSha256'],
            'originalStaticManifestSha256': hashlib.sha256(original.read_bytes()).hexdigest(), 'baseStaticManifestSha256': base['serverManifestSha256'], 'sourceSha256': candidate['result']['allCandidateSourceSha256']}
    os.umask(0o077); out = W / 'pg3958-literal-candidate-static-v1'; out.mkdir()
    script = out / 'static.private.py'; script.write_text('INPUT=' + repr(data) + '\n' + inspect.getsource(require) + '\n' + pmd_source() + '\n' + inspect.getsource(server) + '\nserver(INPUT)\n')
    compile(script.read_text(), '<fixed unchanged candidate analyzers>', 'exec')
    destination = '/home/mini/schubert-nk-pgpt/transfer/PG3958-literal-candidate-static-v1'
    status, _ = run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3958-literal-candidate-static-v1 && mkdir -m700 ' + destination, timeout=30); require(status == 0, 'new-only fixed analysis')
    status, _ = copy(script, destination + '/', timeout=60); require(status == 0, 'fixed static-only source')
    status, output = run('python3 -B ' + destination + '/static.private.py', timeout=360); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'baseProductionSource': SOURCE, 'payloadSha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'MainApplied': False, 'F03Accepted': False}
    if status == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps({k: v for k, v in value.items() if k != 'result'}))
    if status == 0:
        r = value['result']; print(json.dumps({'pmd': r['pmd'], 'checkstyle': r['checkstyle'], 'literalDelta': {k: r['literalDelta'][k] for k in ['actualRawReduction', 'ruleCountDeltaFromBase']}, 'serverManifestSha256': r['serverManifestSha256']}))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
