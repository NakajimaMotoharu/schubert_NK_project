"""Independent synthetic JVM order counterexamples; never load or invoke Production."""
import unittest
from pg6116_http_owner_order import prepared_owner, resolved_body


class Order(unittest.TestCase):
    CODE = '''  private Example(java.util.function.Supplier);
    Code:
      0: aload_0
      1: new #1 // class java/lang/Object
      4: putfield #2 // Field lock:Ljava/lang/Object;
      7: invokeinterface #3, 1 // InterfaceMethod java/util/function/Supplier.get:()Ljava/lang/Object;
     12: ldc #4 // String server
     14: invokestatic #5 // Method java/util/Objects.requireNonNull:(Ljava/lang/Object;Ljava/lang/String;)Ljava/lang/Object;
     17: checkcast #6 // class Server
     20: putfield #7 // Field server:LServer;
     23: return'''

    def verify(self, code):
        return prepared_owner({'  private Example(java.util.function.Supplier);': code}, 'Example',
                              ['lock'], 'java/util/function/Supplier.get:', 'server')

    def test_prepared_state_and_final_store(self):
        actual = self.verify(self.CODE)
        self.assertEqual(7, actual['factoryOffset'])
        self.assertEqual(['ldc', 'invokestatic', 'checkcast', 'putfield', 'return'], actual['postAcquireOpcodes'])

    def test_allocation_callback_missing_or_repeated_acquisition_rejected(self):
        for code in (
            self.CODE.replace('23: return', '22: new #9 // class Unexpected\n     23: return'),
            self.CODE.replace('23: return', '22: invokevirtual #9 // Method callback:()V\n     23: return'),
            self.CODE.replace('// Field lock:', '// Field unrelated:'),
            self.CODE.replace('23: return', '22: invokeinterface #8, 1 // InterfaceMethod java/util/function/Supplier.get:()Ljava/lang/Object;\n     23: return'),
            self.CODE.replace('// Field server:', '// Field wrong:'),
        ):
            with self.subTest(code=code), self.assertRaises(ValueError):
                self.verify(code)

    def test_bootstrap_index_is_resolved_with_actual_handle_and_arguments(self):
        code = '  private void x();\n    Code:\n       0: invokedynamic #CP, 0 // InvokeDynamic #1:apply:()Ljava/lang/Object;\n       5: return'
        verbose = '''BootstrapMethods:
  1: #20 REF_invokeStatic LambdaMetafactory.metafactory
    Method arguments:
      #21 ()V
      #22 REF_invokeVirtual Example.respond:()V
InnerClasses:
'''
        shifted = verbose.replace('  1:', '  0:').replace('#20 ', '#50 ').replace('#21 ', '#51 ').replace('#22 ', '#52 ')
        self.assertEqual(resolved_body(code, verbose), resolved_body(code.replace('Dynamic #1:', 'Dynamic #0:'), shifted))
        self.assertNotEqual(resolved_body(code, verbose), resolved_body(code, verbose.replace('Example.respond', 'Example.other')))
        with self.assertRaises(ValueError):
            resolved_body(code.replace('Dynamic #1:', 'Dynamic #9:'), verbose)


if __name__ == '__main__':
    unittest.main()
