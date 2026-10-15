"""One necessary changed-Main whole3712/545; candidate independent of deployed a9/native28."""
import argparse
import ast
import hashlib
import inspect
import json
import os
import subprocess

from lan_server import run
import pg2798_jdbc_null_fixed_full_six as base
import pg3398_retain_owner_integration as previous
from pg3274_header_group_full_six import rebase
from pg3408_outbox_cause_related import CHANGED, ROOT, W, MAIN
from pg3409_related_qualification import positions, verify_switch_debug, require, classify

SOURCE = '4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
EXPECTED = {'protocol': (86, 17, 174), 'storage': (163, 23, 74), 'bootstrap': (298, 40, 105),
            'api': (973, 160, 407), 'web': (889, 131, 315), 'batch': (1303, 174, 568)}
NEW_CASES = [
    ('dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest', 'cause3404TypedGraphTerminatesCyclesAndVisitsBothProviderEdges'),
    ('dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest', 'cause3404UnconfirmedCommitAlwaysRollsBackClosesAndPreservesOriginalGraph'),
    ('dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest', 'cause3404ReachableTypedDuplicateConfirmsOnlyAfterRollbackAndStillCloses'),
    ('dev.codex.schubert.nk.api.security.AuthenticationFailureGraphTest', 'suppressedCyclesTerminateAndReachableFatalRetainsIdentity'),
    ('dev.codex.schubert.nk.web.session.SessionFailureGraphTest', 'mixedCauseAndSuppressedCyclesTerminateAndReachableFatalRetainsIdentity')]


def validate(snapshot):
    full = json.loads((W / 'pg3400-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())['result']
    changed = set(subprocess.check_output(['git', 'diff', '--name-only', full['sourceSnapshot'], snapshot,
                                         '--', *base.SCOPE], cwd=ROOT, text=True).splitlines())
    require(changed == CHANGED, 'exact registered one Main source and three Test files')
    require(not subprocess.check_output(['git', 'diff', SOURCE, snapshot, '--', *base.SCOPE], cwd=ROOT), 'actual candidate all Main/Test/settings fixed')
    related = json.loads((W / 'pg3409-related-qualified-v1/manifest.safe.json').read_bytes())
    after = json.loads((W / 'pg3410-outbox-cause-after-v1/manifest.safe.json').read_bytes())
    require(related['actualExit'] == related['result']['actualExit'] == after['actualExit'] == 0
            and related['result']['candidateSource'] == after['candidateSource'] == SOURCE
            and related['result']['tests'] == 60 and len(after['cases']) == 8, 'genuine related60/same-eight after')
    require(all(c['expected'] == c['actual'] and c['exit'] == 0 for c in after['cases']), 'all after graphs finite/correct')
    require(subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', MAIN], cwd=ROOT, text=True).strip() == SOURCE, 'exact current Main source identity')


def server_source(head, digest):
    raw = rebase(previous.server_source(head, digest), 'PG3398', 'PG3412', 3707, 3712,
                 {previous.SOURCE: SOURCE})
    tree = ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 543:
            node.value = 545
    return ast.unparse(ast.fix_missing_locations(tree))


def whole():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(); validate(head)
    engine = base.prior.transport_base.previous.previous.previous.previous.transport
    raw = inspect.getsource(engine.main)
    for old, new in [('PG1528', 'PG3412'), ('pg1528', 'pg3412'), ('3582', '3712'), ('524', '545'), ('1637', '1643')]:
        raw = raw.replace(old, new)
    raw = raw.replace('3578/523/1635 + LinuxFilesystemClassifier4 tests/one suite/two Main classes, other tests retained',
                      '3707 retained plus API graph3/Auth1/Session1;545 suites1643Main; one semantic and one generated debug class')
    raw = raw.replace('SSC269 new production storage/batch dependency and required all-source regression; selected attempts failed before target tests, literal NoTests gates preserved',
                      'BUG1299 genuine before/after and related60 with changed API Main require one fresh whole; deployed a9/native not candidate credit')
    namespace = {**engine.__dict__, 'PRODUCTION': SOURCE, 'server_source': server_source}
    exec(compile(raw, '<necessary one candidate3712 whole>', 'exec'), namespace)
    return namespace['main']()


def independent(data):
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import xml.etree.ElementTree as E
    import zipfile

    b = Path('/home/mini/schubert-nk-pgpt'); out = b / 'runs/PG3412-six-v1'; source = b / 'source-full-PG3412'
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    v = json.loads((out / 'manifest.safe.json').read_bytes()); begin = json.loads((out / 'begin.safe.json').read_bytes())
    require(v['actualExit'] == v['mavenExit'] == 0 and not v['issues'] and v['sourceInputsUnchanged'], 'actual whole terminal0')
    require(v['productionSource'] == begin['productionSource'] == data['candidateSource'], 'candidate identity')
    require(v['sourceSnapshotHead'] == begin['sourceSnapshotHead'], 'same original snapshot')
    require(sha(b / 'transfer/PG3412-source.tar') == begin['sourceArchiveSha256'], 'fixed actual archive')
    require(all(sha(source / p) == h for p, h in begin['inputs'].items()), 'every original source unchanged')
    modules = {}; coverage = {}; jar_hashes = {}; all_cases = set(); changed = []; old_cases = set()
    old_manifest = b / 'runs/PG3398-six-v1/manifest.safe.json'
    require(sha(old_manifest) == data['priorManifestSha256'], 'actual immutable original3707 identity authority')
    for module, (nt, ns, nc) in data['expected'].items():
        target = source / ('src/schubert-nk-' + module + '/target')
        xmls = sorted((target / 'surefire-reports').glob('TEST-*.xml'))
        roots = [E.parse(p).getroot() for p in xmls]
        require(len(xmls) == ns and sum(len(r.findall('testcase')) for r in roots) == nt, 'exact independent module cardinality')
        expected_cases = {r.get('name'): len(r.findall('testcase')) for r in roots}
        cases = classify(roots, expected_cases); all_cases.update(cases)
        old_roots = [E.parse(p).getroot() for p in (b / 'runs/PG3398-six-v1' / module / 'surefire-reports').glob('TEST-*.xml')]
        old_cases.update(classify(old_roots, {r.get('name'): len(r.findall('testcase')) for r in old_roots}))
        start = datetime.datetime.fromisoformat(begin['startUTC']).timestamp()
        require(all(p.stat().st_mtime >= start and sha(p) == sha(out / module / 'surefire-reports' / p.name) for p in xmls), 'fresh original/saved XML bytes')
        static = target / 'spotbugsXml.xml'; require(not E.parse(static).findall('.//BugInstance'), 'static0')
        jar = target / ('schubert-nk-' + module + '-0.1.0-SNAPSHOT.jar')
        old = b / 'runs/PG3398-six-v1' / module / jar.name
        require(sha(old) == data['priorJarHashes'][module], 'baseline a9 original Jar')
        images = []
        for path in [old, jar]:
            with zipfile.ZipFile(path) as z:
                require(len(z.namelist()) == len(set(z.namelist())), 'unique full Jar members')
                images.append({n: z.read(n) for n in z.namelist()})
        require(images[0].keys() == images[1].keys(), 'whole physical inventory')
        delta = sorted(n for n in images[0] if images[0][n] != images[1][n])
        expected_delta = ['dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender$1.class',
                          'dev/codex/schubert/nk/api/messaging/outbound/OutboxJmsSender.class'] if module == 'api' else []
        require(delta == expected_delta, 'only registered semantic/debug family changes')
        if module == 'api':
            debug = verify_switch_debug(images[0][delta[0]], images[1][delta[0]])
        require(sum(n.endswith('.class') for n in images[1]) == nc, 'module Main cardinality')
        changed.extend(module + ':' + n for n in delta)
        modules[module] = {'tests': nt, 'suites': ns, 'mainClasses': nc,
                           'xmlHashes': {p.name: sha(p) for p in xmls}, 'staticSha256': sha(static)}
        cov = target / 'site/jacoco/jacoco.xml'
        coverage[module] = {c.get('type'): {'missed': int(c.get('missed')), 'covered': int(c.get('covered'))}
                            for c in E.parse(cov).getroot().findall('counter')}
        modules[module]['coverageXmlSha256'] = sha(cov); jar_hashes[module] = sha(jar)
    require(len(all_cases) == 3712 and sum(m['suites'] for m in modules.values()) == 545, 'genuine full3712/545')
    added_cases = {tuple(v) for v in data['newCases']}
    require(len(old_cases) == 3707 and len(added_cases) == 5 and not (old_cases & added_cases)
            and all_cases == old_cases | added_cases, 'all3707 original actual identities retained plus exactly five declared regressions')
    print(json.dumps({'actualExit': 0, 'productionSource': data['candidateSource'], 'sourceSnapshot': begin['sourceSnapshotHead'],
                      'sourceArchiveSha256': begin['sourceArchiveSha256'], 'tests': 3712, 'suites': 545, 'mainClasses': 1643,
                      'FESFlakyNotRun': 0, 'staticSixModules': 0, 'modules': modules, 'coverage': coverage,
                      'jarHashes': jar_hashes, 'changedClasses': changed, 'semanticChangedClasses': 1,
                      'allOriginalCaseIdentitiesRetained': True, 'newCases': data['newCases'],
                      'debugOnlyChangedClasses': 1, 'generatedSwitchDebug': debug, 'oldNativeImported': False,
                      'candidateNativePending': True, 'formalAccepted': False, 'global100': False,
                      'serverManifestSha256': sha(out / 'manifest.safe.json')}))


def qualify():
    local = W / 'pg3412-server-six-v1/manifest.safe.json'
    value = json.loads(local.read_bytes()); require(value['actualExit'] == 0, 'original full wrapper0')
    validate(value['snapshot'])
    data = {'candidateSource': SOURCE, 'expected': EXPECTED,
            'newCases': NEW_CASES,
            'priorManifestSha256': json.loads((W / 'pg3400-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())['result']['serverManifestSha256'],
            'priorJarHashes': json.loads((W / 'pg3400-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())['result']['jarHashes']}
    raw = '\n'.join(inspect.getsource(f) for f in [positions, verify_switch_debug, require, classify, independent]) + '\nindependent(' + repr(data) + ')\n'
    os.umask(0o077); out = W / 'pg3414-outbox-full-qualified-v1'; out.mkdir()
    (out / 'qualify.private.py').write_text(raw)
    rc, text = run("python3 - <<'QUALIFY'\n" + raw + '\nQUALIFY', timeout=90)
    (out / 'observer.private.log').write_text(text)
    receipt = {'actualExit': rc, 'qualificationSourceSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if rc == 0:
        receipt['result'] = json.loads(text.strip())
    (out / 'manifest.safe.json').write_text(json.dumps(receipt, sort_keys=True))
    print(json.dumps({'actualExit': rc, 'tests': receipt.get('result', {}).get('tests'), 'candidateNativePending': True}))
    return rc


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['whole', 'qualify'])
    raise SystemExit({'whole': whole, 'qualify': qualify}[parser.parse_args().action]())
