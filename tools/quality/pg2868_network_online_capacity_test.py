"""Actual payload source/literal geometry and ownership deltas; no grow issued."""
import ast
import unittest
from pyflakes.api import check
import pg2868_network_online_capacity_grow as p


class NewCapacity(unittest.TestCase):
    def test_same_boot_qemu_only_positive_eight_gib_child_delta(self):
        a=p.lan_payload();b=p.guest_payload()
        self.assertEqual(60129542144,p.NEW_SIZE)
        self.assertEqual(0,check(a,'<actual same QEMU grow>'));self.assertEqual(0,check(b,'<actual same guest grow>'))
        for v in [p.DISK,'101242','f765c39c924d24fc03739355785e22c06b302d68418a85860e3d661960a2b106','(4599,0,0)','oldThreeBackingMetadataUnchanged',"os.O_RDONLY"]:
            self.assertTrue(v in a,v)
        self.assertTrue("rpc('block_resize',{'device':'virtio0','size':60129542144})"in a)
        self.assertTrue("old['image']['virtual-size']==51539607552"in a)
        self.assertTrue("new['size']==old['size']+16777216"in b)
        self.assertTrue('98338783'in b)
        self.assertTrue(p.BOOT in b)
        self.assertTrue('fcntl.LOCK_EX|fcntl.LOCK_NB'in b)
        for v in ['reboot','poweroff','qemu-img','kill(','copyfile','--shrink','resize2fs -f']:
            self.assertFalse(v in a+b,v)
        commands=[n for n in ast.walk(ast.parse(b))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='command']
        self.assertEqual([['/usr/bin/growpart','/dev/vda','1'],['/usr/sbin/resize2fs','/dev/vda1']],[ast.literal_eval(n.args[0])for n in commands])


if __name__=='__main__':unittest.main()
