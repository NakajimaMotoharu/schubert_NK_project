"""Independent header and noargs argv, old logicalrun/activation rejected."""
import unittest
from pyflakes.api import check
from pg2074_current_newrun_live_binding import body,entry,SLOT


class NewBinding(unittest.TestCase):
    def test_actual_live_header_and_fixed_entry(self):
        raw='SOURCE="fixed"\nDIGEST="fixed"\nEXPECTED={}\n'+body()
        self.assertEqual(0,check(raw,'<actual newrun live binding>'))
        for marker in ["MorningProcessMain\\0'","fields[1]!='4148e3e8-f107-431a-ab27-d6e6d1f1772e'","fields[3]!='e31b627c-c0e2-4120-bd64-c0777479e800'",'meta(active.lstat())==m','show()==unit']:
            self.assertTrue(marker in raw,marker)
        self.assertEqual(SLOT,entry().__globals__['SLOT'])
        self.assertFalse('--resume'in raw)


if __name__=='__main__':unittest.main()
