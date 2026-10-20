import unittest
import pg6072_jms_owner_initial_gap as t


class ConstructorGapScopeTest(unittest.TestCase):
    def test_existing_protection_or_nonallocating_constructor_is_not_this_gap(self):
        name = 'public.Fixture'
        ctor = '0: new #CP // class java/util/concurrent/atomic/AtomicBoolean\n9: putfield #CP // Field context:Ljakarta/jms/JMSContext;'
        caller = '1: invokeinterface #CP // InterfaceMethod java/util/function/Supplier.get:()Ljava/lang/Object;\n8: invokespecial #CP // Method "<init>":(Ljakarta/jms/JMSContext;)V\nException table:\n12 20 24 Class java/lang/Error'
        blocks = {'  private '+name+'(jakarta.jms.JMSContext);': ctor, '  public static create();': caller}
        self.assertTrue(t.unprotected_constructor_gap(blocks, name, 'java/util/function/Supplier.get:')['constructorOutsideAllExceptionRanges'])
        for changed in (dict(blocks) | {'  public static create();': caller.replace('12 20', '0 20')},
                        dict(blocks) | {'  private '+name+'(jakarta.jms.JMSContext);': ctor.replace('new #CP', 'other #CP')}):
            with self.assertRaises(ValueError):
                t.unprotected_constructor_gap(changed, name, 'java/util/function/Supplier.get:')


if __name__ == '__main__':
    unittest.main()
