"""Exact stream count/frozen source qualification, no actual coverage or VM."""
import unittest
from pg700_native_gap import source


class BindingTest(unittest.TestCase):
    def test_literal_current_source_and_eight_plus_six_only(self):
        raw=source();compile(raw,'<new source gap>','exec')
        for text in ('pg698-current-eight-native-v1','pg680-owner-six-host-v1','pg700-current-native-gap-v1',
                     'e55c6095a06be0e1aa5a316ee8e43663714728ed5527624e3223c30c1b2a4045',
                     '9bd50536f692610036a0ed8b83e0a8b35fe2a66f','assert len(data) == 14',
                     "record['moduleCounters']",'sourceOrClassExclusions'):
            self.assertIn(text,raw)
        for old in ('pg614-current-eight','pg599-candidate','23b14a44','pg666-current-seventeen'):
            self.assertNotIn(old,raw)


if __name__=='__main__':unittest.main()
