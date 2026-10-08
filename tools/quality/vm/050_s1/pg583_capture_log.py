"""Reuse sealed readonly collector with exact substitutions; no service or DB mutation."""
import ast
import hashlib
import json
import os
import pathlib
import subprocess

R = pathlib.Path(__file__).parent
W = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload():
    parsed = ast.parse((R / 'pg564_capture_log_session.py').read_text())
    raw = next(ast.literal_eval(n.value) for n in parsed.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
    replacements = {
        '/pg553-newrun-preflight-v2/before.private.json': '/pg573-fresh-parent-v2/before.private.json',
        'b9a70c2635febf3893b17369af3ddfdf721f040b3d6782423790ee63353bac87': '557ae9688c03162fe1962cd81d93eb9e4a70eb9acca998a02040afb96f0ec505',
        '/pg559-terminal-readback-v2/after.private.json': '/pg579-native-stop-v1/after.private.json',
        '23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677': 'cb5951e30fda2ef63f2691a24f302e46b8cffcff6c8345e69644672b9135eaf6',
        '3bcfbad981e64d8fadda66f27d1994fa': 'c9949e0a2b84426f84395ccf97cbe3eb',
        'check(len(events)==114)': 'check(len(events)==117)',
        'PG554-ordinary-newrun-v1': 'PG573-ordinary-newrun-v2',
        'pg564-independent-log-session-v1': 'pg583-independent-log-session-v1',
        'p.lstat()==s': 'meta(p.lstat())==meta(s)',
        'path.lstat()==s': 'meta(path.lstat())==meta(s)',
    }
    for old, new in replacements.items():
        assert raw.count(old) == (2 if old in ('b9a70c2635febf3893b17369af3ddfdf721f040b3d6782423790ee63353bac87',
                                             '23263d00948c5df5aca9aa4741a4d0266d9b8d20ebe400c7d180f89bb9ce6677') else 1)
        raw = raw.replace(old, new)
    raw = raw.replace('def check(v):', 'def meta(s):return(s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)\ndef check(v):')
    core = (R / 'pg564_log_session_oracle.py').read_text()
    extension = ast.parse((R / 'pg583_log_oracle.py').read_text())
    imports = [n for n in extension.body if isinstance(n, ast.ImportFrom) and n.module == 'pg564_log_session_oracle']
    assert len(imports) == 1
    extension.body.remove(imports[0])
    return 'ORACLE_SRC=' + repr(core + '\n' + ast.unparse(extension)) + '\n' + raw


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain']) == b''
    log = W / 'pg583-log-session-capture-v1.private.log'
    code = W / 'pg583-log-session-capture-v1.exit'
    receipt = W / 'pg583-log-session-capture-v1.safe.json'
    assert not any(os.path.lexists(p) for p in (log, code, receipt))
    ssh = ['ssh', '-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes', '-oStrictHostKeyChecking=yes',
           '-oUserKnownHostsFile=' + str(P / 'known_hosts'), '-p', '22222', 'ubuntu@127.0.0.1', 'sudo -n python3 -B -']
    source = payload()
    with log.open('xb') as stream:
        result = subprocess.run(ssh, input=source.encode(), stdout=subprocess.PIPE, stderr=stream, timeout=90)
        stream.flush();os.fsync(stream.fileno())
    with code.open('x') as stream:
        stream.write(str(result.returncode) + '\n');stream.flush();os.fsync(stream.fileno())
    if result.returncode == 0:
        safe = json.loads(result.stdout)
        assert safe['actualExit'] == 0 and safe['plaintextExported'] is False
        safe.update(operatorSource=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                    collectorPayloadSha256=hashlib.sha256(source.encode()).hexdigest())
        with receipt.open('x') as stream:
            json.dump(safe, stream, sort_keys=True);stream.flush();os.fsync(stream.fileno())
        print(json.dumps(safe))
    else:
        print(json.dumps({'actualExit':result.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest()}))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
