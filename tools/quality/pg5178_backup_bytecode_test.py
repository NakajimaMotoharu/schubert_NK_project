import unittest
import pg5178_backup_bytecode as role


class CheckedNullFactory(unittest.TestCase):
    def test_nonnull_result_returns_without_call_or_allocation_but_null_only_throws_io(self):
        ops=[(0,'invokeinterface','$Io.open:'),(5,'astore_1',''),(6,'aload_1',''),
             (7,'ifnonnull','20'),(10,'invokestatic','unavailable:()Ljava/io/IOException;'),
             (13,'athrow',''),(20,'aload_1',''),(21,'areturn','')]
        method={'ops':ops}
        self.assertEqual(role.checked_factory(method,'$Io.open:'),[5,6,7,20])
        for op in ('invokestatic','ldc','new','invokedynamic','putfield'):
            bad={'ops':list(ops)};bad['ops'][6]=(20,op,'post-resource work')
            with self.assertRaises(ValueError):role.checked_factory(bad,'$Io.open:')
        bad={'ops':[row for row in ops if 'unavailable:' not in row[2]]}
        with self.assertRaises(ValueError):role.checked_factory(bad,'$Io.open:')


if __name__=='__main__':unittest.main()
