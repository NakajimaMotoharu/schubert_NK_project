"""Seven real constructor/codec PT, one recompiled Main family; old jars are explicit auxiliaries only."""
import argparse
import ast
import hashlib
import json
import os
import shlex
import subprocess
from lan_server import copy, run
import pg3920_current_abandoned_boundary as previous
from git_source_contract import last_main_source
from pg3928_current_boundary_full_six import ROOT, W, require

MAIN = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest.java'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ExpiryWorkerRequestTest.java'
METHOD = 'ereq3962001ImmutableStepAdmissionDefinesIdentityAndStartBounds'
FILES = [MAIN, TEST, *previous.FILES[1:]]


def server(label):
    raw = previous.server().replace('PG3920', label).replace('repository.MorningDatabaseSessionTest', 'platform.ExpiryWorkerRequestTest').replace('repository/MorningDatabaseSession$Session', 'platform/CleanupWorkerRequest$Expiry$PriorExpiry').replace("classes.rglob('MorningDatabaseSession*.class')", "classes.rglob('CleanupWorkerRequest*.class')")
    require(raw.count('require(not mainclasses)') == 1, 'explicit old no-Main-compilation boundary')
    raw = raw.replace('require(not mainclasses)', "require(set(mainclasses)==set(INPUT['expectedMainNames']))\nmainimage=out/'main-image';mainimage.mkdir()\nfor n,h in mainclasses.items():\n p=mainimage/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((classes/n).read_bytes());require(sha(p)==h)")
    raw = raw.replace('jars[-1],str(coverage_xml)', 'str(mainimage),str(coverage_xml)')
    lines = raw.splitlines(); required = [i for i, line in enumerate(lines) if line.startswith('require(len(names)==expected and ')]
    require(len(required) == 1, 'one exact real Test identity condition')
    lines[required[0]] = 'require(len(names)==expected and {' + repr(METHOD) + '}.issubset(names))'
    raw = '\n'.join(lines).replace("'mainRecompiled':False", "'mainRecompiled':True,'mainFilesRecompiled':1,'wholeNewSourceQualification':False,'phase':INPUT['phase']")
    marker = '# Measure without converting remaining branches to PASS.'
    require(raw.count(marker) == 1, 'actual target counter boundary')
    raw = raw.replace(marker, "require(counters['BRANCH']['missed']==5 if INPUT['phase']=='before' else all(counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH']))")
    from pyflakes.api import check
    require(check('INPUT={}\n' + raw, '<actual seven scoped Main constructor tests>') == 0, 'complete standalone namespace')
    compile(raw, '<actual seven scoped Main constructor tests>', 'exec'); return raw


def main(phase):
    require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT), 'clean fixed scoped operator')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(); source = last_main_source(ROOT)
    full = json.loads((W / 'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes()); q = full['result']
    require(full['actualExit'] == 0 and q['productionSource'] == '7fffab57a567914956b66452e5e54388642efdec', 'qualified auxiliary jars, not a new Main global result')
    dependencies = ['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/' + n + '.java' for n in ['BatchStepAttempt', 'BatchRun', 'BatchStep']]
    require(not subprocess.check_output(['git', 'diff', q['sourceSnapshot'], 'HEAD', '--', *dependencies], cwd=ROOT), 'actual immutable constructor dependencies unchanged')
    if phase == 'before':
        require(not subprocess.check_output(['git', 'diff', q['sourceSnapshot'], 'HEAD', '--', MAIN], cwd=ROOT), 'record source before refactor remains exact original')
    else:
        before = json.loads((W / 'pg3962-prior-invariant-before-v1/manifest.safe.json').read_bytes()); require(before['actualExit'] == 0, 'genuine seven-Test before contract')
        changed = subprocess.check_output(['git', 'diff', '--name-only', before['testSource'], 'HEAD', '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT, text=True).splitlines()
        require(changed == [MAIN], 'only one immutable guard simplification, exact same Test oracle')
    tests = (ROOT / TEST).read_text().count('@Test\n'); require(tests == 7, 'exact seven actual Test methods')
    native = json.loads((W / 'pg3892-current-two-cohort-native-v1/input.safe.json').read_bytes())
    tree = ast.parse((W / 'pg3256-completion-guard-selected-v1/selected.private.py').read_bytes()); assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'INPUT' for t in n.targets)); old = ast.literal_eval(assignment.value)
    label = 'PG3962' if phase == 'before' else 'PG3964'; slot = 'pg3962-prior-invariant-before-v1' if phase == 'before' else 'pg3964-prior-invariant-after-v1'
    inputs = {'source': source, 'head': head, 'phase': phase, 'baseFull': q, 'libraries': previous.runtime_libraries(native['libraries'], old['libraries']),
              'files': {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in FILES}, 'tests': 7,
              'expectedMainNames': [n for n in q['allPhysicalMainSha256']['batch'] if n.startswith('dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest')]}
    os.umask(0o077); out = W / slot; out.mkdir(); code = 'INPUT=' + repr(inputs) + '\n' + server(label); payload = out / 'selected.private.py'; payload.write_text(code)
    base = '/home/mini/schubert-nk-pgpt'; destination = base + '/transfer/' + label + '-candidate-v1'
    status, _ = run('test ! -e ' + base + '/runs/' + label + '-candidate-v1 && mkdir -m700 ' + destination, timeout=30); require(status == 0, 'new-only scoped execution')
    for name in FILES:
        remote = destination + '/' + name; status, _ = run('mkdir -p ' + shlex.quote(str(__import__('pathlib').Path(remote).parent)), timeout=30); require(status == 0, 'new transfer parent')
        status, _ = copy(ROOT / name, remote, timeout=60); require(status == 0, 'fixed scoped source transfer')
    status, _ = copy(payload, destination + '/selected.private.py', timeout=60); require(status == 0, 'fixed actual scoped payload')
    status, output = run('python3 -B ' + destination + '/selected.private.py', timeout=400); (out / 'observer.private.log').write_text(output)
    value = {'actualExit': status, 'phase': phase, 'mainSource': source, 'testSource': head, 'auxiliaryFullSource': q['productionSource'], 'wholeNewSourceQualification': False, 'payloadSha256': hashlib.sha256(code.encode()).hexdigest(), 'vmActions': 0}
    if status == 0: value['result'] = json.loads(next(line for line in reversed(output.splitlines()) if line.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return status


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['before', 'after']); raise SystemExit(main(parser.parse_args().phase))
