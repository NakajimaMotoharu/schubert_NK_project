import ast
import unittest
import pg6212_keeper_ownership_whole as subject


class Definition(unittest.TestCase):
    def test_current_source_declarations(self):
        self.assertEqual((4027,605),subject.declared_inventory())

    def test_actual_current_namespace_and_counts(self):
        raw=subject.server_source('a'*40,'0'*64);tree=ast.parse(raw)
        for value,count in ((4027,2),(605,1),(1667,1)):
            self.assertEqual(count,sum(isinstance(x,ast.Constant) and type(x.value)is int and x.value==value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6212',raw)
        self.assertNotIn('source-full-PG6188',raw)

    def test_genuine_current_prerequisites_and_trigger(self):
        raw=subject.driver_source({})
        self.assertIn("'tests': 4027, 'suites': 605, 'mainClasses': 1667",raw)
        self.assertIn(subject.SLOT,raw)
        self.assertIn('SS318 keeper/diagnostic/fallback',raw)
        names=subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6208-keeper-faults-qualification-v1/manifest.json',names)
        self.assertIn('PG6210-keeper-order-v1/manifest.json',names)


if __name__=='__main__':unittest.main()
