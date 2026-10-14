"""PT-OPS-2810: new-only COW resume of the normally stopped three-layer PGPT VM.

SS343/SSC165174/QA047. Server root only. No old RAM, /run, permit or business replay.
Old images/logs/receipts remain untouched; source042 authority is reauthenticated in guest later.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

BASE=Path('/home/mini/schubert-nk-pgpt')
CHAIN=[BASE/'vm/pg2200-outage-cold-v1/active.qcow2',BASE/'vm/pg1435-cold-v1/active.qcow2',BASE/'vm/pg1431/guest.qcow2']
OUT=BASE/'vm/pg2810-network-resume-cold-v1'
SOURCE='04207efc3ad78bca75942153a90c70985064c988'
TOOLS={'vmlinuz':'7efd88a7facf80874d781ccb2c2421f0aaaa575e3b94760430619e826f490117',
       'initrd':'9a384a0b0b81fd50c2cb47d2f94f6ce26006d3cf68564f444b21f0e266bb9eb8',
       'seed.iso':'3d0bf8036b27f80fe18432663c5bb1cb1bbcf0403b506ec577c8aa76e04b6106'}
APPEND=('root=UUID=92978eec-7925-481e-8629-5b963d59ced1 ro console=ttyS0 '
        'systemd.unit=basic.target systemd.wants=systemd-networkd.service '
        'systemd.wants=systemd-resolved.service systemd.wants=systemd-user-sessions.service '
        'systemd.wants=ssh.service systemd.wants=postgresql.service '
        'systemd.mask=timers.target systemd.mask=paths.target '
        'systemd.mask=snapd.socket systemd.mask=lxd-installer.socket')


def require(value):
    if not value:raise ValueError('new-only normal-shutdown cold resume refused')


def identity(p):
    s=p.stat();return [s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]


def digest(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        while chunk:=f.read(8*1024*1024):h.update(chunk)
    return h.hexdigest()


def save(name,value):
    with(OUT/name).open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(OUT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)


def validate_chain(chain):
    require(type(chain)is list and len(chain)==3 and [v['filename']for v in chain]==[str(p)for p in CHAIN])
    require(all(v['format']=='qcow2'and not v.get('dirty-flag')and not v.get('snapshots')and not v['format-specific']['data'].get('corrupt')for v in chain))
    require([v['virtual-size']for v in chain]==[48*1024**3,48*1024**3,40*1024**3])


def idle():
    require(os.geteuid()==0)
    require(not any(n.strip().startswith('qemu-system')for n in subprocess.check_output(['ps','-eo','comm='],text=True).splitlines()))
    require(not subprocess.check_output(['ss','-H','-lnt','( sport = :22222 )']))
    for p in CHAIN:
        require(p.is_file()and not p.is_symlink()and p.stat().st_nlink==1)
        require(subprocess.run(['lsof','-t',str(p)],capture_output=True).returncode==1)
    require(os.statvfs(BASE).f_bavail*os.statvfs(BASE).f_frsize>20*1024**3)
    for n,h in TOOLS.items():require(digest(BASE/'tools'/n)==h)


def arguments():
    return ['/usr/bin/qemu-system-x86_64','-name','pgpt-lan-network-resume-2810','-machine','q35,accel=kvm','-cpu','host','-smp','4','-m','8192',
        '-L','/usr/share/qemu','-bios','/usr/share/seabios/bios-256k.bin','-kernel',str(BASE/'tools/vmlinuz'),'-initrd',str(BASE/'tools/initrd'),
        '-append',APPEND,'-drive',f'file={OUT}/active.qcow2,if=virtio,format=qcow2','-drive',f'file={BASE}/tools/seed.iso,media=cdrom,readonly=on',
        '-netdev','user,id=pgptnet,hostfwd=tcp:127.0.0.1:22222-:22','-device','virtio-net-pci,netdev=pgptnet,romfile=',
        '-vga','none','-display','none','-monitor','none','-qmp',f'unix:{OUT}/qmp.sock,server=on,wait=off',
        '-serial',f'file:{OUT}/console.private.log','-pidfile',str(OUT/'qemu.pid'),'-daemonize']


def preserve():
    idle();OUT.mkdir(mode=0o700)
    chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(CHAIN[0])]))
    validate_chain(chain)
    before={str(p):{'identity':identity(p),'sha256':digest(p)}for p in CHAIN}
    save('before.safe.json',{'source':SOURCE,'chain':before,'information':chain,'lanBoot':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'oldShutdownNormalExternalRecord':'PMO/vm-shutdown-20261014.json','oldRunPermitReused':False,'oldNativeAuthorityTransferred':False})
    with(OUT/'create.private.log').open('xb')as f:
        created=subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(CHAIN[0]),str(OUT/'active.qcow2')],stdout=f,stderr=f)
    require(created.returncode==0)
    with(OUT/'compare.private.log').open('xb')as f:
        compared=subprocess.run(['qemu-img','compare','-q','-f','qcow2','-F','qcow2',str(CHAIN[0]),str(OUT/'active.qcow2')],stdout=f,stderr=f)
    idle();require(compared.returncode==0 and all(identity(Path(p))==v['identity']and digest(Path(p))==v['sha256']for p,v in before.items()))
    save('manifest.safe.json',{'actualExit':0,'logicalCompareExit':0,'source':SOURCE,'chain':before,'newOverlaySha256':digest(OUT/'active.qcow2'),
        'oldRAMRestored':False,'oldRunRestored':False,'businessActions':0,'oldNativeAuthorityTransferred':False,'formalAccepted':False})
    print('PG2810_PRESERVED actualExit=0 threeOldLayersUnchanged=true newOnlyOverlay=true')


def boot():
    idle();proof=json.loads((OUT/'manifest.safe.json').read_bytes())
    require(proof['actualExit']==proof['logicalCompareExit']==0 and proof['source']==SOURCE)
    require(set(proof['chain'])=={str(p)for p in CHAIN}and all(identity(Path(p))==v['identity']and digest(Path(p))==v['sha256']for p,v in proof['chain'].items()))
    require(digest(OUT/'active.qcow2')==proof['newOverlaySha256'])
    require(all(not os.path.lexists(OUT/n)for n in ['boot-reservation.safe.json','boot-result.safe.json','qmp.sock','qemu.pid','console.private.log','launch.private.log']))
    args=arguments();save('boot-reservation.safe.json',{'issuedOnce':True,'args':args,'source':SOURCE,'oldRunPermitRestored':False,'businessStartIssued':False,'toolSha256':digest(Path(__file__))})
    with(OUT/'launch.private.log').open('xb')as f:result=subprocess.run(args,stdout=f,stderr=f)
    stable=all(identity(Path(p))==v['identity']for p,v in proof['chain'].items())
    pid=int((OUT/'qemu.pid').read_text())if(OUT/'qemu.pid').exists()else None
    observed={}
    if pid is not None and Path('/proc',str(pid)).exists():
        p=Path('/proc',str(pid));observed={'pid':pid,'ticks':int((p/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':digest(p/'cmdline')}
    save('boot-result.safe.json',{'actualExit':result.returncode,'oldChainStable':stable,'guestProcess':observed,'guestReauthenticationPending':True,'oldRunNativeAuthorityTransferred':False,'formalAccepted':False})
    require(result.returncode==0 and stable and observed)
    print(json.dumps({'actualExit':0,'guestProcess':observed,'guestReauthenticationPending':True,'businessAccepted':False}))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['preserve','boot']);phase=parser.parse_args().phase
    os.umask(0o077)
    fd=os.open(BASE/'vm/boot-guard.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        s=os.fstat(fd);require(stat.S_ISREG(s.st_mode)and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1)
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        (preserve if phase=='preserve'else boot)()
    finally:os.close(fd)


if __name__=='__main__':main()
