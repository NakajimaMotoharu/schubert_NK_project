import ast
import unittest
import pg5862_terminal_qualification as target


class Independent3971ReaderTest(unittest.TestCase):
    def test_all_original_and_current_identities_without_execution(self):
        self.assertEqual(4,len(target.added_cases()))
        self.assertEqual(12,len(target.PHYSICAL_KINDS))
        raw=target.emitted({});constants=[n.value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Constant)]
        for n in(3971,3967,592,1666,1654):self.assertIn(n,constants)
        self.assertNotIn('PG5808',raw);self.assertIn('source-full-PG5860',raw)
        self.assertNotIn('Popen',raw);self.assertNotIn('subprocess.run',raw)
        self.assertIn("old = base / 'runs/PG5832-six-v1'",raw)
        self.assertEqual(8,sum(map(len,target.previous.TARGETS.values())))


if __name__=='__main__':unittest.main()
