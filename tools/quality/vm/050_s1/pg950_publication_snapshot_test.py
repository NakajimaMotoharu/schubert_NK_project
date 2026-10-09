"""Immutable preimage and explicit finite after phase; never run guest from this test."""
import ast,unittest
from pg949_publication_snapshot import payload
class Test(unittest.TestCase):
    def test_before_never_changes_current_or_epoch(self):
        p=payload('before');ast.parse(p)
        for literal in ("assert current.readlink() == old",'expected_old_approval','genuine_parent()','value[\'comparison\'] = comparable','resources();value=protected();assert value==protected();resources()'):
            self.assertIn(literal,p)
        self.assertNotIn("phase='after'",p)
    def test_after_pins_unmodified_before_not_reconstructed_after(self):
        p=payload('after');ast.parse(p)
        for literal in ('88fe076a608f8877b54bd9e250c5684fa7117667fbd952f46871382550e47d22',"baseline['trees']=saved['comparison']['trees']","phase='after';expected_epoch=expected()",'pg942-activate-v1',"old-epoch.private",'88ab94922aa165ae1c01e778521922e3693986eba93b587032affeedf16c130c',"stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)"):
            self.assertIn(literal,p)
        self.assertNotIn('approval_root =',p)
        self.assertLess(p.index('saved=json.loads(before_raw)'),p.index("phase='after'"))
        for forbidden in ('StartUnit','StopUnit','daemon-reload','Files.move','tar.extractall'):
            self.assertNotIn(forbidden,p)
if __name__=='__main__':unittest.main()
