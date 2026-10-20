import unittest
import pg6078_jms_owner_order as t


class FactoryLastInstructionProofTest(unittest.TestCase):
    def test_post_acquire_allocation_or_unknown_call_is_not_safe(self):
        cls = 'public.Fixture'; factory = 'java/util/function/Supplier.get:'
        key = '  private '+cls+'(java.util.function.Supplier<jakarta.jms.JMSContext>);'
        code = '0: new #CP // class java/util/concurrent/atomic/AtomicBoolean\n8: invokeinterface #CP // InterfaceMethod '+factory+'()Ljava/lang/Object;\n13: ldc #CP // String fixed\n15: invokestatic #CP // Method java/util/Objects.requireNonNull:(Ljava/lang/Object;Ljava/lang/String;)Ljava/lang/Object;\n18: checkcast #CP // class jakarta/jms/JMSContext\n21: putfield #CP // Field context:Ljakarta/jms/JMSContext;\n24: return'
        self.assertTrue(t.factory_last({key: code}, cls, factory)['statePreparedBeforeFactory'])
        for broken in (code.replace('13: ldc', '13: new'), code.replace('java/util/Objects.requireNonNull:', 'user/Unknown.call:'), code.replace('Field context:', 'Field different:')):
            with self.assertRaises(ValueError):
                t.factory_last({key: broken}, cls, factory)

    def test_group_capacity_is_preallocated_and_not_a_loop_or_default_list(self):
        code = '0: iconst_3\n1: invokespecial #CP // Method java/util/ArrayList."<init>":(I)V\n8: invokestatic #CP // Method SyncRequestConsumers.start:\n'+''.join(str(10+i)+': invokevirtual #CP // Method java/util/ArrayList.add:\n' for i in range(3))
        self.assertEqual(3, t.group_capacity(code)['maximumGroups'])
        for broken in (code.replace('iconst_3', 'iconst_2'), code+'20: goto 8', code+'20: invokevirtual #CP // Method java/util/ArrayList.add:'):
            with self.assertRaises(ValueError):
                t.group_capacity(broken)


if __name__ == '__main__':
    unittest.main()
