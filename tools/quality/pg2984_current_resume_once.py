"""One new activation of already-completed current run, not replay of prior start."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg2982_current_resume_observer import namespace, SOURCE, BOM
import pg2980_scoped_resume_independent_post as post
import pg1257_fresh_independent_terminal_post as schema
from pg2360_current_completed_resume_once import body as proven_body

SLOT = 'pg2984-current-fresh-resume-once-v1'


def body():
    proof = json.loads((W / post.SLOT / 'manifest.safe.json').read_bytes())
    if proof['actualExit'] != 0 or not proof['normalResumePrepared']:
        raise ValueError('current normal finite independent post required')
    raw = proven_body()
    for a, b in [('pg2358', 'pg2982'), ('pg2360-current-completed-resume-once-v1', SLOT), ('3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8', SOURCE), ('62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c', BOM), ('PG2126', 'PG2802'), ('91f5484b-9702-4c7c-97f3-dd5110a853f9', '0dc63b79-3f9a-450c-b2a6-56f86272d272'), ('6873c5eb138bbd3dbd6a8e00398738b837dca149325db0ff555d0901bd1b10ec', proof['preparedAfterSha256']), ('9bf72ad074cbe798ef6082d31f25be89fe7cf3e3d31be484a997ce4b0b82c955', proof['nativeCanonicalSha256'])]:
        raw = raw.replace(a, b)
    old = "accepted_before={**after,'configuration':dict(current_view)}"
    if raw.count(old) != 1:
        raise ValueError('one prepared configuration already independently projected')
    return raw.replace(old, 'accepted_before=after')


def payload(hashes):
    proof = json.loads((W / post.SLOT / 'manifest.safe.json').read_bytes())
    seals = {n: proof['proofHashes'][n]['sha256'] for n in schema.previous.SEALS}
    raw = post.payload(seals)
    tree = ast.parse(raw)
    scope = next(n for n in tree.body if isinstance(n, ast.Try) and any(isinstance(x, ast.FunctionDef) and x.name == 'snapshot' for x in n.body))
    lines = raw.splitlines(keepends=True)
    end = next(i for i in range(scope.lineno - 1, scope.end_lineno) if lines[i].startswith('finally:'))
    header = 'WATCH_FILES=' + repr(hashes) + '\nHASHES=' + repr(proof['toolHashes']) + '\nRECEIPT=' + repr((W / 'pg2890-network-owned-stop-tools-v1/pg2890_parent_receipt.py').read_text()) + '\n'
    raw = header + ''.join(lines[:end]) + '\n'.join('    ' + line if line else line for line in body().splitlines()) + '\n' + ''.join(lines[end:scope.end_lineno]) + '\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n'
    if check(raw, '<whole current fresh-resume once>'):
        raise ValueError('complete independent start namespace required')
    compile(raw, '<whole current fresh-resume once>', 'exec')
    return raw


def main():
    os.umask(0o077)
    if subprocess.check_output(['git', 'status', '--porcelain']):
        raise ValueError('clean fixed once operator required')
    changes = subprocess.check_output(['git', 'diff', '--name-only', SOURCE, '--', 'src', 'pom.xml'], text=True).splitlines()
    if any('/src/main/' in name or name.endswith('pom.xml') for name in changes):
        raise ValueError('same current Main required')
    proof = json.loads((W / post.SLOT / 'manifest.safe.json').read_bytes())
    if proof['actualExit'] != 0 or proof['productionSource'] != SOURCE or not proof['normalResumePrepared'] or not proof['allClientAdvisoryFlock0']:
        raise ValueError('qualified current preparation and zero-resource post required')
    if not (W / 'pg2982-watch-v1.started').exists() or (W / 'pg2982-watch-v1.exit').exists():
        raise ValueError('new live immutable observer required')
    frames = [json.loads(line) for line in (W / 'pg2982-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states = [x['states'] for x in frames if 'states' in x]
    if not states or any(v.get('race') or v['MainPID'] != '0' or v['ControlPID'] != '0' or v['Job'] for v in states[-1].values()):
        raise ValueError('fresh stable quiescent observer frame required')
    hashes = {n: hashlib.sha256(s.encode()).hexdigest() for n, s in namespace()['files']().items()}
    if {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (P / 'pg2982-observer-stage-v1').iterdir()} != hashes:
        raise ValueError('same staged immutable observer closure required')
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload(hashes)
    (out / 'payload.private.py').write_text(raw)
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P / 'current-management-critical.lock'):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=90)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    (out / 'stdout.private.json').write_bytes(r.stdout)
    value = {'actualExit': r.returncode, 'operatorSource': operator, 'sourceQualified': operator == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() and not subprocess.check_output(['git', 'status', '--porcelain']), 'productionSource': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'startedUTC': start, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'formalAccepted': False, 'clientSuccessIsNotParentSuccess': True, 'replayForbidden': True}
    if not r.returncode:
        value['guest'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
