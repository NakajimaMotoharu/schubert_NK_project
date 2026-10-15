"""Fresh actual negative cohort, no repeat old operation or failed-native import."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg3216_legacy_negative_dispatch as transport
from pg1446_current_cold_stage import W, P

ROOT = Path(__file__).resolve().parents[2]
OUT = W / 'pg3218-legacy-negative-v1'
STAGE = '/home/ubuntu/pg3218-legacy-negative-v1'
FILES = ['pg3216_legacy_negative_observer.py', 'pg3218_legacy_negative_retained.py']


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(); parser.add_argument('phase', choices=['stage', 'prepare', 'execute']); phase = parser.parse_args().phase
    transport.owners(); transport.OUT = OUT
    require = transport.require
    if phase == 'stage':
        require(not subprocess.check_output(['git', 'status', '--porcelain']))
        OUT.mkdir(mode=0o700)
        require(transport.guest('STAGE=' + repr(STAGE) + '\n' + transport.RECEIVER_PREP, 'reservation.private.log') == 0)
        files = [ROOT / 'tools/quality/vm/050_s1' / name for name in FILES]
        args = ['scp', '-q', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(P / 'known_hosts'), '-o', 'HostKeyAlias=[127.0.0.1]:22222', '-i', str(P / 'vm-access'), '-P', '22224', *map(str, files), 'ubuntu@127.0.0.1:' + STAGE + '/']
        with (OUT / 'copy.private.log').open('xb') as log: copied = subprocess.run(args, stdout=log, stderr=log, timeout=30)
        require(copied.returncode == 0)
        hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        code = 'import hashlib\np=Path(' + repr(STAGE) + ')\nhashes=' + repr(hashes) + '\n'
        code += 'assert {x.name for x in p.iterdir()}==set(hashes)\nfor name,digest in hashes.items():\n x=p/name;assert hashlib.sha256(x.read_bytes()).hexdigest()==digest;os.chown(x,0,0);x.chmod(0o400)\nos.chown(p,0,0);p.chmod(0o700)\n'
        require(transport.guest(code, 'seal.private.log') == 0)
        transport.save('stage.safe.json', {'actualExit': 0, 'hashes': hashes, 'boot': transport.BOOT, 'operatorSource': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()})
    else:
        proof = json.loads((OUT / 'stage.safe.json').read_text()); require(proof['actualExit'] == 0 and proof['boot'] == transport.BOOT)
        code = 'import hashlib\np=Path(' + repr(STAGE) + ')\nhashes=' + repr(proof['hashes']) + '\n'
        code += 'for name,digest in hashes.items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest\n'
        code += 'os.execv("/usr/bin/python3",' + repr(['python3', '-B', STAGE + '/pg3218_legacy_negative_retained.py', phase]) + ')\n'
        actual = transport.guest(code, phase + '.private.log', timeout=180)
        transport.save(phase + '.safe.json', {'actualExit': actual, 'formalAccepted': False}); require(actual == 0)
    print('PG3218_' + phase.upper() + ' actual0=true formal=false', flush=True)


if __name__ == '__main__':
    main()
