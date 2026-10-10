import ast
import unittest
from pg1155_native_failed_owner_proof_v3 import payload


class PinNamespaceTest(unittest.TestCase):
    def test_independent_old_and_new_pins(self):
        s=payload();tree=ast.parse(s)
        assignments=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ['FILES','NATIVE_FILES']for t in n.targets)]
        self.assertEqual(len(assignments),2)
        values={n.targets[0].id:ast.literal_eval(n.value)for n in assignments}
        self.assertNotEqual(values['FILES'],values['NATIVE_FILES'])
        self.assertTrue('pg1148_native_role_refs.py'in values['NATIVE_FILES'])
        self.assertFalse('pg1148_native_role_refs.py'in values['FILES'])
        self.assertTrue('for n in NATIVE_FILES'in s)


if __name__=='__main__':unittest.main()
