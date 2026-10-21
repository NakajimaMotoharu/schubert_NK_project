import ast
import unittest
import pg6302_web_send_whole as subject


class Definition(unittest.TestCase):
    def test_current4043_declarations_without_erasing_old_repeated10(self):
        self.assertEqual((4043,607),subject.declared_inventory())

    def test_new_only_whole_namespace_and_actual_dimensions(self):
        raw=subject.server_source('a'*40,'0'*64);tree=ast.parse(raw)
        for value,count in ((4043,2),(607,1),(1667,1)):
            self.assertEqual(count,sum(isinstance(x,ast.Constant)and type(x.value)is int and x.value==value for x in ast.walk(tree)))
        self.assertIn('source-full-PG6302',raw);self.assertNotIn('source-full-PG6188',raw)

    def test_original84_and_current_pg_before_whole(self):
        raw=subject.driver_source({})
        self.assertIn("'tests': 4043, 'suites': 607, 'mainClasses': 1667",raw)
        self.assertIn(subject.SLOT,raw);self.assertIn('SS321 Web ordinary sender',raw)
        values=subject.definitions()['prerequisites'].__code__.co_consts
        self.assertIn('PG6298-web-send-qualification-v1/manifest.json',values)
        self.assertIn('PG6300-web-send-order-v1/manifest.json',values)


if __name__=='__main__':unittest.main()
