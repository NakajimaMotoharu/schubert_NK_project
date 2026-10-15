"""Fixed fixture-only stage/setup/execute; current owner authenticated each time.

SS343/451/PT-OPS-LFACT001..007. No automatic retry, primary operations or
production deployment. Keys remain local. Any failed/native output is private.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import run
from pg1446_current_cold_stage import W, SSH, P
from pg3212_legacy_negative_forward import fingerprint
from pg3214_legacy_fixture_compile import OUT as COMPILED

ROOT = Path(__file__).resolve().parents[2]
OBSERVER = ROOT / 'tools/quality/vm/050_s1/pg3216_legacy_negative_observer.py'
OUT = W / 'pg3216-legacy-negative-v2'
STAGE = '/home/ubuntu/pg3216-legacy-negative-v2'
BOOT = 'dd710ec8-bfdf-4157-b445-8073895110d2'
FIXTURE = {'pid': 445092, 'ticks': 3906100, 'argvSha256': 'f67196ed972d7fe199fb4e9089a45c98b1f9ae619ee6ffbf989af14234ef5f3e', 'exe': '/usr/bin/qemu-system-x86_64'}

RECEIVER_PREP = '''import pwd,stat
user=pwd.getpwnam('ubuntu');parent=Path('/home/ubuntu');home=parent.lstat()
assert stat.S_ISDIR(home.st_mode)and not parent.is_symlink()and home.st_uid==user.pw_uid and home.st_gid==user.pw_gid and user.pw_uid>0
p=Path(STAGE);assert p.parent==parent and not os.path.lexists(p)
p.mkdir(mode=0o700);os.chown(p,user.pw_uid,user.pw_gid)
s=p.lstat();assert s.st_uid==user.pw_uid and s.st_gid==user.pw_gid and stat.S_IMODE(s.st_mode)==0o700 and not list(p.iterdir())
'''


def require(value):
    if not value: raise ValueError('exact fixture transport refused; never retry automatically')


def owners():
    fixed = json.loads((P / 'pg3212-legacy-negative-forward-v1/running.safe.json').read_bytes())
    require(fingerprint(fixed['parent']['pid']) == fixed['parent'] and fingerprint(fixed['child']['pid']) == fixed['child'])
    raw = """import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/home/mini/schubert-nk-pgpt/tools/pg3210-negative-fixed-v1')
import pg3210_legacy_negative_vm as v
v.primary(FIXTURE['pid'])
p=Path('/proc')/str(FIXTURE['pid']);s=(p/'stat').read_text().rpartition(')')[2].split();a=(p/'cmdline').read_bytes()
assert {'pid':FIXTURE['pid'],'ticks':int(s[19]),'argvSha256':hashlib.sha256(a).hexdigest(),'exe':str((p/'exe').readlink())}==FIXTURE
assert s[19]==(p/'stat').read_text().rpartition(')')[2].split()[19]and a==(p/'cmdline').read_bytes()
print(json.dumps({'actualExit':0,'primaryAndFixtureOwned':True}))
"""
    code, output = run("python3 -B - <<'OWNERS'\nFIXTURE=" + repr(FIXTURE) + '\n' + raw + '\nOWNERS', timeout=20, sudo=True)
    require(code == 0 and json.loads(next(s for s in output.splitlines() if s.startswith('{')))['actualExit'] == 0)


def ssh():
    args = list(SSH); args[args.index('-p') + 1] = '22224'
    args[-1:-1] = ['-o', 'HostKeyAlias=[127.0.0.1]:22222']
    return args


def guest(code, name, timeout=60):
    guard = "from pathlib import Path\nimport os\nassert os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==" + repr(BOOT) + '\n'
    with (OUT / name).open('xb') as log:
        value = subprocess.run(ssh() + ['sudo', '-n', 'python3', '-B', '-'], input=(guard + code).encode(), stdout=log, stderr=log, timeout=timeout)
    return value.returncode


def save(name, value):
    with (OUT / name).open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())


def stage():
    require(not subprocess.check_output(['git', 'status', '--porcelain']))
    proof = json.loads((COMPILED / 'manifest.safe.json').read_bytes())
    require(proof['actualExit'] == 0 and proof['casesRun'] == 0 and proof['mainClasses'] == 1643 and proof['mainRecompiled'] is False)
    archive = COMPILED / 'runtime.private.tar'
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == proof['archiveSha256'])
    OUT.mkdir(mode=0o700)
    code = 'STAGE=' + repr(STAGE) + '\n' + RECEIVER_PREP
    require(guest(code, 'stage-reservation.private.log') == 0)
    args = ['scp', '-q', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(P / 'known_hosts'),
            '-o', 'HostKeyAlias=[127.0.0.1]:22222', '-i', str(P / 'vm-access'), '-P', '22224', str(archive), str(OBSERVER), 'ubuntu@127.0.0.1:' + STAGE + '/']
    with (OUT / 'copy.private.log').open('xb') as log:
        copied = subprocess.run(args, stdout=log, stderr=log, timeout=60)
    require(copied.returncode == 0)
    digest = hashlib.sha256(OBSERVER.read_bytes()).hexdigest()
    code = 'import hashlib\np=Path(' + repr(STAGE) + ')\n'
    code += 'assert {x.name for x in p.iterdir()}=={"runtime.private.tar","pg3216_legacy_negative_observer.py"}\n'
    code += 'assert hashlib.sha256((p/"runtime.private.tar").read_bytes()).hexdigest()==' + repr(proof['archiveSha256']) + '\n'
    code += 'assert hashlib.sha256((p/"pg3216_legacy_negative_observer.py").read_bytes()).hexdigest()==' + repr(digest) + '\n'
    code += 'for x in p.iterdir():os.chown(x,0,0);x.chmod(0o400)\nos.chown(p,0,0);p.chmod(0o700)\n'
    require(guest(code, 'stage-verify.private.log') == 0)
    save('stage.safe.json', {'actualExit': 0, 'observerSha256': digest, 'compiled': proof, 'boot': BOOT, 'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()})


def phase(name):
    proof = json.loads((OUT / 'stage.safe.json').read_bytes())
    require(proof['actualExit'] == 0 and proof['boot'] == BOOT)
    code = 'import hashlib,sys\np=Path(' + repr(STAGE) + ')\nassert hashlib.sha256((p/"pg3216_legacy_negative_observer.py").read_bytes()).hexdigest()==' + repr(proof['observerSha256']) + '\n'
    args = ['python3', '-B', STAGE + '/pg3216_legacy_negative_observer.py', name]
    if name == 'setup':
        args += ['--archive-sha', proof['compiled']['archiveSha256'], '--input-sha', proof['compiled']['inputSha256']]
    code += 'os.execv("/usr/bin/python3",' + repr(args) + ')\n'
    actual = guest(code, name + '.private.log', timeout=180)
    save(name + '.safe.json', {'actualExit': actual, 'boot': BOOT, 'observerSha256': proof['observerSha256'], 'casesNotYetIndependentlyQualified': True, 'formalAccepted': False})
    require(actual == 0)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['stage', 'setup', 'execute']); selected = parser.parse_args().phase
    owners()
    if selected == 'stage': stage()
    else: phase(selected)
    print('PG3216_' + selected.upper() + ' actual0=true formal=false', flush=True)


if __name__ == '__main__':
    main()
