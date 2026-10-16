import ast
import unittest
import pg3762_hygiene_unused_post as p


class Post(unittest.TestCase):
    def test_independent_complete_payload_has_no_operation_or_old_native_credit(self):
        raw=p.payload();tree=ast.parse(raw)
        self.assertEqual(1,sum(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='print'for n in tree.body))
        for s in ['all24TablesEqualTwice','configuration32EveryFieldUnchanged','unitFilesActual',"cfg==oldcfg",'native34Preserved','0.1.0-PG3748','0.1.0-PG3420',p.role.BEFORE,'candidateNativeCredit']:self.assertIn(s,raw)
        for s in ['start-unit','stop-unit','daemon-reload','pg_restore','poweroff']:self.assertNotIn(s,raw)


if __name__=='__main__':unittest.main()
