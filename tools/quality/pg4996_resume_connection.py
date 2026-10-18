"""Fresh owned forward after local reboot; original remote VM is never restarted."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import types
import lan_forward as forward
from lan_server import run
from pg3428_vm_candidate_preflight_readonly import HOST
from pg1446_current_cold_stage import P

OUT = P / 'pg4996-local-reboot-forward-v1'
REMOTE_BOOT = 'c7964823-c628-4ef2-99b5-07b0f0b62bba'


def process(pid):
    path = Path('/proc') / str(pid)
    return {'pid': pid,
            'ticks': int((path / 'stat').read_text().rsplit(')', 1)[1].split()[19]),
            'argvSha256': hashlib.sha256((path / 'cmdline').read_bytes()).hexdigest()}


def remote_identity():
    code, output = run(HOST, timeout=30)
    if code != 0:
        raise ValueError('original remote VM identity read failed; no boot fallback')
    value = json.loads(output)
    if value['boot'] != REMOTE_BOOT:
        raise ValueError('remote boot changed; existing VM contract not authenticated')
    return value


def save(name, value):
    record = dict(value)
    record['localBoot'] = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    record['parent'] = process(os.getpid())
    if name == 'running.safe.json':
        record['child'] = process(record['sshPid'])
        record['remote'] = remote_identity()
    with (OUT / name).open('x') as f:
        json.dump(record, f, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())


def qualify(value, boot, parent, child, listener):
    if (value.get('localBoot') != boot or value.get('parent') != parent
            or value.get('child') != child or value.get('forward') !=
            '127.0.0.1:22222->server127.0.0.1:22222'
            or value.get('miniOnly') is not True
            or value.get('guestPrivateKeyTransferred') is not False
            or ('pid=' + str(child['pid']) + ',') not in listener):
        raise ValueError('fresh exact forward owner, process generation and listener required')


def authenticate_host():
    value = json.loads((OUT / 'running.safe.json').read_bytes())
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    parent, child = process(value['parent']['pid']), process(value['child']['pid'])
    listener = subprocess.check_output(['ss', '-H', '-lntp', '( sport = :22222 )'], text=True)
    qualify(value, boot, parent, child, listener)
    if (OUT / 'closed.safe.json').exists() or remote_identity() != value['remote']:
        raise ValueError('owned forward already closed or original remote VM changed')


def execute(slot, raw, timeout=180):
    # Keep the existing read/write evidence transport, source and single gate;
    # replace only historical local-forward authentication with this fresh proof.
    import pg4900_current_admission_image as current
    authenticate_host()
    return types.FunctionType(current.transport.execute.__code__,
                              {**vars(current.transport), 'SOURCE': current.SOURCE})(slot, raw, timeout)


def main():
    remote_identity()
    return types.FunctionType(forward.main.__code__,
                              {**vars(forward), 'OUT': OUT, 'save': save})()


if __name__ == '__main__':
    main()
