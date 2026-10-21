import unittest
from pg6586_api_mapper_jvm_join import jvm_calls,join_calls


class MapperJvmJoinTest(unittest.TestCase):
    def test_actual_receiver_line_and_catch_variable(self):
        raw='''  private void call();
    Code:
       0: aload_1
       1: invokestatic #1 // Method p/TemporaryInfrastructureException.preserveFatal:(Ljava/lang/Throwable;)V
       4: return
    LineNumberTable:
      line 1: 0
      line 2: 4
'''
        bytecode=jvm_calls(raw)
        source='try {} catch(SQLException failure) { TemporaryInfrastructureException.preserveFatal(failure); }'
        rows=join_calls(source,bytecode,{1:dict(ci=1,mi=0,cb=0,mb=0)})
        self.assertEqual('failure',rows[0]['catchVariable'])
        self.assertFalse(rows[0]['perTestCausalityProved'])
        self.assertFalse(rows[0]['accepted'])
        # javac duplicates finally bytecode; distinct offsets are paths, not extra source sites.
        duplicated=bytecode+[dict(bytecode[0],bci=10)]
        self.assertEqual(2,len(join_calls(source,duplicated,{})[0]['jvmPaths']))
        with self.assertRaises(ValueError):join_calls(source,[],{})
        with self.assertRaises(ValueError):join_calls(source,bytecode*2,{})

    def test_missing_debug_or_wrong_receiver_does_not_pass(self):
        raw='''  private void call();
       1: invokestatic #1 // Method p/Other.preserveFatal:(Ljava/lang/Throwable;)V
'''
        with self.assertRaises(ValueError):jvm_calls(raw)
        source='TemporaryInfrastructureException.attachSecondary(a,b);'
        wrong=[dict(method='attachSecondary',owner='p/Other',line=1,bci=1,member='method')]
        with self.assertRaises(ValueError):join_calls(source,wrong,{})


if __name__=='__main__':unittest.main()
