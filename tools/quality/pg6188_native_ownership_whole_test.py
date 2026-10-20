import ast
import unittest
import pg6188_native_ownership_whole as subject


class Definition(unittest.TestCase):
    def test_complete_current_declarations(self):
        self.assertEqual((4023,605),subject.declared_inventory())

    def test_exact_dimensions_and_new_only_namespace(self):
        raw=subject.server_source('a'*40,'0'*64)
        tree=ast.parse(raw)
        for value,count in ((4023,2),(605,1),(1667,1)):
            self.assertEqual(count,sum(isinstance(x,ast.Constant) and type(x.value)is int and x.value==value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6188',raw)
        self.assertNotIn('source-full-PG6118',raw)
        self.assertNotIn(subject.prior.SOURCE,raw)
        self.assertIn('a'*40,raw)

    def test_driver_records_current_whole_not_historical_success(self):
        raw=subject.driver_source({})
        self.assertIn("'tests': 4023, 'suites': 605, 'mainClasses': 1667",raw)
        self.assertIn(subject.SLOT,raw)
        self.assertIn('No VM/current/actualRoot/failedcohort/intent/permit action',raw)


if __name__=='__main__':unittest.main()
