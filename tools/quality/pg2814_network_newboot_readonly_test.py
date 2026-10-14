"""Pure exact newboot oracle binding, no actual metadata/DB authority or PT credit."""
import unittest
from pyflakes.api import check
import pg2814_network_newboot_readonly as p


class ColdOracleBinding(unittest.TestCase):
    def test_all_semantic_boundaries_and_no_old_tmpfs_authority(self):
        r=p.payload();self.assertEqual(0,check(r,'<newboot complete oracle>'))
        for text in [p.SOURCE,p.BOM,p.BOOT,p.BEFORE,'pg2806-current-042-before-v1/before.private.json',
            "rows==old['rows'] and len(rows)==24","durable==old['durable']","old['unitFiles']",
            '0.1.0-PG2654','pg2654-manifest.sig',"'oldRunPermitNativeRestored':False","'newLocksNoFlockTwice':True"]:
            self.assertIn(text,r)
        self.assertNotIn("old['startup']",r);self.assertNotIn("old['runtime']",r)
        self.assertNotIn('os.chmod(',r);self.assertNotIn('StartUnit(',r)
        self.assertIn("require(boot=='"+p.BOOT+"' and boot!='b2d6",r)
        with self.assertRaises(ValueError):p.one('missing','wanted','replacement')
        with self.assertRaises(ValueError):p.one('duplicated duplicated','duplicated','replacement')


if __name__=='__main__':unittest.main()
