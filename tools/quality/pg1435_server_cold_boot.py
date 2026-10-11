"""New-only server COW boot using the existing PG1001 management isolation flags.

Runs through mini sudo on the dedicated server. Retains qualified transferred
guest and original host chain. No old RAM, /run, permit, unit start or migration.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

BASE=Path('/home/mini/schubert-nk-pgpt')
DISK=BASE/'vm/pg1431/guest.qcow2'
OUT=BASE/'vm/pg1435-cold-v1'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while part:=f.read(8*1024*1024):h.update(part)
    return h.hexdigest()


def identity(path):
    value=path.stat()
    return [value.st_dev,value.st_ino,value.st_mode,value.st_uid,value.st_gid,
            value.st_nlink,value.st_size,value.st_mtime_ns,value.st_ctime_ns]


def write(name, value):
    with (OUT/name).open('x') as f:
        json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())


def arguments():
    return ['/usr/bin/qemu-system-x86_64','-name','pgpt-lan-cold','-machine','q35,accel=kvm',
        '-cpu','host','-smp','4','-m','8192','-L','/usr/share/qemu','-bios','/usr/share/seabios/bios-256k.bin',
        '-kernel',str(BASE/'tools/vmlinuz'),'-initrd',str(BASE/'tools/initrd'),
        '-append','root=UUID=92978eec-7925-481e-8629-5b963d59ced1 ro console=ttyS0 systemd.unit=basic.target systemd.wants=systemd-networkd.service systemd.wants=systemd-resolved.service systemd.wants=systemd-user-sessions.service systemd.wants=ssh.service systemd.wants=postgresql.service systemd.mask=timers.target systemd.mask=paths.target systemd.mask=snapd.socket systemd.mask=lxd-installer.socket',
        '-drive',f'file={OUT}/active.qcow2,if=virtio,format=qcow2',
        '-drive',f'file={BASE}/tools/seed.iso,media=cdrom,readonly=on',
        '-netdev','user,id=pgptnet,hostfwd=tcp:127.0.0.1:22222-:22',
        '-device','virtio-net-pci,netdev=pgptnet,romfile=','-vga','none','-display','none','-monitor','none',
        '-qmp',f'unix:{OUT}/qmp.sock,server=on,wait=off','-serial',f'file:{OUT}/console.private.log',
        '-pidfile',str(OUT/'qemu.pid'),'-daemonize']


def main():
    os.umask(0o077)
    assert os.geteuid()==0
    guard=BASE/'vm/boot-guard.lock'
    with guard.open('a') as locked:
        fcntl.flock(locked,fcntl.LOCK_EX|fcntl.LOCK_NB)
        names=subprocess.check_output(['ps','-eo','comm='],text=True).splitlines()
        assert not any(x.strip().startswith('qemu-system') for x in names)
        assert not subprocess.check_output(['ss','-H','-lnt','( sport = :22222 )'])
        assert subprocess.run(['lsof','-t',str(DISK)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).returncode==1
        assert os.statvfs(BASE).f_bavail*os.statvfs(BASE).f_frsize > 50*1024**3
        proof=json.loads((BASE/'vm/pg1434-transfer-proof.safe.json').read_bytes())
        assert proof['actualExit']==0 and proof['oldJobActualExit']==1 and proof['copyReissued'] is False
        st=DISK.stat()
        disk_identity=identity(DISK)
        assert st.st_size==proof['remote']['bytes'] and sha(DISK)==proof['remote']['sha256']
        info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(DISK)]))
        assert info['format']=='qcow2' and not info['dirty-flag'] and not info.get('snapshots') and 'backing-filename' not in info
        OUT.mkdir(mode=0o700)
        args=arguments()
        write('boot-reservation.safe.json',{'issuedOnce':True,'args':args,'qualifiedDiskSha256':proof['remote']['sha256'],
            'diskSize':st.st_size,'oldRunRestored':False,'oldPermitReused':False,'businessActions':0,
            'toolSha256':sha(Path(__file__)),'formalAccepted':False})
        with (OUT/'create.private.log').open('xb') as log:
            create=subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(DISK),str(OUT/'active.qcow2')],stdout=log,stderr=log)
        assert create.returncode==0
        with (OUT/'launch.private.log').open('xb') as log:
            launch=subprocess.run(args,stdout=log,stderr=log)
        # Read-only backing byte proof prior to writable guest admission is separate
        # from cold guest/DB/Unit proof; do not report business readiness here.
        write('boot-result.safe.json',{'actualExit':launch.returncode,'createExit':create.returncode,
            'guestPid':int((OUT/'qemu.pid').read_text()) if (OUT/'qemu.pid').exists() else None,
            'backingMetadataUnchanged':disk_identity==identity(DISK),'ramRestored':False,'businessAccepted':False,
            'coldGuestReauthenticationPending':True})
        assert launch.returncode==0
        print('PG1435_ISOLATED_COLD_BOOT_ONCE launchExit=0 businessAccepted=false')


if __name__=='__main__':main()
