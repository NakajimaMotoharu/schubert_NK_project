import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pg2200_outage_cold_preservation as p


class ColdPreservation(unittest.TestCase):
    def test_isolation_contract_and_no_old_writable_disk(self):
        args=p.arguments()
        expected=('root=UUID=92978eec-7925-481e-8629-5b963d59ced1 ro console=ttyS0 '
          'systemd.unit=basic.target systemd.wants=systemd-networkd.service '
          'systemd.wants=systemd-resolved.service systemd.wants=systemd-user-sessions.service '
          'systemd.wants=ssh.service systemd.wants=postgresql.service '
          'systemd.mask=timers.target systemd.mask=paths.target '
          'systemd.mask=snapd.socket systemd.mask=lxd-installer.socket')
        self.assertEqual(args[args.index('-append')+1],expected)
        self.assertEqual(args[args.index('-smp')+1],'4')
        self.assertEqual(args[args.index('-m')+1],'8192')
        self.assertEqual([args[i+1] for i,a in enumerate(args) if a=='-drive'],[
          str('file='+str(p.OUT)+'/active.qcow2,if=virtio,format=qcow2'),
          'file=/home/mini/schubert-nk-pgpt/tools/seed.iso,media=cdrom,readonly=on'])
        self.assertNotIn('-loadvm',args)
        self.assertNotIn(str(p.OLD),args)

    def test_hash_identity_and_exclusive_durable_receipt(self):
        with tempfile.TemporaryDirectory() as d,patch.object(p,'OUT',Path(d)):
            f=Path(d)/'fixture';f.write_bytes(b'abc')
            self.assertEqual(p.digest(f),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            old=p.identity(f);f.write_bytes(b'abd');self.assertNotEqual(p.identity(f),old)
            p.save('receipt',{'oldStopNativeAccepted':False})
            with self.assertRaises(FileExistsError):p.save('receipt',{'oldStopNativeAccepted':True})
            self.assertFalse(json.loads((Path(d)/'receipt').read_text())['oldStopNativeAccepted'])

    def test_boot_refuses_changed_source_before_any_launch(self):
        with tempfile.TemporaryDirectory() as d,patch.object(p,'OUT',Path(d)),patch.object(p,'require_idle'),patch.object(p.subprocess,'run') as launch:
            p.save('manifest.safe.json',{'actualExit':0,'logicalCompareExit':0,'source':'foreign'})
            with self.assertRaises(AssertionError):p.boot()
            launch.assert_not_called()
            self.assertFalse((Path(d)/'boot-reservation.safe.json').exists())

    def test_boot_rejects_existing_reservation_without_second_launch(self):
        with tempfile.TemporaryDirectory() as d,patch.object(p,'OUT',Path(d)),patch.object(p,'require_idle'),patch.object(p.subprocess,'run') as launch:
            active=Path(d)/'active.qcow2';active.write_bytes(b'fixture')
            p.save('manifest.safe.json',{'actualExit':0,'logicalCompareExit':0,'source':p.SOURCE,'chain':{},'newOverlaySha256':hashlib.sha256(b'fixture').hexdigest()})
            p.save('boot-reservation.safe.json',{'issuedOnce':True})
            with self.assertRaises(AssertionError):p.boot()
            launch.assert_not_called()


if __name__=='__main__':unittest.main()
