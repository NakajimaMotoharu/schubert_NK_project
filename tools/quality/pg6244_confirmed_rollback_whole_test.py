import ast
import unittest
import pg6244_confirmed_rollback_whole as subject


class Definition(unittest.TestCase):
    def test_current_source_declarations(self):
        self.assertEqual((4034,606),subject.declared_inventory())

    def test_exact_new_namespace_and_actual_dimensions(self):
        raw=subject.server_source('a'*40,'0'*64);tree=ast.parse(raw)
        for value,count in ((4034,2),(606,1),(1667,1)):
            self.assertEqual(count,sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6244',raw)
        self.assertNotIn('source-full-PG6188',raw)

    def test_current_prerequisites_and_actual_trigger(self):
        raw=subject.driver_source({})
        self.assertIn("'tests': 4034, 'suites': 606, 'mainClasses': 1667",raw)
        self.assertIn(subject.SLOT,raw)
        self.assertIn('SS319 per-delivery rollback',raw)
        values=subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6248-normal-phase-qualification-v1/manifest.json',values)
        self.assertIn('PG6242-confirmed-rollback-order-v1/manifest.json',values)


if __name__=='__main__':unittest.main()
