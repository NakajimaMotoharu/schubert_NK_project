import ast
import unittest
import pg3840_current_full11_baseline as tool


class FreshFull11(unittest.TestCase):
    def test_all_actual_fields_current_source_and_finite_reference_close(self):
        raw=tool.payload();ast.parse(raw)
        for marker in [tool.SOURCE,tool.BOM,tool.AFTER,'pg3822-native-stop-v1','baseline==expected','states[unit]==old',"cfg[unit]==expected['configuration'][unit]",'j==expected[\'pid1\']','read_rows()==first','==40)','dataOnlyNotAdmissionAuthority',tool.SLOT]:self.assertTrue(marker in raw,marker)
        for marker in ['pg3662','PG3420','==34)','systemctl start','systemctl stop','daemon-reload']:self.assertFalse(marker in raw,marker)
        self.assertLess(raw.index('for unit in reversed(refs):'),raw.rindex('print(json.dumps('))


if __name__=='__main__':unittest.main()
