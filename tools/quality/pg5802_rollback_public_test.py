import unittest
from pg5802_rollback_public import DESIGN,case_name


class IndependentFiniteXmlBindingTest(unittest.TestCase):
    def test_all16_design_ids_and_ordinary_injected_method_identity(self):
        ids=[v for methods in DESIGN.values()for v in methods.values()]
        self.assertEqual(16,len(ids));self.assertEqual({str(i).zfill(3)for i in range(1,17)},set(ids))
        self.assertEqual('method',case_name('method(Path)'))
        self.assertEqual('method',case_name('method()'))
        for value in('',None,'[1] parameter','bad.name()'):
            with self.assertRaises(ValueError):case_name(value)


if __name__=='__main__':unittest.main()
