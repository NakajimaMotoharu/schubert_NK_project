"""SSC276 current full read-only 24/187/Backup/native and exact retained pair."""
import ast
import datetime
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from pg1446_current_cold_stage import W, P, SSH
from pg1724_retained_host_gate import queued_gate
from pg2960_retained_resume_readonly import host_owner
from pg1991_fresh_runtime_partial_full_proof import helpers as old_helpers
from pg2940_current_resume_before import payload as current_post
import pg1257_fresh_independent_terminal_post as seal_schema

SLOT = 'pg2964-retained-full-pair-proof-v1'


def helpers():
    raw = old_helpers()
    for a, b in [('498727', '118988'), ('10276205', '1642675'), ('498725', '118986'), ('498758', '119019'), ('10276392', '1642861'), ('498756', '119017'), ('pg1980-fresh-resume-tools-v1', 'pg2950-current-cold-resume-tools-v1'), ('pg1980_native_refs.py', 'pg2950_native_refs.py'), ('pg1984-fresh-resume-preparation-v1', 'pg2954-current-cold-resume-preparation-v1')]:
        raw = raw.replace(a, b)
    raw = raw.replace('require(children == {119019})', 'require(children == (set() if REF_CLOSED else {119019}))')
    return raw


TAIL = r'''
failed=base/'pg2954-current-cold-resume-preparation-v1'
require({p.name for p in failed.iterdir()}=={'refs-prepare.private.log'})
require(hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest()=='f176d954ada998d12fec8a7227f66882d208aebce430f107823c36eeb123910e')
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').exists())
tool=base/'pg2950-current-cold-resume-tools-v1'
for name,digest in TOOL_HASHES.items():
 p=tool/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
a=pair();require(a==pair());locks=[owned_lock(n)for n in ['maintenance.lock','startup-admission.lock']]
save=base/'pg2964-retained-full-pair-proof-v1';require(not os.path.lexists(save));save.mkdir(mode=0o700)
value={'pair':a,'locks':locks,'native':native,'toolHashes':TOOL_HASHES,'all24And187OriginalBackupUnchanged':True,'runtimeDirectoryAbsent':True,'onlyOwnedPeerAndAdvisory':True,'signals0':True,'oldCloseUnknown':True}
encoded=json.dumps(value,sort_keys=True).encode()
with(save/'proof.private.json').open('xb')as f:os.fchmod(f.fileno(),0o600);f.write(encoded);f.flush();os.fsync(f.fileno())
for p in[save,base]:
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
print(json.dumps({'actualExit':0,'proofSha256':hashlib.sha256(encoded).hexdigest(),'parentPid':118988,'childPid':119019,'backendPid':119017,'parentFdCount':101,'childFdCount':4,'samePeer':True,'ownedLocks':2,'allOriginalValuesPreserved':True,'signals0':True,'formalAccepted':False}))
'''


def body():
    post = json.loads((W / 'pg2940-current-resume-before-v1/manifest.safe.json').read_bytes())
    if post['actualExit'] != 0:
        raise ValueError('qualified actual current before required')
    seals = {n: post['proofHashes'][n]['sha256'] for n in seal_schema.previous.SEALS}
    raw = current_post(seals)
    raw = raw[:raw.index("result = {'actualExit': 0")]
    old = "lines[-2:] == [b'0', b'0']"
    if raw.count(old) != 1:
        raise ValueError('one owned peer and advisory boundary')
    raw = raw.replace(old, "lines[-2:] == ([b'0', b'0'] if PEER_CLOSED else [b'1', b'1'])")
    start = raw.index("        for name in ('maintenance.lock', 'startup-admission.lock'):")
    end = raw.index("        require(tree(pathlib.Path('/run/systemd/system'))", start)
    raw = raw[:start] + "        if not PEER_CLOSED:\n            for name in ('maintenance.lock','startup-admission.lock'):owned_lock(name)\n" + raw[end:]
    marker = '\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker) != 1:
        raise ValueError('single whole metadata scope')
    raw = raw.replace(marker, '\n' + helpers() + '\n' + marker)
    cp = '/var/lib/pgpt-s1-preservation/pg2950-current-cold-resume-tools-v1:/opt/schubert-nk/releases/0.1.0-PG2802/operations/batch.jar:/opt/schubert-nk/releases/0.1.0-PG2802/operations/lib/*:/opt/schubert-nk/releases/0.1.0-PG2802/api/api.jar:/opt/schubert-nk/releases/0.1.0-PG2802/api/lib/*:/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/flyway-core-13.4.0.jar'
    argv = ['/opt/jdk-25.0.4/bin/java', '--enable-native-access=ALL-UNNAMED', '-cp', cp, 'Pg2950FreshResumePreparation', 'prepare-resume']
    receipt = (W / 'pg2890-network-owned-stop-tools-v1/pg2890_parent_receipt.py').read_text()
    header = 'PEER_CLOSED=False\nREF_CLOSED=False\nEXPECTED_ARGV=' + repr(b'\0'.join(x.encode() for x in argv) + b'\0') + '\nHASHES=' + repr(post['toolHashes']) + '\nRECEIPT=' + repr(receipt) + '\n'
    return header + raw


def payload():
    frozen = json.loads((W / 'pg2952-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit'] != 0:
        raise ValueError('actual frozen ABI required')
    raw = 'TOOL_HASHES=' + repr(frozen['fileHashes']) + '\n' + body() + TAIL
    if check(raw, '<whole current retained pair readonly>'):
        raise ValueError('all proof globals required')
    compile(raw, '<whole current retained pair readonly>', 'exec')
    return raw


def main():
    os.umask(0o077)
    out = W / SLOT
    out.mkdir(mode=0o700)
    raw = payload()
    (out / 'payload.private.py').write_text(raw)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with queued_gate(P / 'current-management-critical.lock', validate_owner=host_owner, require_completion=lambda: False):
        r = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=180)
    (out / 'stderr.private.log').write_bytes(r.stderr)
    (out / 'result.private.json').write_bytes(r.stdout)
    value = {'actualExit': r.returncode, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'startUTC': start, 'endUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'signals0': True, 'formalAccepted': False}
    if not r.returncode:
        value['guest'] = json.loads(r.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps(value))
    return r.returncode


if __name__ == '__main__':
    raise SystemExit(main())
