"""Independent normal/GC/journal/null vectors plus previous logicalrun and activation rejection."""
import unittest
from pg2021_fresh_resume_terminal_receipt_test import Receipt
from pg2076_current_newrun_terminal_receipt import classify,payload,entry,SLOT


class Newrun(unittest.TestCase):
    def test_newrun_receipt_and_foreign_previous_completion(self):
        fixture=Receipt()
        for code in [0,10]:
            b,s,r,d=fixture.fixture(code)
            self.assertEqual(code,classify(b,s,r,d)['completionCode'])
            payload(dict(b,rootPid=588342))
            for key,value in [('run','4148e3e8-f107-431a-ab27-d6e6d1f1772e'),('activation','e31b627c-c0e2-4120-bd64-c0777479e800')]:
                with self.assertRaises(ValueError):classify(dict(b,**{key:value}),s,r,d)
        self.assertEqual(SLOT,entry().__globals__['SLOT'])
        with self.assertRaises(ValueError):classify(None,None,None,None)


if __name__=='__main__':unittest.main()
