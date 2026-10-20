import ast
import unittest
import pg5834_isolation_qualification as target


class Original3967QualificationTest(unittest.TestCase):
    def test_exact_source_cases_and_eight_core_no_new_execution(self):
        self.assertEqual(12,len(target.added_cases()))
        raw=target.emitted({});values=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        self.assertIn(3967,values);self.assertIn(3955,values);self.assertIn(590,values);self.assertIn(1666,values)
        self.assertNotIn('PG5780',raw);self.assertIn('source-full-PG5832',raw)
        self.assertNotIn('Popen',raw);self.assertNotIn('subprocess.run',raw)
        self.assertEqual(7,len(target.PHYSICAL_KINDS))
        self.assertEqual(8,sum(map(len,target.TARGETS.values())))


if __name__=='__main__':unittest.main()
