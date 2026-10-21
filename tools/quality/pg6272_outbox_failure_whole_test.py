import ast
import unittest
import pg6272_outbox_failure_whole as subject


class Definition(unittest.TestCase):
    def test_actual_current_source_declarations(self):
        self.assertEqual((4040,607),subject.declared_inventory())

    def test_exact_new_namespace_and_actual_dimensions(self):
        raw=subject.server_source('a'*40,'0'*64);tree=ast.parse(raw)
        for value,count in ((4040,2),(607,1),(1667,1)):
            self.assertEqual(count,sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6272',raw)
        self.assertNotIn('source-full-PG6188',raw)

    def test_original51_and_current_pg_prerequisites(self):
        raw=subject.driver_source({})
        self.assertIn("'tests': 4040, 'suites': 607, 'mainClasses': 1667",raw)
        self.assertIn(subject.SLOT,raw)
        self.assertIn('SS320 ordinary Outbox fatal cleanup',raw)
        values=subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6268-outbox-failure-qualification-v1/manifest.json',values)
        self.assertIn('PG6270-outbox-failure-order-v2/manifest.json',values)


if __name__=='__main__':unittest.main()
