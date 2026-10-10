"""Fixed SS343 management-only argv oracle; no actual boot in this test."""
import unittest
from pg1001_isolated_boot import arguments,OUT

class BootTest(unittest.TestCase):
    def test_same_isolation_new_disk_only_no_business_want_or_old_resume(self):
        a=arguments();append=a[a.index('-append')+1]
        self.assertIn('systemd.unit=basic.target',append)
        self.assertIn('systemd.mask=timers.target',append)
        self.assertIn('systemd.mask=paths.target',append)
        self.assertNotIn('schubert',append)
        self.assertEqual(f'file={OUT}/active.qcow2,if=virtio,format=qcow2',a[a.index('-drive')+1])
        self.assertEqual('q35,accel=kvm',a[a.index('-machine')+1])
        self.assertEqual('8192',a[a.index('-m')+1])
        self.assertEqual('user,id=pgptnet,hostfwd=tcp:127.0.0.1:22222-:22',a[a.index('-netdev')+1])
        self.assertNotIn('pg500',str(a))
        self.assertNotIn('resume',str(a))

if __name__=='__main__':unittest.main()
