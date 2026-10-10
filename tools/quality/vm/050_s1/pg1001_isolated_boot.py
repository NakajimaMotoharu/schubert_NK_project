"""Once-only management boot of the saved instance through a fresh COW layer.
The SS343 basic.target isolation flags are inherited unchanged from PG500.
No business start, migration, old /run restoration, or historical-success inference.
"""
import fcntl
import json
import os
import subprocess
from pathlib import Path
from pg997_offline_preservation import VM,ENV,identity,idle,digest,write_new

QEMU=Path('/home/mini/codex/project1/work/toolchain/qemu/root/usr/bin/qemu-system-x86_64')
OUT=VM/'private/pg1000-cold-overlay-v1'
QROOT=QEMU.parents[1]

def arguments():
    return [str(QEMU),'-name','pgpt-r2','-machine','q35,accel=kvm','-cpu','host','-smp','4','-m','8192',
      '-L',str(QROOT/'share/qemu'),'-bios',str(QROOT/'share/seabios/bios-256k.bin'),
      '-kernel',str(VM/'pg443-offline.eRv29R/vmlinuz'),'-initrd',str(VM/'pg443-offline.eRv29R/initrd'),
      '-append','root=UUID=92978eec-7925-481e-8629-5b963d59ced1 ro console=ttyS0 systemd.unit=basic.target systemd.wants=systemd-networkd.service systemd.wants=systemd-resolved.service systemd.wants=systemd-user-sessions.service systemd.wants=ssh.service systemd.wants=postgresql.service systemd.mask=timers.target systemd.mask=paths.target systemd.mask=snapd.socket systemd.mask=lxd-installer.socket',
      '-drive',f'file={OUT}/active.qcow2,if=virtio,format=qcow2',
      '-drive',f'file={VM}/seed.iso,media=cdrom,readonly=on',
      '-netdev','user,id=pgptnet,hostfwd=tcp:127.0.0.1:22222-:22',
      '-device','virtio-net-pci,netdev=pgptnet,romfile=','-vga','none','-display','none','-monitor','none',
      '-qmp',f'unix:{OUT}/qmp.sock,server=on,wait=off','-serial',f'file:{OUT}/console.private.log',
      '-pidfile',str(OUT/'qemu.pid'),'-daemonize']

def main():
    os.umask(0o077)
    with (VM/'private/pg997-boot-guard.lock').open('a') as guard:
        fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB);idle()
        record=json.loads((OUT/'manifest.safe.json').read_bytes())
        assert record['actualExit']==record['logicalCompareExit']==0
        disk=VM/'instance.qcow2';base=VM/'ubuntu-26.04-server-cloudimg-amd64.img'
        assert record['sourceIdentity']==identity(disk) and record['backingIdentity']==identity(base)
        assert record['workingDiskBeforeSha256']==digest(OUT/'active.qcow2')
        for name in ['qmp.sock','console.private.log','qemu.pid','boot-reservation.safe.json','boot-result.safe.json']:
            assert not (OUT/name).exists()
        assert os.statvfs(VM).f_bavail*os.statvfs(VM).f_frsize>2*1024**3
        args=arguments()
        write_new(OUT/'boot-reservation.safe.json',{'run':'PG1001-isolated-boot-v1','args':args,
          'logicalCheckpoint':'PG1000-cold-overlay-v1','sourceIdentity':record['sourceIdentity'],
          'toolHashes':{p.name:digest(p) for p in [Path(__file__),Path(__file__).with_name('pg997_offline_preservation.py')]},
          'originalDiskIsBacking':True,'businessAcceptance':False,'oldRunRestored':False,'issuedOnce':True})
        with (OUT/'launch.private.log').open('xb') as f:
            result=subprocess.run(args,env=ENV,stdout=f,stderr=f)
        write_new(OUT/'boot-result.safe.json',{'actualExit':result.returncode,
          'originalDiskStable':record['sourceIdentity']==identity(disk),'run':'PG1001-isolated-boot-v1',
          'businessAcceptance':False,'oldRunRestored':False})
        assert result.returncode==0 and record['sourceIdentity']==identity(disk)
        print('PG1001_MANAGEMENT_BOOT issuedOnce=true actualExit=0 originalDiskStable=true businessAcceptance=false')

if __name__=='__main__':main()
