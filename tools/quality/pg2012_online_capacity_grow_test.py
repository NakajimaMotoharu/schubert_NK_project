"""Actual finite payloads: only grow, preserve partition identity and existing VM ownership."""
import ast
import unittest
from pyflakes.api import check
from pg2012_online_capacity_grow import LAN,GUEST,NEW_SIZE


class Capacity(unittest.TestCase):
    def test_actual_only_online_fixed_growth_and_guards(self):
        self.assertEqual(51539607552,NEW_SIZE)
        for name,raw in [('LAN',LAN),('guest',GUEST)]:
            self.assertEqual(0,check(raw,'<actual '+name+'>'))
            for forbidden in ['qemu-img','reboot','poweroff','kill(', 'copyfile','--shrink','resize2fs -f']:
                self.assertTrue(forbidden not in raw,'no '+forbidden)
        self.assertTrue("rpc('block_resize',{'device':'virtio0','size':51539607552})" in LAN)
        self.assertTrue("SO_PEERCRED,12))==(13204,0,0)" in LAN)
        self.assertTrue('disk.stat().st_ino==inode' in LAN)
        self.assertTrue("new['size']==old['size']+16777216" in GUEST)
        self.assertTrue("after['lastlba']==before['lastlba']+16777216" in GUEST)
        self.assertTrue("noRepeat" in GUEST and "rootStartUuidTypeUnchanged" in GUEST)
        self.assertTrue('fcntl.LOCK_EX|fcntl.LOCK_NB' in GUEST)
        tree=ast.parse(GUEST)
        commands=[n.args[0]for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='command']
        self.assertEqual([['/usr/bin/growpart','/dev/vda','1'],['/usr/sbin/resize2fs','/dev/vda1']],[[v.value for v in n.elts]for n in commands])


if __name__=='__main__':unittest.main()
