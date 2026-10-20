"""Independent synthetic JVM order counterexamples; never load or invoke Production."""
import unittest
from pg6116_http_owner_order import prepared_owner


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


if __name__ == '__main__':
    unittest.main()
