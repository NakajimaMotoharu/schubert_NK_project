import unittest
import pg6334_current4048_trace as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_exact4048_run_and_no_prior_measurement(self):
        scope=subject.definitions('a'*64,'b'*64);values=scope['measurement'].__code__.co_consts
        for value in (4048,607,'PG6330-six-v1'):self.assertIn(value,values)
        for value in (3985,4034,4040,4043,606,'PG6244-six-v1','PG6302-six-v1'):self.assertNotIn(value,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE'])
        self.assertIn('PG6334-current943-trace-v1',scope['report'].__code__.co_consts)
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
