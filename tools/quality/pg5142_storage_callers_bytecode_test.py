import unittest
import pg5142_storage_callers_bytecode as role


class CallerBytecode(unittest.TestCase):
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
