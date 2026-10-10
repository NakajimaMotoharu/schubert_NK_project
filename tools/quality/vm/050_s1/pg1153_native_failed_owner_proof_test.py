import ast
import unittest
from pg1153_native_failed_owner_proof import payload


class OwnerProofTest(unittest.TestCase):
    def test_fixed_exact_generation_and_immutable_original(self):
        s=payload();tree=ast.parse(s)
        for part in ['JAVA=410279;CHILD=410308','4653404','4653520','PG1148-fixed-recovery','owned_snapshot=whole()','cfd139237f179e7531b94d28c1570c07af9612b476857f3eb479d9a732a7c0b9','current():','nativeMutation0']:
            self.assertTrue(part in s,part)
        self.assertFalse('pidfd_send_signal'in s);self.assertFalse('systemctl stop'in s)
        def walk(n):
            if isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.Lambda)):return []
            return ([n]if isinstance(n,ast.Name)and isinstance(n.ctx,ast.Store)and n.id=='before'else [])+[x for c in ast.iter_child_nodes(n)for x in walk(c)]
        self.assertEqual(len(walk(tree)),1)


if __name__=='__main__':unittest.main()
