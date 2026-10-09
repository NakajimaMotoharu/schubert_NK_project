import ast
import unittest
from pg797_native_v4 import source


class Test(unittest.TestCase):
    def test_complete_assembled_namespace_not_outer_wrapper(self):
        raw=source();ast.parse(raw)
        for literal in ('pg797-liveness-tools-v3','pg797-frozen-v3.safe.json','pg797-stage-v4.exit','pg797-fixed-stage-v4','Pg797DatabaseProbeTest','Pg797DatabaseProbe ',"action+'-v4'",'frozen[\'fileHashes\']','set(FILES)|{\'payload-sha256.json\'}'):
            self.assertIn(literal,raw)
        for old in ('pg778','Pg778','PG778','pg783','Pg783','PG783','pg797-liveness-tools-v1','pg797-stage-v1.exit','pg797-frozen-v1.safe.json'):
            self.assertNotIn(old,raw)
        self.assertIn("assert (W/'pg797-stage-v4.exit').read_text()=='0\\n'",raw)
        self.assertEqual(1,raw.count('def main():'))


if __name__=='__main__':unittest.main()
