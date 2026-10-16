import ast
import unittest
import pg3794_hygiene_publication_post as tool


class IndependentPublication(unittest.TestCase):
    def test_all_finite_phases_and_originals_retained(self):
        raw=tool.payload();ast.parse(raw)
        for marker in ['for stamp,phase,observed in phases:',"require(json.loads(pub_before)==old_after)",'read_rows()==first',"complete_configuration(r.stdout,unit)==oldcfg",'newTenReferencesReturnedNormally',tool.role.SOURCE,tool.role.BOM,tool.role.BEFORE,tool.role.SAVE,tool.role.TOOLS,'pg3662-native-stop-v1/after.private.json','originalBackupNative34Preserved']:
            self.assertTrue(marker in raw,marker)
        self.assertIn("expected={**expected,'startup':after['startup']}",raw)
        self.assertLess(raw.index('for unit in reversed(refs):'),raw.rindex('print(json.dumps('))
        for marker in ['daemon-reload\',','systemctl start','systemctl stop','pg3450','pg3456']:self.assertFalse(marker in raw,marker)


if __name__=='__main__':unittest.main()
