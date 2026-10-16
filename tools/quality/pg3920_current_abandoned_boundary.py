"""New-only isolated DB suite against the exact current six qualified Main jars."""
import hashlib
import ast
import json
import os
import shlex
import subprocess
from pathlib import Path

from lan_server import copy, run
import pg3256_completion_guard_selected as previous
from pg1446_current_cold_stage import W
from pg3798_hygiene_current_observer import SOURCE

ROOT = Path(__file__).resolve().parents[2]
BASE = '/home/mini/schubert-nk-pgpt'
OUT = W / 'pg3920-current-abandoned-boundary-v1'
SLOT = 'PG3920-candidate-v1'
LABEL = 'PG3920'
FILES = previous.FILES
METHOD = 'mdb3920001RetainedRequestTimeBoundariesPreserveActualRowsAndOwnedLock'
LAUNCHER = 'org/junit/platform/junit-platform-launcher/1.13.4/junit-platform-launcher-1.13.4.jar'
LAUNCHER_SHA = '0b0beaeb6880a31149641d2d848b863712885469670c12099586d7f798522564'


def runtime_libraries(coverage, historical):
    require(historical.get(LAUNCHER) == LAUNCHER_SHA, 'independently successful fixed launcher binding')
    launchers = {n: h for n, h in coverage.items() if '/junit-platform-launcher/' in n}
    require(not launchers or launchers == {LAUNCHER: LAUNCHER_SHA}, 'no alternate launcher/version/hash')
    return {**coverage, LAUNCHER: LAUNCHER_SHA}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def server():
    raw = previous.server('statement')
    for old, new in [('PG3256', LABEL), ('source-full-PG3248', 'source-full-PG3734')]:
        require(old in raw, 'exact fixed server boundary')
        raw = raw.replace(old, new)
    before = raw.index('hosts=[]\n')
    after = raw.index('coverage_xml=out/', before)
    # Only the fresh selected stream is measured here. No historic native is imported,
    # and no new total four-counter/full-regression qualification is claimed.
    raw = raw[:before] + 'hosts=[]\n' + raw[after:]
    old = "'mdb3256001CompletionGuardSqlFailurePreservesCommittedBeginsAndEmptyBackupRoot'"
    require(raw.count(old) == 1, 'existing guard method retained exactly once')
    raw = raw.replace(old, old + ',' + repr(METHOD))
    marker = "require(all(sha(fixtures/n)==h for n,h in fixturehashes.items())"
    require(raw.count(marker) == 1, 'fixed-input postcondition boundary')
    raw = raw.replace(marker, "require(all(sha(Path(p))==INPUT['baseFull']['jarHashes'][m] for m,p in zip(['protocol','storage','bootstrap','api','web','batch'],jars)))\n" + marker)
    from pyflakes.api import check
    require(check('INPUT={}\n' + raw, '<current isolated DB suite>') == 0, 'complete namespace')
    compile(raw, '<current isolated DB suite>', 'exec')
    return raw


def main():
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed operator')
    full = json.loads((W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes())
    native = json.loads((W / 'pg3892-current-two-cohort-native-v1/input.safe.json').read_bytes())
    q = full['result']
    require(full['actualExit'] == q['actualExit'] == 0 and q['productionSource'] == SOURCE
            and q['tests'] == 3714 and q['mainClasses'] == 1643, 'genuine current whole authority')
    require(not subprocess.check_output(['git', 'diff', SOURCE, '--', 'src/*/src/main', 'pom.xml', '.mvn']), 'current Main/resources/settings unchanged')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    files = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in FILES}
    tests = (ROOT / FILES[0]).read_text().count('@Test\n')
    require(tests == 64 and METHOD in (ROOT / FILES[0]).read_text(), 'exact current64 including new boundary')
    tree = ast.parse((W / 'pg3256-completion-guard-selected-v1/selected.private.py').read_bytes())
    assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'INPUT' for t in n.targets))
    historical = ast.literal_eval(assignment.value)
    libraries = runtime_libraries(native['libraries'], historical['libraries'])
    inputs = {'source': SOURCE, 'head': head, 'baseFull': q, 'libraries': libraries, 'files': files, 'tests': tests}
    raw = 'INPUT=' + repr(inputs) + '\n' + server()
    os.umask(0o077)
    OUT.mkdir(mode=0o700)
    payload = OUT / 'selected.private.py'
    payload.write_text(raw)
    rc, _ = run(f'test ! -e {BASE}/runs/{SLOT} && test ! -e {BASE}/transfer/{SLOT} && mkdir -m700 {BASE}/transfer/{SLOT}', timeout=30)
    require(rc == 0, 'new-only selected execution; no overwrite or reattachment guessing')
    for name in FILES:
        destination = BASE + '/transfer/' + SLOT + '/' + name
        rc, _ = run('mkdir -p ' + shlex.quote(str(Path(destination).parent)), timeout=30)
        require(rc == 0, 'new transfer parent')
        rc, _ = copy(ROOT / name, destination, timeout=60)
        require(rc == 0, 'fixed nonsecret Test/helper transfer')
    rc, _ = copy(payload, BASE + '/transfer/' + SLOT + '/selected.private.py', timeout=60)
    require(rc == 0, 'fixed selected payload transfer')
    rc, output = run('python3 -B ' + BASE + '/transfer/' + SLOT + '/selected.private.py', timeout=1950)
    (OUT / 'observer.private.log').write_text(output)
    value = {'actualExit': rc, 'productionSource': SOURCE, 'testSource': head, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'vmActions': 0, 'formalAccepted': False}
    if rc == 0:
        value['result'] = json.loads([line for line in output.splitlines() if line.startswith('{')][-1])
    (OUT / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value, sort_keys=True))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
