import unittest
import pg6312_current4043_static_join as subject
from pyflakes.api import checkPath


class Definition(unittest.TestCase):
    def test_current_whole_and_source_inputs_only(self):
        scope=subject.definitions();values=scope['main'].__code__.co_consts
        for value in (4043,1357,'PG6302-six-v1','PG6312-current4043-static-join-v1'):
            self.assertIn(value,values)
        for value in (4040,1350,'PG6272-six-v1','PG6282-current4040-static-join-v1'):
            self.assertNotIn(value,values)
        self.assertEqual(subject.SOURCE,scope['SOURCE'])
        self.assertIs(subject.read_qualified,scope['read_qualified'])
        self.assertEqual(subject.INPUT_SHA,scope['INPUT_SHA'])
        self.assertEqual(0,checkPath(subject.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
