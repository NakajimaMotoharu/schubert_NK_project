"""Pure exact newboot oracle binding, no actual metadata/DB authority or PT credit."""
import unittest
import copy
from pyflakes.api import check
import pg2814_network_newboot_readonly as p


class ColdOracleBinding(unittest.TestCase):
    def test_actual_current_vector_schema_is_exact_and_preserved(self):
        metadata=[1,2,0,0,0o100644,1,32,100,101]
        values={'/etc/systemd/system/fixture.service':metadata+['c'*64]}
        before=copy.deepcopy(values)
        self.assertEqual({'/etc/systemd/system/fixture.service':{'metadata':metadata,'sha256':'c'*64}},p.unit_vectors(values))
        self.assertEqual(before,values)
        cases=[None,{},{'relative':metadata+['c'*64]},{'/etc/../foreign':metadata+['c'*64]},
            {'/etc/unit\n':metadata+['c'*64]},{'/etc/unit':{'metadata':metadata,'sha256':'c'*64}},
            {'/etc/unit':metadata+['c'*63]},{'/etc/unit':metadata+['C'*64]},
            {'/etc/unit':metadata+['c'*64,0]},{'/etc/unit':metadata[:-1]+['c'*64]}]
        for index in range(9):
            for bad in [None,True,-1,'1']:
                row=metadata.copy();row[index]=bad;cases.append({'/etc/unit':row+['c'*64]})
        for bad in cases:
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):p.unit_vectors(bad)

    def test_all_semantic_boundaries_and_no_old_tmpfs_authority(self):
        r=p.payload();self.assertEqual(0,check(r,'<newboot complete oracle>'))
        for text in [p.SOURCE,p.BOM,p.BOOT,p.BEFORE,'pg2806-current-042-before-v1/before.private.json',
            "rows==old['rows'] and len(rows)==24","durable==old['durable']","old['unitFiles']",
            '0.1.0-PG2654','pg2654-manifest.sig',"'oldRunPermitNativeRestored':False","'newLocksNoFlockTwice':True"]:
            self.assertIn(text,r)
        self.assertNotIn("old['startup']",r);self.assertNotIn("old['runtime']",r)
        self.assertIn("'unitFiles':unit_vectors(saved['unitFilesActual'])",r)
        self.assertIn('pg2814-network-newboot-readonly-v2',r)
        self.assertNotIn('os.chmod(',r);self.assertNotIn('StartUnit(',r)
        self.assertIn("require(boot=='"+p.BOOT+"' and boot!='b2d6",r)
        with self.assertRaises(ValueError):p.one('missing','wanted','replacement')
        with self.assertRaises(ValueError):p.one('duplicated duplicated','duplicated','replacement')


if __name__=='__main__':unittest.main()
