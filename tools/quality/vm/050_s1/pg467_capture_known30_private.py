"""Read-only actual known30/stopped graph snapshot to NEW root-private preservation.
No start/stop/current/permit repair. Private payloads must never be copied to Git or normal logs.
"""
import hashlib
import json
import os
import pathlib
import stat
import subprocess
import tarfile

assert os.geteuid() == 0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip() == 'e07aa706-1acd-4e65-b309-d7f330f79d54'
SAVE = pathlib.Path('/var/lib/pgpt-s1-preservation/pg467-parent-known30-private')
assert not SAVE.exists() and not SAVE.is_symlink()
FIELDS = 'Id,LoadState,ActiveState,SubState,Job,InvocationID,Type,Restart,RemainAfterExit,MainPID,ControlPID,Result,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,ExecMainCode,ExecMainStatus,KillMode,SendSIGKILL'
UNITS = ['schubert-nk-morning-controller.service', 'schubert-nk-api.service', 'schubert-nk-web.service', 'caddy.service',
         'artemis.service', 'schubert-nk-backup.service', 'schubert-nk-cleanup.service', 'schubert-nk-expiry-cleanup.service', 'schubert-nk-inbox-inspector.service']
def manager(unit):
    raw = subprocess.check_output(['/usr/bin/systemctl', 'show', unit, '--property=' + FIELDS], timeout=5)
    values = dict(line.split('=', 1) for line in raw.decode('ascii').splitlines())
    assert len(values) == 18
    return raw, values
before = {unit: manager(unit) for unit in UNITS}
parent = before[UNITS[0]][1]
assert parent['MainPID'] == parent['ControlPID'] == '0' and parent['Job'] == ''
assert parent['InvocationID'] == '86fd86f54b464bd29f73a844ee4f1bd3'
assert parent['Result'] == 'exit-code' and parent['ExecMainCode'] == '1' and parent['ExecMainStatus'] == '30'
for unit, pid, invocation in [(UNITS[1], '1587773', '28efa4cf44ef4302b4fc9c67d3bb7432'),
                              (UNITS[2], '1589852', '960e8045cf1f4c4b88d7ca0da2fc6f8e')]:
    value = before[unit][1]
    assert value['MainPID'] == value['ControlPID'] == '0' and value['InvocationID'] == invocation
    assert not (pathlib.Path('/proc') / pid).exists()
    assert value['Result'] == 'exit-code' and value['ExecMainCode'] == '1' and value['ExecMainStatus'] == '143'
    assert value['ActiveState'] == 'failed' and value['SubState'] == 'failed' and value['Job'] == ''
SAVE.mkdir(mode=0o700)
def save(name, payload):
    fd = os.open(SAVE / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(payload);stream.flush();os.fsync(stream.fileno())
for i, unit in enumerate(UNITS):
    save('unit-' + str(i) + '-before.properties', before[unit][0])
# Dead actors are not reconstructed; retain the original external spy separately.
paths = [pathlib.Path('/run/schubert-nk/startup'), pathlib.Path('/var/lib/schubert-nk/maintenance')]
metadata = {}
for root in paths:
    for p in [root, *sorted(root.rglob('*'))]:
        s = p.lstat()
        assert not stat.S_ISLNK(s.st_mode) and (stat.S_ISDIR(s.st_mode) or (stat.S_ISREG(s.st_mode) and s.st_nlink == 1))
        metadata[str(p)] = {'dev': s.st_dev, 'ino': s.st_ino, 'mode': s.st_mode, 'uid': s.st_uid, 'gid': s.st_gid,
                            'nlink': s.st_nlink, 'size': s.st_size, 'ctimeNs': s.st_ctime_ns, 'mtimeNs': s.st_mtime_ns}
        if p.is_file():
            assert s.st_size <= 1048576
            metadata[str(p)]['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
save('startup-original-metadata.private.json', json.dumps(metadata, sort_keys=True).encode())
archive = SAVE / 'startup-original.private.tar'
fd = os.open(archive, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'wb') as stream:
    with tarfile.open(fileobj=stream, mode='w') as tar:
        for root in paths:
            tar.add(root, arcname=root.name, recursive=True)
    stream.flush();os.fsync(stream.fileno())
dump = SAVE / 'current27.private.dump'
fd = os.open(dump, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'wb') as stream:
    result = subprocess.run(['/usr/bin/sudo', '-n', '-u', 'postgres', '/usr/bin/pg_dump', '--format=custom', '--dbname=schubert_nk'],
                            stdout=stream, stderr=subprocess.DEVNULL, timeout=60)
    assert result.returncode == 0
    stream.flush();os.fsync(stream.fileno())
for unit in UNITS:
    assert before[unit][1] == manager(unit)[1]
save('capture-complete.private.json', json.dumps({'parentKnownFailure30': True, 'normalExitClaimed': False,
     'ordinaryApiWebStopped143': True, 'originalStartupPreserved': True, 'dumpSha256': hashlib.sha256(dump.read_bytes()).hexdigest(),
     'startStopIssued': False, 'currentPermitRepaired': False}, sort_keys=True).encode())
fd = os.open(SAVE, os.O_RDONLY | os.O_DIRECTORY);os.fsync(fd);os.close(fd)
print('PG467_KNOWN30_CAPTURED parentActualFailure30=true ordinaryApiWebStopped143=true privatePreservation=true normalExitClaimed=false startStopIssued=false')
