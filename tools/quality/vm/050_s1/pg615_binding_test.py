"""Only new8 actual source coordinates; no mutations or prior native input."""
import ast
from pathlib import Path
import unittest
class Test(unittest.TestCase):
    def test_fixed_source_fourteen_inputs(self):
        s=(Path(__file__).resolve().parent/'pg615_current_native_gap.py').read_text();ast.parse(s)
        self.assertIn('pg614-current-eight-native-v1',s)
        self.assertIn('4c178d8e6d2f76f097a315226586bb934041ce1805a5cd79811e2034b3b442c1',s)
        self.assertIn('23b14a44b10504172e030bbd6625926bf049fb5c',s)
        self.assertIn('assert len(data) == 14',s);self.assertIn("record['selected']",s)
        self.assertNotIn('bootstrap.exec',s);self.assertNotIn("prior['currentNativeFiles']",s)
        self.assertIn('NativeCoverageXml471',s);self.assertIn("record['moduleCounters']",s)
        self.assertIn("sourceOrClassExclusions':False",s)
if __name__=='__main__':unittest.main()
