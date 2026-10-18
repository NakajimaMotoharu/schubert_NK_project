import unittest
from pyflakes.api import checkPath
import pg5506_snapshot_ownership_review as entry


FIXTURE='''
  private static byte[] compress(byte[]);
    Code:
       0: new #1 // class java/util/zip/Deflater
       2: invokespecial #2 // Method java/util/zip/Deflater."<init>":(I)V
       5: newarray byte
       9: invokevirtual #3 // Method java/util/zip/Deflater.end:()V
      12: invokevirtual #3 // Method java/util/zip/Deflater.end:()V
    Exception table:
       from to target type
       6 10 11 any
  private static void other();
'''


class BytecodeEvidence(unittest.TestCase):
    def test_unprotected_array_is_open_gap_not_finally_exemption(self):
        text=entry.method(FIXTURE,'private static byte[] compress(byte[])');value=entry.scratch_gap(text,'Deflater')
        self.assertTrue(value['allocationAfterNativeBeforeGuard']);self.assertFalse(value['scratchProtectedByErrorHandler'])
        self.assertEqual(value['constructorPc'],2);self.assertEqual(value['scratchNewarrayPc'],5)
        self.assertEqual(value['endPcs'],[9,12])

    def test_error_guard_or_array_before_native_does_not_create_that_gap(self):
        text=entry.method(FIXTURE,'private static byte[] compress(byte[])')
        self.assertFalse(entry.scratch_gap(text.replace('6 10 11 any','3 10 11 any'),'Deflater')['allocationAfterNativeBeforeGuard'])
        self.assertFalse(entry.scratch_gap(text.replace('5: newarray','1: newarray'),'Deflater')['allocationAfterNativeBeforeGuard'])
        self.assertTrue(entry.scratch_gap(text.replace('6 10 11 any','3 10 11 Class java/util/zip/DataFormatException'),'Deflater')['allocationAfterNativeBeforeGuard'])

    def test_missing_or_foreign_class_cannot_be_qualified(self):
        for text in(FIXTURE.replace('newarray','aload'),FIXTURE.replace('Deflater','Inflater')):
            with self.assertRaises(ValueError):entry.scratch_gap(text,'Deflater')
        with self.assertRaises(ValueError):entry.method(FIXTURE+FIXTURE,'private static byte[] compress(byte[])')
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
