"""Explicit actual whole source bound projection and new-only output."""
import unittest
from pg2087_current_newrun_parent_projection import payload,entry,SLOT


class Parent(unittest.TestCase):
    def test_whole_source_role_and_entry(self):
        raw=payload('a'*64)
        self.assertTrue('pg2085-native-augmented-newrun-full-seal-v1'in raw)
        self.assertFalse('pg2081-current-newrun-full-live-seal-v1'in raw)
        self.assertEqual(SLOT,entry().__globals__['SLOT'])


if __name__=='__main__':unittest.main()
