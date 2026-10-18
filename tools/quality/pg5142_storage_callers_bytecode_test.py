import unittest
import pg5142_storage_callers_bytecode as role


class CallerBytecode(unittest.TestCase):
    def test_static_initializer_never_belongs_to_preceding_factory_method(self):
        raw='  private Object factory();\n    Code:\n       0: invokeinterface #1 // Io.open:\n       5: areturn\n  static {};\n    Code:\n       0: new #2 // an initializer\n       3: return\n  public void next();\n    Code:\n       0: return\n'
        methods=role.bytecode.methods(raw)
        self.assertEqual(len(methods),3)
        self.assertEqual(methods[1]['header'],'static {};')
        self.assertEqual(role.tail(methods[0],'Io.open:'),[5])
        self.assertEqual(methods[2]['ops'],[(0,'return','')])

    def test_raw_factory_return_rejects_every_post_acquisition_fault_boundary(self):
        valid={'ops':[(0,'invokeinterface','Io.open:'),(5,'areturn','')]}
        self.assertEqual(role.tail(valid,'Io.open:'),[5])
        for op in ('ldc','invokestatic','checkcast','invokedynamic','new','astore_1'):
            bad={'ops':[valid['ops'][0],(5,op,'post-acquisition processing'),(8,'areturn','')]}
            with self.assertRaises(ValueError):role.tail(bad,'Io.open:')

    def test_all_ports_are_ordered_before_protection_and_legacy_sites_rejected(self):
        ops=[(0,'invokedynamic','ResourceScope$Acquire;'),(5,'invokedynamic','ResourceScope$Release;'),
             (10,'invokedynamic','ResourceScope$OwnedAction;'),(15,'invokestatic','ResourceScope.acquire:')]
        valid=[{'header':'caller','ops':ops}]
        self.assertEqual(role.callers(valid)[0]['portPcs'],[0,5,10])
        for changed in (ops[1:], [ops[1],ops[0],*ops[2:]], [*ops,(18,'invokestatic','ResourceScope.use:')]):
            with self.assertRaises(ValueError):role.callers([{'header':'caller','ops':changed}])


if __name__=='__main__':unittest.main()
