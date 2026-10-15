"""Isolated actual-Unit negative PT; independent kernel witness, not business entry.

SS343/451/PT-OPS-LFACT001..007. Fixed guest boot only. Refusal alone never
passes. Failed/native output is retained and cannot qualify another cohort.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import queue
import re
import select
import socket
import stat
import struct
import subprocess
import tarfile
import threading
import time

BOOT = 'dd710ec8-bfdf-4157-b445-8073895110d2'
SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
BASE = Path('/var/lib/pgpt-negative-3210')
RUN = Path('/run/pgpt-negative-3210')
STAGE = Path('/home/ubuntu/pg3216-legacy-negative-v2')
APPROVAL = Path('/etc/schubert-nk/release-approval/current')
ORIGINAL_APPROVAL = '7c22aaff846b9605e3f83e8f6291de761f46b8e0d0a88d35d5a07d5756861984'
BAD = b'PGPT_INVALID_APPROVAL\n'
UNIT = 'schubert-nk-morning-controller.service'
DROP = Path('/etc/systemd/system') / (UNIT + '.d/zz-pg3216-negative-fixture.conf')
IDS = ['PT-OPS-LFACT' + str(i).zfill(3) for i in range(1, 8)]
PROTECTED = [Path('/run/schubert-nk'), Path('/var/lib/schubert-nk/maintenance'), Path('/srv/schubert-nk/backup')]
RESULTS = BASE
CASE = BASE / 'case-cohort-v1'
NATIVE = BASE / 'cohort-native.exec'
RETAINED_TERMINAL = False


def require(value):
    if not value:
        raise ValueError('isolated negative fixture contract refused')


def guard():
    require(os.geteuid() == 0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip() == BOOT)


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda: file.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def save(name, value):
    with (RESULTS / name).open('x') as file:
        json.dump(value, file, sort_keys=True); file.flush(); os.fsync(file.fileno())


def command(args, allowed=(0,), timeout=15):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    require(result.returncode in allowed)
    return result


def unit():
    keys = ['Id', 'ActiveState', 'SubState', 'MainPID', 'ControlPID', 'InvocationID', 'ControlGroup', 'Job', 'ExecMainCode', 'ExecMainStatus', 'Result']
    text = command(['systemctl', 'show', UNIT] + ['--property=' + key for key in keys]).stdout
    value = dict(line.split('=', 1) for line in text.splitlines())
    require(set(value) == set(keys) and value['Id'] == UNIT)
    return value


def tree():
    value = {}
    for root in PROTECTED:
        require(root.is_dir() and not root.is_symlink())
        for p in [root, *sorted(root.rglob('*'))]:
            s = p.lstat()
            require(stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode))
            value[str(p)] = [s.st_dev, s.st_ino, s.st_uid, s.st_gid, s.st_mode, s.st_nlink,
                             s.st_size if p.is_file() else None, s.st_mtime_ns,
                             sha(p) if p.is_file() else None]
    return value


def database():
    def sql(text):
        return command(['runuser', '-u', 'postgres', '--', 'psql', '-XAt', '-v', 'ON_ERROR_STOP=1', '-d', 'schubert_nk', '-c', text]).stdout.strip()
    names = sql("SELECT schemaname||'.'||tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY schemaname,tablename").splitlines()
    require(len(names) == 25 and 'schubert_meta.flyway_schema_history' in names)
    rows = {}
    for name in names:
        require(re.fullmatch(r'[a-z_]+\.[a-z_]+', name) is not None)
        rows[name] = sql("SELECT count(*)::text||'|'||md5(COALESCE(string_agg(v,E'\\n' ORDER BY v),'')) FROM (SELECT row_to_json(t)::text AS v FROM " + name + ' t) s')
    require(sql("SELECT count(*) FROM pg_stat_activity WHERE datname='schubert_nk' AND pid<>pg_backend_pid() AND backend_type='client backend'") == '0')
    require(sql("SELECT count(*) FROM pg_locks WHERE locktype='advisory' AND database=(SELECT oid FROM pg_database WHERE datname='schubert_nk')") == '0')
    return rows


def setup(archive_sha, input_sha):
    guard(); require(not BASE.exists() and not RUN.exists() and not DROP.exists())
    require(unit()['MainPID'] == '0' and unit()['ActiveState'] == 'inactive')
    archive = STAGE / 'runtime.private.tar'
    require(sha(archive) == archive_sha and sha(APPROVAL) == ORIGINAL_APPROVAL)
    BASE.mkdir(mode=0o700); RUN.mkdir(mode=0o700)
    runtime = BASE / 'runtime'; runtime.mkdir(mode=0o700)
    with tarfile.open(archive, 'r:') as tar:
        members = tar.getmembers(); mapping = {m.name: m for m in members}
        require(len(mapping) == len(members) and 'input.safe.json' in mapping)
        for name, member in mapping.items():
            p = PurePosixPath(name)
            require(member.isfile() and not p.is_absolute() and '..' not in p.parts and str(p) == name and member.size < 64 * 1024**2)
        raw = tar.extractfile(mapping['input.safe.json']).read()
        require(hashlib.sha256(raw).hexdigest() == input_sha)
        meta = json.loads(raw)
        require(set(mapping) == set(meta['files']) | {'input.safe.json'} and meta['loadedMainSource'] == SOURCE
                and meta['allMainSameBytes'] == 1643 and meta['allResourceMetaSameBytes'] == 79 and meta['hostTests'] == 3694)
        for name, member in mapping.items():
            data = raw if name == 'input.safe.json' else tar.extractfile(member).read()
            if name != 'input.safe.json':
                require(len(data) == meta['files'][name]['bytes'] and hashlib.sha256(data).hexdigest() == meta['files'][name]['sha256'])
            p = runtime / name; p.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            with p.open('xb') as file:
                file.write(data); file.flush(); os.fsync(file.fileno())
            p.chmod(0o400)
    require(set(meta['runtimeClasspath']) == {'classes'} | {n for n in meta['files'] if n.startswith(('jars/', 'lib/'))})
    # Preserve the copied fixture's original approval privately, never the primary VM's.
    original = APPROVAL.read_bytes()
    s = APPROVAL.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_uid == s.st_gid == 0 and stat.S_IMODE(s.st_mode) == 0o400 and s.st_nlink == 1)
    with (BASE / 'original-approval.private').open('xb') as file:
        file.write(original); file.flush(); os.fsync(file.fileno())
    # Controlled, public malformed vector, identical proper inode metadata.
    with APPROVAL.open('wb') as file:
        file.write(BAD); file.flush(); os.fsync(file.fileno())
    require(APPROVAL.lstat().st_ino == s.st_ino)
    for name in ['startup', 'backup-request', 'cleanup-request', 'expiry-request', 'maintenance']:
        p = Path('/run/schubert-nk') / name
        if not p.exists(): p.mkdir(mode=0o700)
        a = p.lstat(); require(stat.S_ISDIR(a.st_mode) and a.st_uid == a.st_gid == 0 and stat.S_IMODE(a.st_mode) == 0o700 and not list(p.iterdir()))
    cp = ':'.join(str(runtime / name) for name in meta['runtimeClasspath'])
    require(' ' not in cp and '\n' not in cp)
    text = ('# Fixture-only negative admission, not MorningProcessMain/normal deployment.\n[Service]\n'
            'ExecStart=\nLoadCredential=\nWorkingDirectory=' + str(BASE) + '\nSuccessExitStatus=\n'
            'ExecStart=/usr/bin/java -javaagent:' + str(runtime / 'agent.jar') + '=destfile=' + str(BASE / 'cohort-native.exec') + ',append=false,sessionid=PG3216-LFACT-v1 '
            '--enable-native-access=ALL-UNNAMED -Dfile.encoding=UTF-8 -Duser.timezone=UTC -cp ' + cp + ' '
            'dev.codex.schubert.nk.batch.file.NativeLegacyAdmissionNegative ' + str(RUN / 'watch.sock') + ' ' + str(BASE / 'case-cohort-v1') + '\n'
            'ReadWritePaths=' + str(BASE) + ' ' + str(RUN) + '\nTimeoutStartSec=120s\nTimeoutStopSec=10s\nRestart=no\nSendSIGKILL=no\n')
    with DROP.open('x') as file:
        file.write(text); file.flush(); os.fsync(file.fileno())
    DROP.chmod(0o644)
    command(['systemctl', 'daemon-reload'])
    require(unit()['MainPID'] == '0')
    save('setup.safe.json', {'actualExit': 0, 'boot': BOOT, 'source': SOURCE, 'archiveSha256': archive_sha, 'inputSha256': input_sha,
                            'approvalOriginalSha256': ORIGINAL_APPROVAL, 'badVectorSha256': hashlib.sha256(BAD).hexdigest(),
                            'unitDropinSha256': sha(DROP), 'normalMorningIssued': False, 'formalAccepted': False})


class Watch:
    def __init__(self, paths):
        self.lib = ctypes.CDLL(None, use_errno=True)
        self.lib.inotify_init1.argtypes = [ctypes.c_int]; self.lib.inotify_init1.restype = ctypes.c_int
        self.lib.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]; self.lib.inotify_add_watch.restype = ctypes.c_int
        self.fd = self.lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC); require(self.fd >= 0)
        self.paths = {}
        for path in paths:
            wd = self.lib.inotify_add_watch(self.fd, os.fsencode(path), 0xFFF)
            require(wd >= 0 and wd not in self.paths); self.paths[wd] = str(path)

    def read(self):
        events = []
        while select.select([self.fd], [], [], 0)[0]:
            data = os.read(self.fd, 65536); offset = 0
            while offset < len(data):
                wd, mask, cookie, length = struct.unpack_from('iIII', data, offset); offset += 16 + length
                require(wd in self.paths and not mask & 0xC000)
                events.append((self.paths[wd], mask))
        return events

    def close(self):
        os.close(self.fd)


class Bus:
    def __init__(self):
        self.events = queue.Queue(); self.serial = 0
        self.out = (RESULTS / 'bus.private.jsonl').open('x', buffering=1)
        self.err = (RESULTS / 'bus.private.err').open('x')
        self.process = subprocess.Popen(['busctl', '--system', '--json=short', "--match=type='method_call',interface='org.freedesktop.systemd1.Manager'", 'monitor'], stdout=subprocess.PIPE, stderr=self.err, text=True, bufsize=1)
        self.thread = threading.Thread(target=self.collect, daemon=True); self.thread.start()

    def collect(self):
        for line in self.process.stdout:
            self.out.write(line)
            try: self.events.put(json.loads(line))
            except ValueError: self.events.put({'invalid': True})

    def barrier(self):
        self.serial += 1; name = 'pgpt3216-barrier-' + str(self.serial).zfill(4) + '.service'
        # Monitor readiness is witnessed, never assumed from Popen or a sleep.
        until = time.monotonic() + 5; observed = []
        while time.monotonic() < until:
            require(self.process.poll() is None)
            command(['busctl', '--system', '--timeout=2', 'call', 'org.freedesktop.systemd1', '/org/freedesktop/systemd1', 'org.freedesktop.systemd1.Manager', 'GetUnit', 's', name], allowed=(1,))
            try:
                while True:
                    item = self.events.get(timeout=.1); require(item.get('type') == 'method_call')
                    observed.append(item)
                    if item.get('member') == 'GetUnit' and item.get('payload', {}).get('data') == [name]: return observed
            except queue.Empty: pass
        raise ValueError('live independent bus barrier unavailable')

    def close(self):
        if self.process.poll() is None: self.process.terminate()
        self.process.wait(timeout=5); self.thread.join(timeout=5)
        require(not self.thread.is_alive()); self.process.stdout.close(); self.out.close(); self.err.close()


def stable_bad():
    s = APPROVAL.lstat()
    require(stat.S_ISREG(s.st_mode) and s.st_uid == s.st_gid == 0 and stat.S_IMODE(s.st_mode) == 0o400 and s.st_nlink == 1 and APPROVAL.read_bytes() == BAD)
    return [s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid, s.st_size, s.st_mtime_ns]


def resource_closed(pid, before):
    keys = {(v[0], v[1]) for v in before.values()}
    for fd in (Path('/proc') / str(pid) / 'fd').iterdir():
        try: s = fd.stat()
        except FileNotFoundError: continue
        require((s.st_dev, s.st_ino) not in keys)
    # No M/A/OFD lock may escape a refused factory callback.
    inodes = {int(v[1]) for name, v in before.items() if name.endswith('.lock')}
    for line in Path('/proc/locks').read_text().splitlines():
        fields = line.split()
        require(not any(re.fullmatch(r'[0-9a-f]+:[0-9a-f]+:[0-9]+', v) and int(v.rsplit(':', 1)[1]) in inodes for v in fields))


def execute():
    guard(); require(json.loads((RESULTS / 'setup.safe.json').read_text())['actualExit'] == 0)
    require(not (RESULTS / 'run-reservation.safe.json').exists() and not NATIVE.exists())
    initial_unit = unit(); require(initial_unit['MainPID'] == '0' and initial_unit['Job'] == '' and initial_unit['ActiveState'] == 'inactive')
    before = {'tree': tree(), 'database': database(), 'bad': stable_bad()}; save('before.private.json', before)
    save('run-reservation.safe.json', {'issuedOnce': True, 'boot': BOOT, 'expectedCases': IDS, 'businessEntry': False})
    watch = Watch([APPROVAL, Path('/etc/schubert-nk/credentials/db-batch'), Path('/etc/schubert-nk/credentials/mq-ops')])
    bus = Bus(); server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); server.settimeout(30)
    server.bind(str(RUN / 'watch.sock')); os.chmod(RUN / 'watch.sock', 0o600); server.listen(1)
    try:
        bus.barrier()
        command(['systemctl', 'start', '--no-block', UNIT])  # Sole isolated harness start, never a business main.
        conn, _ = server.accept(); conn.settimeout(20)
        with conn:
            pid, uid, gid = struct.unpack('3i', conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            require(uid == gid == 0 and pid > 1)
            ticks = (Path('/proc') / str(pid) / 'stat').read_text().rpartition(')')[2].split()[19]
            def same_peer():
                guard(); value = unit()
                require(value['MainPID'] == str(pid) and value['ControlPID'] == '0' and value['ActiveState'] in ['activating', 'active'] and value['SubState'] in ['start', 'running']
                        and value['ControlGroup'] == '/system.slice/' + UNIT and re.fullmatch(r'(?!0{32}$)[a-f0-9]{32}', value['InvocationID']) is not None)
                require((Path('/proc') / str(pid) / 'stat').read_text().rpartition(')')[2].split()[19] == ticks)
                require((Path('/proc') / str(pid) / 'cgroup').read_text() == '0::/system.slice/' + UNIT + '\n')
                return value
            invocation = same_peer()['InvocationID']
            wire = conn.makefile('rw', encoding='ascii', buffering=1)
            def receive(expected): require(wire.readline(512).rstrip('\n') == expected)
            def send(value): wire.write(value + '\n'); wire.flush()
            receive('HELLO|' + str(pid) + '|' + BOOT); send('READY')
            results = []
            for test_id in IDS:
                receive('BEGIN|' + test_id); require(same_peer()['InvocationID'] == invocation)
                require(stable_bad() == before['bad'] and tree() == before['tree'])
                bus.barrier(); watch.read()  # Discard observer's own pre-case reads BEFORE arming.
                send('ARMED|' + test_id)
                receive('END|' + test_id)
                events = watch.read()  # Inspect actual case events BEFORE our next hash/read.
                require(any(path == str(APPROVAL) and mask & 1 for path, mask in events))
                require(all(path == str(APPROVAL) and not mask & (2 | 4 | 8 | 64 | 128 | 256 | 512 | 1024 | 2048) for path, mask in events))
                methods = bus.barrier()
                require(all(item['member'] in ['GetUnit', 'GetUnitByPID', 'Subscribe', 'Unsubscribe'] for item in methods))
                require(same_peer()['InvocationID'] == invocation and stable_bad() == before['bad'])
                resource_closed(pid, before['tree']); require(tree() == before['tree'] and database() == before['database'])
                item = {'testId': test_id, 'actualExit': 0, 'approvalAccessObserved': True, 'credentialReadEvents': 0,
                        'unsafeManagerCalls': 0, 'protectedFileDescriptorOrLock': 0, 'all24AndHistoryUnchanged': True,
                        'noAppDbClientOrAdvisory': True, 'samePeerInvocation': True, 'formalAccepted': False}
                save(test_id + '.observer.safe.json', item); results.append(item); send('ACCESSED|' + test_id)
            receive('COMPLETE|7'); require(len(results) == 7); send('SEALED|7'); wire.close()
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            terminal = unit()
            if terminal['MainPID'] == '0' and terminal['ControlPID'] == '0' and terminal['Job'] == '': break
            time.sleep(.1)
        require_terminal(terminal, invocation, RETAINED_TERMINAL)
        require(not Path('/proc', str(pid)).exists())
        if RETAINED_TERMINAL:
            # No live JVM remains. This is a finite stop of this exact fixture
            # invocation, not Production Morning or a second business operation.
            group = Path('/sys/fs/cgroup/system.slice') / UNIT
            require(not group.exists() or not (group / 'cgroup.procs').read_text().strip())
            actual = command(['systemctl', 'show', UNIT, '-p', 'ExecStop', '-p', 'ExecStopPost', '-p', 'RemainAfterExit']).stdout
            require(dict(line.split('=', 1) for line in actual.splitlines()) == {'ExecStop': '', 'ExecStopPost': '', 'RemainAfterExit': 'yes'})
            require(unit() == terminal)
            save('owned-stop-reservation.safe.json', {'issuedOnce': True, 'invocation': invocation, 'pidGone': pid, 'unit': UNIT})
            command(['systemctl', 'stop', UNIT], timeout=15)
            stopped = unit()
            require(stopped['ActiveState'] == 'inactive' and stopped['SubState'] == 'dead' and stopped['MainPID'] == stopped['ControlPID'] == '0' and stopped['Job'] == '')
            require(not group.exists() or not (group / 'cgroup.procs').read_text().strip())
            save('owned-stop.safe.json', {'actualExit': 0, 'invocation': invocation, 'actorAndJobEmpty': True})
        require(tree() == before['tree'] and database() == before['database'] and stable_bad() == before['bad'])
        require(json.loads((CASE / 'complete.safe.json').read_text())['actualExit'] == 0)
        require(NATIVE.stat().st_size > 0)
        save('manifest.safe.json', {'actualExit': 0, 'cases': 7, 'boot': BOOT, 'source': SOURCE, 'pid': pid, 'ticks': int(ticks),
                                   'invocation': invocation, 'naturalUnitExit': 0, 'all24AndHistoryUnchanged': True,
                                   'protectedTreeUnchanged': True, 'nativeSha256': sha(NATIVE),
                                   'normalBusinessEntryCount': 0, 'formalAccepted': False})
        print('PG3216_NEGATIVE actual0=true cases7=true independentWitness=true nativeNotYetQualified=true', flush=True)
    except Exception as failure:
        save('failed.safe.json', {'actualExit': 1, 'type': type(failure).__name__, 'casesPassed': len(list(RESULTS.glob('*.observer.safe.json'))), 'nativeAccepted': False})
        raise
    finally:
        server.close(); watch.close(); bus.close()


def require_terminal(terminal, invocation, retained):
    require(terminal['Result'] == 'success' and terminal['ExecMainCode'] == '1' and terminal['ExecMainStatus'] == '0'
            and terminal['MainPID'] == terminal['ControlPID'] == '0' and terminal['Job'] == '')
    require((terminal['ActiveState'], terminal['SubState']) == (('active', 'exited') if retained else ('inactive', 'dead')))
    if retained: require(terminal['InvocationID'] == invocation)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['setup', 'execute'])
    parser.add_argument('--archive-sha'); parser.add_argument('--input-sha'); args = parser.parse_args()
    if args.phase == 'setup': setup(args.archive_sha, args.input_sha)
    else: execute()


if __name__ == '__main__':
    main()
