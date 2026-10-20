import unittest
import pg6258_current4034_trace as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_fixed_current_measurement_definitions_not_old3985(self):
        scope=subject.definitions('a'*64,'b'*64)
        values=scope['measurement'].__code__.co_consts
        self.assertIn(4034,values);self.assertIn(606,values);self.assertIn('PG6244-six-v1',values)
        self.assertNotIn(3985,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE'])

    def test_host_only_no_acceptance_or_support_readdition(self):
        scope=subject.definitions('a'*64,'b'*64)
        self.assertIn('PG6258-current943-trace-v1',scope['report'].__code__.co_consts)
        self.assertEqual(0,checkPath(subject.__file__))
        self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
