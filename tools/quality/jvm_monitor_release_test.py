"""Handwritten independent javap-shaped branch/release fixtures."""
import unittest
from jvm_monitor_release import check_monitor


class Monitor(unittest.TestCase):
    TWO = '''Code:
      0: aload_0
      1: getfield #CP // Field lock:Ljava/lang/Object;
      4: dup
      5: astore_1
      6: monitorenter
      7: iconst_0
      8: ifeq 15
     11: aload_1
     12: monitorexit
     13: ireturn
     15: aload_1
     16: monitorexit
     17: ireturn
     20: astore_2
     21: aload_1
     22: monitorexit
     23: aload_2
     24: athrow
    Exception table:
       7 13 20 any
      15 17 20 any
      20 23 20 any
'''

    def test_two_normal_return_release_paths_and_one_handler(self):
        value = check_monitor(self.TWO, 3)
        self.assertEqual([12, 16, 22], value['releaseOffsets'])
        self.assertEqual([13, 17], value['normalReturnOffsets'])
        self.assertEqual(1, value['monitorLocal'])

    def test_single_normal_return_and_handler(self):
        code = '''Code:
      0: aload_0
      1: getfield #CP // Field lock:Ljava/lang/Object;
      4: dup
      5: astore_1
      6: monitorenter
      7: aload_1
      8: monitorexit
      9: return
     10: astore_2
     11: aload_1
     12: monitorexit
     13: aload_2
     14: athrow
    Exception table:
       7 9 10 any
      10 13 10 any
'''
        self.assertEqual([9], check_monitor(code, 2)['normalReturnOffsets'])

    def test_missing_wrong_lock_wrong_count_and_unprotected_throw_fail(self):
        for text, count in (
            (self.TWO.replace('12: monitorexit', '12: nop'), 3),
            (self.TWO.replace('21: aload_1', '21: aload_3'), 3),
            (self.TWO, 2),
            (self.TWO.replace('       7 13 20 any', '       8 13 20 any'), 3),
            (self.TWO.replace('23: aload_2', '23: astore_1'), 3),
        ):
            with self.subTest(text=text, count=count), self.assertRaises(ValueError):
                check_monitor(text, count)


if __name__ == '__main__':
    unittest.main()
