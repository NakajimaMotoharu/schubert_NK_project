"""Actual new-slot stage graph names, original Root UUID untouched."""
import unittest
from pg1857_warning_nested_unused_dispatch import source,STAGE
from pg1855_warning_nested_unused_sources import sources


class Profile(unittest.TestCase):
    def test_actual_complete_new_names_and_frozen_python_closure(self):
        raw=source()
        for v in ['pg1856-frozen-v1.safe.json','pg1857-warning-release-v1.tar','Pg1855UnusedStage place','pg1857-stage-v2.exit']:
            self.assertIn(v,raw)
        self.assertIn('pg1855-warning-unused-tools-v1',STAGE)
        s=sources('b'*64,'c'*64)
        self.assertIn('4148e3e8-f107-431a-ab27-d6e6d1f1772e',s['Pg1855UnusedStage.java'])
        self.assertIn('pg1858-warning-unused-placement-v1',s['pg1855_native_refs.py'])
        self.assertNotIn('pg1850-frozen',raw)


if __name__=='__main__':unittest.main()
