"""Transport pure checks, not Production PT credit."""
import ast
import unittest
import pg3680_typed_inode_related as p


class Contract(unittest.TestCase):
    def test_current_exact_group_and_no_original_operator_replay(self):
        raw=p.server_source();tree=ast.parse(raw)
        self.assertEqual(33,sum(sum(v.values())for v in p.CLASSES.values()))
        self.assertEqual(6,sum(len(v)for v in p.CLASSES.values()))
        self.assertIn('source-full-PG3412',raw)
        self.assertNotIn('PG3348',raw)
        self.assertIn('every Main/resource/debug member identical required',raw)
        strings=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)and isinstance(n.value,str)]
        self.assertIn('whole typed metadata method executed and every branch required',strings)
        self.assertNotIn('-DfailIfNoTests=false',strings)
        self.assertEqual(3,len(p.METHODS))


if __name__=='__main__':unittest.main()
