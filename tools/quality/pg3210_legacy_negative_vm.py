"""New-only independent kernel/Unit negative fixture, not another business replay.

SS343/451; PT-OPS-3210-001..004. Existing primary VM remains alive and untouched.
Only the three historically sealed, already read-only backing files are shared.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import pg2810_network_resume_cold as original

BASE = original.BASE
CHAIN = original.CHAIN
OUT = BASE / 'vm/pg3210-legacy-negative-v1'
PORT = 22224
LOADED_SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
PRIMARY = {'pid': 4599, 'ticks': 101242, 'argvSha256': 'f765c39c924d24fc03739355785e22c06b302d68418a85860e3d661960a2b106',
           'hostBoot': 'c7964823-c628-4ef2-99b5-07b0f0b62bba', 'exe': '/usr/bin/qemu-system-x86_64'}
REFERENCE = BASE / 'vm/pg2810-network-resume-cold-v1/manifest.safe.json'
REFERENCE_SHA = '03d0ace38e19d1cff3b2676c84d238b823cee9eb8af4c275941ac06312903d9d'
identity, digest, require = original.identity, original.digest, original.require


def qualify_primary(observed, modes, qemu_pids):
    require(type(observed) is dict and observed == PRIMARY)
    require(type(modes) is dict and set(modes) == {str(p) for p in CHAIN})
    require(all(type(v) is int and v == os.O_RDONLY for v in modes.values()))
    require(type(qemu_pids) is list and qemu_pids == [PRIMARY['pid']])
    return observed


def primary(fixture_pid=None):
    require(os.geteuid() == 0)
    p = Path('/proc') / str(PRIMARY['pid'])
    before = (p / 'stat').read_text().rpartition(')')[2].split()
    argv = (p / 'cmdline').read_bytes()
    value = {'pid': PRIMARY['pid'], 'ticks': int(before[19]), 'argvSha256': hashlib.sha256(argv).hexdigest(),
             'hostBoot': Path('/proc/sys/kernel/random/boot_id').read_text().strip(), 'exe': str((p / 'exe').readlink())}
    modes = {}
    for fd in (p / 'fd').iterdir():
        try:
            name = str(fd.readlink())
        except FileNotFoundError:
            continue
        if name in {str(path) for path in CHAIN}:
            require(name not in modes)
            info = dict(line.split(':', 1) for line in (p / 'fdinfo' / fd.name).read_text().splitlines() if ':' in line)
            modes[name] = int(info['flags'].strip(), 8) & os.O_ACCMODE
    require(before[19] == (p / 'stat').read_text().rpartition(')')[2].split()[19] and argv == (p / 'cmdline').read_bytes())
    qemu = sorted(int(row.split()[0]) for row in subprocess.check_output(['ps', '-eo', 'pid=,comm='], text=True).splitlines() if len(row.split()) == 2 and row.split()[1].startswith('qemu-system'))
    if fixture_pid is not None:
        require(type(fixture_pid) is int and fixture_pid != PRIMARY['pid'] and fixture_pid in qemu)
        qemu.remove(fixture_pid)
    return qualify_primary(value, modes, qemu)


def reference():
    s = REFERENCE.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and not os.listxattr(REFERENCE))
    raw = REFERENCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == REFERENCE_SHA)
    proof = json.loads(raw)
    require(proof['actualExit'] == proof['logicalCompareExit'] == 0 and set(proof['chain']) == {str(p) for p in CHAIN})
    return proof['chain']


def chain(proof, full=True):
    info = json.loads(subprocess.check_output(['qemu-img', 'info', '-U', '--backing-chain', '--output=json', str(CHAIN[0])]))
    original.validate_chain(info)
    for p in CHAIN:
        require(not p.is_symlink() and identity(p) == proof[str(p)]['identity'])
        if full:
            require(digest(p) == proof[str(p)]['sha256'])
    return info


def capacity():
    # Worst48GiB COW +8GiB staging +8GiB data/evidence, plus20GiB preservation.
    fs = os.statvfs(BASE)
    require(fs.f_bavail * fs.f_frsize >= 84 * 1024**3)
    memory = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    require(memory >= 12 * 1024**3)
    require(not subprocess.check_output(['ss', '-H', '-lnt', '( sport = :22224 )']))
    for name, expected in original.TOOLS.items():
        require(digest(BASE / 'tools' / name) == expected)


def save(name, value):
    with (OUT / name).open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())
    fd = os.open(OUT, os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def arguments():
    args = original.arguments()
    args = [str(OUT) + value[len(str(original.OUT)):] if value.startswith(str(original.OUT)) else value.replace(str(original.OUT), str(OUT)) for value in args]
    args[args.index('-name') + 1] = 'pgpt-legacy-negative-3210'
    args[args.index('-smp') + 1] = '2'
    args[args.index('-m') + 1] = '4096'
    args[args.index('-netdev') + 1] = 'user,id=pgptnet,restrict=on,hostfwd=tcp:127.0.0.1:22224-:22'
    args[args.index('-device') + 1] = 'virtio-net-pci,netdev=pgptnet,romfile=,mac=52:54:00:32:10:01'
    return args


def preserve():
    primary(); capacity(); proof = reference(); info = chain(proof)
    require(not OUT.exists())
    OUT.mkdir(mode=0o700)
    save('preserve-reservation.safe.json', {'purpose': 'ISOLATED_NEGATIVE_UNIT_FIXTURE', 'primary': PRIMARY, 'referenceSha256': REFERENCE_SHA, 'loadedMainSourcePlanned': LOADED_SOURCE,
                                          'inheritedDiskIsNotCurrentDeploymentAuthority': True, 'businessActions': 0, 'chain': proof, 'information': info})
    with (OUT / 'create.private.log').open('xb') as log:
        result = subprocess.run(['qemu-img', 'create', '-f', 'qcow2', '-F', 'qcow2', '-b', str(CHAIN[0]), str(OUT / 'active.qcow2')], stdout=log, stderr=log)
    require(result.returncode == 0)
    with (OUT / 'compare.private.log').open('xb') as log:
        result = subprocess.run(['qemu-img', 'compare', '-U', '-q', '-f', 'qcow2', '-F', 'qcow2', str(CHAIN[0]), str(OUT / 'active.qcow2')], stdout=log, stderr=log)
    require(result.returncode == 0); primary(); chain(proof)
    save('preserve-result.safe.json', {'actualExit': 0, 'logicalCompareExit': 0, 'chain': proof, 'overlaySha256': digest(OUT / 'active.qcow2'),
                                     'primaryUnchanged': True, 'oldRAMRunPermitNativeAuthorityTransferred': False, 'businessActions': 0, 'formalAccepted': False})
    print('PG3210_PRESERVE actual0=true primaryUnchanged=true newOnly=true businessActions0=true', flush=True)


def boot():
    primary(); capacity(); proof = reference(); chain(proof)
    result = json.loads((OUT / 'preserve-result.safe.json').read_bytes())
    require(result['actualExit'] == result['logicalCompareExit'] == 0 and result['chain'] == proof)
    require(digest(OUT / 'active.qcow2') == result['overlaySha256'])
    require(all(not os.path.lexists(OUT / name) for name in ['boot-reservation.safe.json', 'boot-result.safe.json', 'qmp.sock', 'qemu.pid', 'console.private.log', 'launch.private.log']))
    argv = arguments()
    save('boot-reservation.safe.json', {'issuedOnce': True, 'purpose': 'ISOLATED_NEGATIVE_UNIT_FIXTURE', 'argv': argv, 'argvSha256': hashlib.sha256(b'\0'.join(v.encode() for v in argv) + b'\0').hexdigest(), 'toolSha256': digest(Path(__file__)), 'primary': PRIMARY})
    with (OUT / 'launch.private.log').open('xb') as log:
        status = subprocess.run(argv, stdout=log, stderr=log)
    require(status.returncode == 0)
    pid = int((OUT / 'qemu.pid').read_text()); require(pid != PRIMARY['pid'])
    p = Path('/proc') / str(pid)
    value = {'pid': pid, 'ticks': int((p / 'stat').read_text().rpartition(')')[2].split()[19]), 'argvSha256': digest(p / 'cmdline'), 'exe': str((p / 'exe').readlink())}
    require(value['argvSha256'] == hashlib.sha256(b'\0'.join(v.encode() for v in argv) + b'\0').hexdigest() and value['exe'] == '/usr/bin/qemu-system-x86_64')
    primary(pid)
    chain(proof, False)
    save('boot-result.safe.json', {'actualExit': 0, 'fixtureOwner': value, 'primaryUntouched': True, 'guestReauthenticationPending': True, 'businessAccepted': False, 'formalAccepted': False})
    print(json.dumps({'actualExit': 0, 'fixtureOwner': value, 'guestReauthenticationPending': True, 'businessAccepted': False}), flush=True)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['preserve', 'boot']); phase = parser.parse_args().phase
    os.umask(0o077)
    fd = os.open(BASE / 'vm/boot-guard.lock', os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        s = os.fstat(fd); require(stat.S_ISREG(s.st_mode) and s.st_uid == 0 and stat.S_IMODE(s.st_mode) == 0o600 and s.st_nlink == 1)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        (preserve if phase == 'preserve' else boot)()
    finally:
        os.close(fd)


if __name__ == '__main__':
    main()
