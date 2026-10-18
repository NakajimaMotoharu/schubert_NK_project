import unittest
import pg5250_startup_view_bytecode as loops


class CloseDirection(unittest.TestCase):
    def method(self,step):
        return {'header':'void drain(int);','ops':[(0,'aload_0',''),
            (1,'invokeinterface','DirectoryCalls.close:(I)V'),(4,'iinc',f'1, {step}'),
            (7,'goto','0'),(10,'return','')],
            'handlers':[(1,4,10,kind) for kind in ('Class dev/codex/schubert/nk/storage/StorageIoException',
                'Class java/lang/RuntimeException','Class java/lang/Error')]}

    def test_default_reverse_and_explicit_fifo_never_interchange(self):
        self.assertEqual(loops.native_loop(self.method(-1),set())['direction'],-1)
        self.assertEqual(loops.native_loop(self.method(1),set(),direction=1)['direction'],1)
        with self.assertRaises(ValueError):loops.native_loop(self.method(1),set())
        with self.assertRaises(ValueError):loops.native_loop(self.method(-1),set(),direction=1)
        for direction in (False,0,2):
            with self.assertRaises(ValueError):loops.native_loop({},set(),direction=direction)

    def test_heap_or_non_native_suppression_inspection_during_drain_is_refused(self):
        for opcode,arg in [('new','exception'),('invokedynamic','callback'),
            ('invokevirtual','java/lang/Throwable.getSuppressed:()[Ljava/lang/Throwable;')]:
            method=self.method(1);method['ops'].insert(0,(0,opcode,arg))
            with self.assertRaises(ValueError):loops.native_loop(method,set(),direction=1)


if __name__=='__main__':unittest.main()
