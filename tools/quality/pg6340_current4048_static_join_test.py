import unittest
import pg6340_current4048_static_join as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_current_source_whole_and_inputs_only(self):
        scope=subject.definitions();values=scope['main'].__code__.co_consts
        for value in (4048,1356,'PG6330-six-v1','PG6340-current4048-static-join-v1'):self.assertIn(value,values)
        for value in (4040,1350,'PG6272-six-v1','PG6282-current4040-static-join-v1'):self.assertNotIn(value,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE']);self.assertIs(subject.read_qualified,scope['read_qualified'])
        self.assertEqual(subject.INPUT_SHA,scope['INPUT_SHA'])
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
