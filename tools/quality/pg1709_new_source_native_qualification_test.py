"""Fixed distinct Main/test/full-source joins and independent catalog sources."""
import ast
import unittest
from pg1709_new_source_native_qualification import source,server


class QualificationJoinTest(unittest.TestCase):
    def test_current_full3596_only_and_no_old_source_exec(self):
        code=server();transport=source();ast.parse(code);ast.parse(transport)
        for literal in ['2741c4546afad6c1e8b6efbd53dfb58144edf7bb',
                        'runs/PG1633-six-v1/manifest.safe.json','source-full-PG1633/src',
                        "full['tests']==3596","'qualified1633Tests':3596","classByteMismatch']==0"]:
            self.assertIn(literal,code)
        for literal in ['PG1532','3583','4d6bcbddb417b76d27e52d5d9640752c300edccf']:
            self.assertNotIn(literal,code)
        for literal in ['pg1708-new-source-native-catalog-v1','pg1636-api-boundary-full-qualified-v1',
                        '1683dd9f6de00e71d2317d9af3cd50400a37bf4e','pg1709-new-source-native-qualified-v1']:
            self.assertIn(literal,transport)
        self.assertNotIn('pg1542-filesystem-full-qualified-v3',transport)


if __name__=='__main__':unittest.main()
