"""Literal bytecode success/negative paths, not Java/VM authority or coverage fabrication."""
import unittest
import pg5138_factory_bytecode as role


class FactoryBytecode(unittest.TestCase):
    def test_canonical_cp_padding_is_not_literal_or_handler_normalization(self):
        old = {'ops':[(0,'ldc','#7                  // String resource release'),(2,'areturn','')], 'handlers':[]}
        new = {'ops':[(0,'ldc','#15                 // String resource release'),(2,'areturn','')], 'handlers':[]}
        self.assertEqual(role.canonical(old), role.canonical(new))
        for changed in ({'ops':[(0,'ldc','#15 // String resource release '),(2,'areturn','')], 'handlers':[]},
                        {'ops':[(0,'aconst_null',''),(2,'areturn','')], 'handlers':[]},
                        {**new,'handlers':[(0,2,2,'Class java/io/IOException')]}):
            self.assertNotEqual(role.canonical(old), role.canonical(changed))

    def test_nonnull_success_skips_only_null_fault_and_requires_all_handlers(self):
        method = {'ops':[(0,'invokeinterface','ResourceScope$Acquire.open:()Ljava/lang/Object;'),
                         (5,'astore_3',''),(6,'aload_3',''),(7,'ifnonnull','20'),(10,'new','NPE'),
                         (13,'athrow',''),(20,'aload_2',''),(21,'invokeinterface','action')],
                  'handlers':[(20,21,30,'Class java/io/IOException'),(20,21,30,'Class java/lang/RuntimeException'),
                              (20,21,30,'Class java/lang/Error')]}
        self.assertEqual(role.scope_prefix(method)['successfulPrefixPcs'],[5,6,7])
        for op in ('ldc','new','invokedynamic','invokestatic','newarray'):
            bad = {**method,'ops':list(method['ops'])}
            bad['ops'][1] = (5,op,'owned allocation or call')
            with self.assertRaises(ValueError): role.scope_prefix(bad)
        bad = {**method,'handlers':method['handlers'][:2]}
        with self.assertRaises(ValueError): role.scope_prefix(bad)

    def test_nonnegative_primitive_skips_invalid_fd_allocation_only(self):
        method = {'ops':[(0,'istore_2',''),(1,'iload_2',''),(2,'ifge','20'),
                         (5,'new','invalid fd exception'),(8,'athrow',''),(20,'aload_0',''),
                         (21,'iload_2',''),(22,'putfield','descriptor:I'),(25,'return','')]}
        self.assertEqual(role.positive_path(method,0,None,'nonnegative'),[0,1,2,20,21,22])
        bad = {'ops':list(method['ops'])}; bad['ops'][6] = (21,'invokestatic','Integer.valueOf')
        with self.assertRaises(ValueError): role.positive_path(bad,0,None,'nonnegative')


if __name__=='__main__':
    unittest.main()
