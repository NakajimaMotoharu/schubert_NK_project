"""One required new-source whole six, preserving literal NoTests and all quality checks."""
import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy, run
import pg1476_corrected_server_six as engine

ROOT = Path(__file__).resolve().parents[2]
W = ROOT.parent / 'pgpt-runs/PG379'
SOURCE = '964e96e45bb588e7e75798b5adf425cbd9985427'
LABEL = 'PG4420'


def server_source(head, digest):
    raw = engine.server_source(head, digest)
    class Rebase(ast.NodeTransformer):
        def visit_Constant(self, node):
            value = node.value
            if type(value) is int and value in {3578, 523, 1635}:
                value = {3578: 3721, 523: 545, 1635: 1644}[value]
            elif isinstance(value, str):
                value = value.replace('PG1476', LABEL).replace('769ddb15cd735c25fef581b5f9850ef9d0053c0f', SOURCE)
            return ast.copy_location(ast.Constant(value), node)
    result = ast.unparse(ast.fix_missing_locations(Rebase().visit(ast.parse(raw))))
    compile(result, '<one required full3721>', 'exec')
    return result


def main():
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT):
        raise ValueError('candidate Main/Tests/resources remain exact source964e')
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out = W / 'pg4420-shared-manager-six-v1'; os.umask(0o077); out.mkdir(mode=0o700)
    archive = out / 'source.tar'
    with archive.open('xb') as target:
        subprocess.run(['git', 'archive', SOURCE, 'src', 'pom.xml', '.mvn', 'mvnw', 'program/characterization'], cwd=ROOT, stdout=target, check=True)
        target.flush(); os.fsync(target.fileno())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest(); raw = server_source(SOURCE, digest)
    from pyflakes.api import check
    if check(raw, '<complete six standalone>'): raise ValueError('full standalone static0 required')
    helper = out / 'full.private.py'; helper.write_text(raw)
    base = '/home/mini/schubert-nk-pgpt'
    paths = [base + '/source-full-' + LABEL, base + '/runs/' + LABEL + '-six-v1', base + '/transfer/' + LABEL + '-source.tar', base + '/tools/pg4420-full.py']
    status, _ = run(' && '.join('test ! -e ' + p for p in paths), timeout=30)
    if status != 0: raise ValueError('new-only full artifacts; inspect original instead of replay')
    for local, remote in [(archive, paths[2]), (helper, paths[3])]:
        status, _ = copy(local, remote, timeout=300)
        if status != 0: raise ValueError('fixed full input transfer failed; no blind restart')
    status, output = run('sha256sum ' + paths[2] + ' ' + paths[3], timeout=30)
    if status != 0 or digest not in output or hashlib.sha256(raw.encode()).hexdigest() not in output:
        raise ValueError('exact full input transfer bytes')
    (out / 'begin.safe.json').write_text(json.dumps({'source': SOURCE, 'operator': operator,
        'archiveSha256': digest, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(),
        'tests': 3721, 'suites': 545, 'mainClasses': 1644, 'replayAllowed': False,
        'trigger': 'SSC295 shared strict native manager reader across bootstrap/batch; old7bb native not portable; selected4412 NoTests preserved'}, sort_keys=True))
    status, _ = run('mkdir -m700 ' + paths[0] + ' && tar -xf ' + paths[2] + ' -C ' + paths[0], timeout=120)
    if status != 0: raise ValueError('one new fixed source extraction')
    status, output = run('python3 -B ' + paths[3], timeout=7200)
    (out / 'observer.private.log').write_text(output)
    result = {'actualExit': status, 'source': SOURCE, 'operator': operator, 'formalAccepted': False, 'independentQualificationPending': True}
    if status == 0: result['result'] = json.loads(next(v for v in reversed(output.splitlines()) if v.startswith('{')))
    (out / 'manifest.safe.json').write_text(json.dumps(result, sort_keys=True)); print(json.dumps(result)); return status


if __name__ == '__main__':
    raise SystemExit(main())
