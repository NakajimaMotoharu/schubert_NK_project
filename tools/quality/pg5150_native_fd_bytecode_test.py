import unittest
import pg5150_native_fd_bytecode as role


class NativeProof(unittest.TestCase):
    def test_preallocation_and_exact_factory_count_cannot_be_inferred_from_constructor_alone(self):
        valid=[{'header':'factory','ops':[(0,'new','File$Owner'),(3,'dup',''),
               (4,'invokespecial','File$Owner."<init>":(Supplier)V'),(7,'areturn','')]}]
        self.assertEqual(role.constructor_factories(valid,'File$Owner',1)[0]['allocationPc'],0)
        for methods,count in ((valid,2),([{'header':'bad','ops':valid[0]['ops'][1:]}],1)):
            with self.assertRaises(ValueError):role.constructor_factories(methods,'File$Owner',count)

    def test_nested_debug_equivalence_retains_every_opcode_handler_and_literal(self):
        original=[{'header':'void close();','ops':[(0,'ldc','#1 // String literal'),(2,'return','')],'handlers':[]}]
        changed=[{'header':'void close();','ops':[(0,'ldc','#92    // String literal'),(2,'return','')],'handlers':[]}]
        role.same_methods(original,changed)
        for row in ({**changed[0],'ops':[(0,'ldc','#92 // String literal '),(2,'return','')]},
                    {**changed[0],'handlers':[(0,2,2,'any')]},
                    {**changed[0],'header':'void other();'}):
            with self.assertRaises(ValueError):role.same_methods(original,[row])


if __name__=='__main__':unittest.main()
