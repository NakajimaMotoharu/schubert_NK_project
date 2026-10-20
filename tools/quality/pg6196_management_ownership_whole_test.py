import ast
import unittest
import pg6196_management_ownership_whole as subject


class Definition(unittest.TestCase):
    def test_all_current_source_cases(self):
        self.assertEqual((4024,605),subject.declared_inventory())

    def test_current_dimensions_namespace_and_source(self):
        raw=subject.server_source('a'*40,'0'*64);tree=ast.parse(raw)
        for value,count in ((4024,2),(605,1),(1667,1)):
            self.assertEqual(count,sum(isinstance(x,ast.Constant) and type(x.value)is int and x.value==value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6196',raw)
        self.assertNotIn('source-full-PG6188',raw)
        self.assertIn('a'*40,raw)

    def test_correct_actual_prerequisites_and_expected_driver(self):
        raw=subject.driver_source({})
        self.assertIn("'tests': 4024, 'suites': 605, 'mainClasses': 1667",raw)
        self.assertIn(subject.SLOT,raw)
        self.assertIn('Original60 all-six qualification',raw)
        names=subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6193-management-primary-qualification-v2/manifest.json',names)
        self.assertIn('PG6195-management-primary-order-v2/manifest.json',names)


if __name__=='__main__':unittest.main()
