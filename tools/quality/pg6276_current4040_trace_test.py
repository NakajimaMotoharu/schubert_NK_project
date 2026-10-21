import unittest
import pg6276_current4040_trace as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_exact4040_run_and_no_old_measurement_values(self):
        scope=subject.definitions('a'*64,'b'*64);values=scope['measurement'].__code__.co_consts
        for value in (4040,607,'PG6272-six-v1'):self.assertIn(value,values)
        for value in (3985,4034,606,'PG6244-six-v1'):self.assertNotIn(value,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE'])

    def test_host_only_zero_new_supports_and_clean_definitions(self):
        scope=subject.definitions('a'*64,'b'*64)
        self.assertIn('PG6276-current943-trace-v1',scope['report'].__code__.co_consts)
        self.assertEqual(0,checkPath(subject.__file__))
        self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
