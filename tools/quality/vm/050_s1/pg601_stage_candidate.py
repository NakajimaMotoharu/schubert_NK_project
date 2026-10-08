"""Place signed unused PG600 only; current/approval/permit/DB/Units unchanged."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from pg601_stage_contract import check_members
from pg548_candidate_contract import artifacts

T = Path('/home/mini/codex/project1/work/pgpt-foundation')
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P = Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE = '23b14a44b10504172e030bbd6625926bf049fb5c'
DIGEST = 'a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f'
RELEASE = W / 'pg600-release-v1'

PAYLOAD = r'''
import datetime,grp,hashlib,json,os,pathlib,stat,subprocess,tarfile
assert os.geteuid()==0
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
current=pathlib.Path('/opt/schubert-nk/current');old=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG548')
assert current.readlink()==old
assert hashlib.sha256((old/'RELEASE-MANIFEST.json').read_bytes()).hexdigest()=='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b'
assert not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf').exists()
units=('caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service')
def terminal():
 for unit in units:
  raw=subprocess.check_output(['systemctl','show',unit,'--property=Id,LoadState,MainPID,ControlPID,Job'],text=True)
  assert dict(l.split('=',1)for l in raw.splitlines())=={'Id':unit,'LoadState':'loaded','MainPID':'0','ControlPID':'0','Job':''}
  cg=pathlib.Path('/sys/fs/cgroup/system.slice')/unit
  if cg.exists():
   for p in (cg/'cgroup.procs',*cg.rglob('cgroup.procs')):assert not p.read_text().strip()
terminal()
root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG600')
stage=pathlib.Path('/home/ubuntu/pg601-stage-v1')
sig=pathlib.Path('/var/lib/pgpt-s1-preservation/pg600-manifest.sig')
assert not os.path.lexists(root)and not os.path.lexists(sig)
archive=stage/'pg601-release-v1.tar';signature=stage/'pg600-manifest-v1.sig'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==TARHASH
signature_bytes=signature.read_bytes();assert len(signature_bytes)==64 and hashlib.sha256(signature_bytes).hexdigest()==SIGHASH
policy={};exec(compile(CONTRACT,'<pinned closed archive policy>','exec'),policy)
with tarfile.open(archive,'r:')as tar:
 raw=tar.extractfile('RELEASE-MANIFEST.json').read();assert hashlib.sha256(raw).hexdigest()==DIGEST
 data=json.loads(raw);assert data['source']['commit']==SOURCE and data['release']=='0.1.0-PG600'and data['versions']['schema']=='028'
 assert len(data['artifacts'])==187 and len(data['migrations'])==29
 sums={row['path']:row['sha256']for row in data['artifacts']};assert len(sums)==187
 sums['RELEASE-MANIFEST.json']=DIGEST
 canonical=''.join(sums[name]+'  '+name+'\n'for name in sorted(sums)).encode('ascii')
 assert tar.extractfile('SHA256SUMS').read()==canonical
 policy['check_members'](tar.getmembers(),set(sums)|{'SHA256SUMS'})
 for row in data['artifacts']:
  value=tar.extractfile(row['path']).read();assert len(value)==row['size']and hashlib.sha256(value).hexdigest()==row['sha256']
 root.mkdir(mode=0o750);tar.extractall(root,filter='data')
group=grp.getgrnam('schubert').gr_gid;assert group==986
expected=set(sums)|{'SHA256SUMS'}
assert {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==expected
for p in (root,*root.rglob('*')):
 s=p.lstat();assert not p.is_symlink()and(stat.S_ISDIR(s.st_mode)or(stat.S_ISREG(s.st_mode)and s.st_nlink==1))
 executable=p.relative_to(root).as_posix()in('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
 os.chown(p,0,group);os.chmod(p,0o750 if p.is_dir()or executable else 0o640)
 if p.is_file():
  with p.open('rb')as f:os.fsync(f.fileno())
for row in data['artifacts']:
 p=root/row['path'];assert p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
assert(root/'SHA256SUMS').read_bytes()==canonical
with sig.open('xb')as f:
 os.fchmod(f.fileno(),0o400);f.write(signature_bytes);f.flush();os.fsync(f.fileno())
subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(root/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for p in sorted((q for q in root.rglob('*')if q.is_dir()),key=lambda q:len(q.parts),reverse=True):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
for p in(root,root.parent,sig.parent):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
terminal();assert current.readlink()==old
print('PG601_UNUSED_CANDIDATE_PLACED artifacts187=true signatureVerified=true currentUnchanged=true businessActions0=true')
'''


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=T) == b''
    operator = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip()
    raw = (RELEASE / 'RELEASE-MANIFEST.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == DIGEST
    data = json.loads(raw); rows = artifacts(data['artifacts'])
    for name, row in rows.items():
        p = RELEASE / name
        assert not p.is_symlink() and p.stat().st_size == row['size'] and hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256']
    bundle = P / 'pg601-release-v1.tar'; signature = P / 'pg600-manifest-v1.sig'
    log = W / 'pg601-candidate-stage-v1.private.log'
    assert not bundle.exists() and not log.exists()
    with tarfile.open(bundle, 'x:') as tar:
        for p in sorted(RELEASE.rglob('*')):
            assert not p.is_symlink()
            tar.add(p, arcname=p.relative_to(RELEASE).as_posix(), recursive=False)
    with tarfile.open(bundle, 'r:') as tar:
        check_members(tar.getmembers(), set(rows) | {'RELEASE-MANIFEST.json', 'SHA256SUMS'})
    opts = ['-i', str(P / 'vm-access'), '-oBatchMode=yes', '-oIdentitiesOnly=yes',
            '-oStrictHostKeyChecking=yes', '-oUserKnownHostsFile=' + str(P / 'known_hosts')]
    ssh = ['ssh', *opts, '-p', '22222', 'ubuntu@127.0.0.1']
    scp = ['scp', *opts, '-P', '22222']
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('xb') as f:
        subprocess.run(ssh + ['test ! -e /home/ubuntu/pg601-stage-v1 && sudo -n test ! -e /opt/schubert-nk/releases/0.1.0-PG600 && sudo -n test ! -e /var/lib/pgpt-s1-preservation/pg600-manifest.sig && mkdir -m 700 /home/ubuntu/pg601-stage-v1'], stdout=f, stderr=f, check=True)
        subprocess.run(scp + [str(bundle), str(signature), 'ubuntu@127.0.0.1:/home/ubuntu/pg601-stage-v1/'], stdout=f, stderr=f, check=True)
        prefix = 'SOURCE=' + repr(SOURCE) + '\nDIGEST=' + repr(DIGEST) + '\n'
        prefix += 'TARHASH=' + repr(hashlib.sha256(bundle.read_bytes()).hexdigest()) + '\n'
        prefix += 'SIGHASH=' + repr(hashlib.sha256(signature.read_bytes()).hexdigest()) + '\n'
        prefix += 'CONTRACT=' + repr((Path(__file__).parent / 'pg601_stage_contract.py').read_text()) + '\n'
        result = subprocess.run(ssh + ['sudo -n python3 -B -'], input=(prefix + PAYLOAD).encode(), stdout=f, stderr=f)
        f.flush(); os.fsync(f.fileno())
    witness = b'PG601_UNUSED_CANDIDATE_PLACED artifacts187=true signatureVerified=true currentUnchanged=true businessActions0=true\n'
    if result.returncode == 0: assert log.read_bytes() == witness
    safe = {'run': 'PG601-candidate-stage-v1', 'actualExit': result.returncode,
            'candidateSource': SOURCE, 'operatorSource': operator, 'manifestSha256': DIGEST,
            'startedUTC': started, 'completedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'privateLogSha256': hashlib.sha256(log.read_bytes()).hexdigest(),
            'helperSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'currentUnchanged': result.returncode == 0, 'candidateOnly': True,
            'activationNotRun': True, 'formalAccepted': False}
    with (W / 'pg601-candidate-stage-v1.safe.json').open('x') as f:
        json.dump(safe, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'actualExit': result.returncode, 'unusedCandidateOnly': True,
                      'currentUnchangedVerified': result.returncode == 0, 'formalAccepted': False}))
    raise SystemExit(result.returncode)


if __name__ == '__main__': main()
