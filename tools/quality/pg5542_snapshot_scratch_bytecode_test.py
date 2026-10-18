import unittest
from pyflakes.api import checkPath
import pg5542_snapshot_scratch_bytecode as entry


FIXTURE='''
  static byte[] fixture(byte[]);
    0: new #1 // class java/util/zip/Deflater
    4: invokespecial #2 // Method java/util/zip/Deflater."<init>":(I)V
    7: astore_2
    8: new #3 // class java/util/zip/DeflaterOutputStream
    12: invokevirtual #4 // Method java/util/zip/Deflater.end:()V
    15: invokevirtual #4 // Method java/util/zip/Deflater.end:()V
    Exception table:
       from to target type
       8 12 14 any
'''


class Bytecode(unittest.TestCase):
    def test_immediate_protected_action_and_missing_late_or_wrong_handler(self):
        self.assertEqual(entry.fixture_guard(FIXTURE)['firstProtectedActionPc'],8)
        for bad in(FIXTURE.replace('8 12 14 any','9 12 14 any'),FIXTURE.replace('astore_2','invokevirtual'),
            FIXTURE.replace('8 12 14 any','8 12 14 Class java/lang/Exception'),FIXTURE.replace('15: invokevirtual','15: aload_2')):
            with self.assertRaises(ValueError):entry.fixture_guard(bad)

    def test_only_local_slots_and_pool_indices_are_normalized_not_literal_values(self):
        old=FIXTURE.replace('12: invokevirtual','9: aload_1\n    10: iconst_1\n    12: invokevirtual')
        new=old.replace('9: aload_1','9: aload_2').replace('#4 //','#99 //')
        self.assertEqual(entry.canonical_body(old),entry.canonical_body(new,True))
        self.assertNotEqual(entry.canonical_body(old),entry.canonical_body(new.replace('10: iconst_1','10: iconst_2'),True))
        self.assertEqual(len(entry.method_parts(FIXTURE)),1)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
