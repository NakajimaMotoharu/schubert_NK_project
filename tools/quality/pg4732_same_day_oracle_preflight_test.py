"""Emitted before-only tool retains independent oracle and never emits private rows."""
import ast
import unittest
from pyflakes.api import check
import pg4732_same_day_oracle_preflight as target


class BeforeOnly(unittest.TestCase):
    def test_complete_emitted_source_and_no_external_mutation(self):
        raw=target.payload()
        self.assertEqual(0,check(raw,'<before only>'))
        tree=ast.parse(raw)
        calls=[ast.unparse(n.func)for n in ast.walk(tree)if isinstance(n,ast.Call)]
        for forbidden in ['subprocess.run','subprocess.Popen','os.system','systemctl','write_text','write_bytes']:
            self.assertFalse(any(c==forbidden or c.endswith('.'+forbidden)for c in calls),forbidden)
        self.assertIn("now+datetime.timedelta(hours=2)",raw)
        self.assertIn("'f8dff44c321575ecc5eaa14e76bc9db66bda5850c4d5f81f1d85d4b706a4c601'",raw)
        prints=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='print']
        self.assertEqual(1,len(prints))
        output=ast.unparse(prints[0])
        self.assertNotIn("'rows'",output)
        self.assertIn("'projections': projections",output)


if __name__=='__main__':unittest.main()
