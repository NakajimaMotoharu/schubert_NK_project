"""SS343/SSC165/174 isolated reboot: preserve existing chain, no business replay.

PT-OPS-2200-001/002, QA047/QA052. Execute on the dedicated LAN server only.
Old current-boot owned stop/native acceptance is NOT inferred from power loss.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

BASE = Path('/home/mini/schubert-nk-pgpt')
OLD = BASE/'vm/pg1435-cold-v1/active.qcow2'
BACKING = BASE/'vm/pg1431/guest.qcow2'
OUT = BASE/'vm/pg2200-outage-cold-v1'
SOURCE = '3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'
APPEND = ('root=UUID=92978eec-7925-481e-8629-5b963d59ced1 ro console=ttyS0 '
          'systemd.unit=basic.target systemd.wants=systemd-networkd.service '
          'systemd.wants=systemd-resolved.service systemd.wants=systemd-user-sessions.service '
          'systemd.wants=ssh.service systemd.wants=postgresql.service '
          'systemd.mask=timers.target systemd.mask=paths.target '
          'systemd.mask=snapd.socket systemd.mask=lxd-installer.socket')


def identity(p):
    s=p.stat()
    return [s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,
            s.st_size,s.st_mtime_ns,s.st_ctime_ns]


def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(8*1024*1024):h.update(chunk)
    return h.hexdigest()


def save(name,value):
    with (OUT/name).open('x') as f:
        json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(OUT,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


def require_idle():
    assert os.geteuid()==0
    assert not any(n.strip().startswith('qemu-system') for n in
                   subprocess.check_output(['ps','-eo','comm='],text=True).splitlines())
    assert not subprocess.check_output(['ss','-H','-lnt','( sport = :22222 )'])
    for p in [OLD,BACKING]:
        assert subprocess.run(['lsof','-t',str(p)],capture_output=True).returncode==1
        assert p.is_file() and not p.is_symlink() and p.stat().st_nlink==1
    v=os.statvfs(BASE)
    assert v.f_bavail*v.f_frsize>20*1024**3


def arguments():
    return ['/usr/bin/qemu-system-x86_64','-name','pgpt-lan-cold-2201',
        '-machine','q35,accel=kvm','-cpu','host','-smp','4','-m','8192',
        '-L','/usr/share/qemu','-bios','/usr/share/seabios/bios-256k.bin',
        '-kernel',str(BASE/'tools/vmlinuz'),'-initrd',str(BASE/'tools/initrd'),
        '-append',APPEND,'-drive',f'file={OUT}/active.qcow2,if=virtio,format=qcow2',
        '-drive',f'file={BASE}/tools/seed.iso,media=cdrom,readonly=on',
        '-netdev','user,id=pgptnet,hostfwd=tcp:127.0.0.1:22222-:22',
        '-device','virtio-net-pci,netdev=pgptnet,romfile=','-vga','none',
        '-display','none','-monitor','none',
        '-qmp',f'unix:{OUT}/qmp.sock,server=on,wait=off',
        '-serial',f'file:{OUT}/console.private.log',
        '-pidfile',str(OUT/'qemu.pid'),'-daemonize']


def preserve():
    require_idle();OUT.mkdir(mode=0o700)
    before={str(p):{'identity':identity(p),'sha256':digest(p)} for p in [OLD,BACKING]}
    chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(OLD)]))
    assert len(chain)==2 and [x['filename'] for x in chain]==[str(OLD),str(BACKING)]
    assert all(x['format']=='qcow2' and not x.get('dirty-flag') and
               not x.get('snapshots') and not x['format-specific']['data'].get('corrupt') for x in chain)
    assert chain[0]['virtual-size']==48*1024**3 and chain[1]['virtual-size']==40*1024**3
    save('before.safe.json',{'source':SOURCE,'chain':before,'information':chain,
         'lanBoot':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
         'oldShutdownNormalProven':False,'oldOwnedStopAccepted':False})
    subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(OLD),str(OUT/'active.qcow2')],check=True)
    with (OUT/'compare.private.log').open('xb') as f:
        r=subprocess.run(['qemu-img','compare','-q','-f','qcow2','-F','qcow2',str(OLD),str(OUT/'active.qcow2')],stdout=f,stderr=f)
    require_idle()
    assert r.returncode==0 and all(identity(Path(p))==v['identity'] and digest(Path(p))==v['sha256'] for p,v in before.items())
    save('manifest.safe.json',{'actualExit':0,'logicalCompareExit':r.returncode,'source':SOURCE,
         'chain':before,'newOverlaySha256':digest(OUT/'active.qcow2'),
         'oldRAMRestored':False,'oldRunRestored':False,'businessActions':0,
         'oldStopNativeAccepted':False,'formalAccepted':False})
    print('PG2200_PRESERVED actualExit=0 oldStopNativeAccepted=false')


def boot():
    require_idle()
    proof=json.loads((OUT/'manifest.safe.json').read_bytes())
    assert proof['actualExit']==proof['logicalCompareExit']==0 and proof['source']==SOURCE
    assert all(identity(Path(p))==v['identity'] for p,v in proof['chain'].items())
    assert digest(OUT/'active.qcow2')==proof['newOverlaySha256']
    for n in ['boot-reservation.safe.json','boot-result.safe.json','qmp.sock','qemu.pid','console.private.log']:
        assert not (OUT/n).exists()
    args=arguments()
    save('boot-reservation.safe.json',{'issuedOnce':True,'args':args,'source':SOURCE,
         'oldRunPermitRestored':False,'businessStartIssued':False,'toolSha256':digest(Path(__file__))})
    with (OUT/'launch.private.log').open('xb') as f:r=subprocess.run(args,stdout=f,stderr=f)
    stable=all(identity(Path(p))==v['identity'] for p,v in proof['chain'].items())
    save('boot-result.safe.json',{'actualExit':r.returncode,'oldChainStable':stable,
         'guestPid':int((OUT/'qemu.pid').read_text()) if (OUT/'qemu.pid').exists() else None,
         'guestReauthenticationPending':True,'oldStopNativeAccepted':False,'formalAccepted':False})
    assert r.returncode==0 and stable
    print('PG2201_ISOLATED_BOOT actualExit=0 businessAccepted=false')


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['preserve','boot']);a=p.parse_args()
    os.umask(0o077)
    with (BASE/'vm/boot-guard.lock').open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        (preserve if a.phase=='preserve' else boot)()


if __name__=='__main__':main()
