import ast
import unittest
from pyflakes.api import check,checkPath
import pg5602_current_vm_reauthentication as entry


class FreshCurrentIdentity(unittest.TestCase):
    def test_exact_deployed_and_candidate_roles_never_cascade(self):
        raw=entry.payload('c'*64)
        self.assertIn("data['source']['commit']=='"+entry.CURRENT+"'",raw)
        self.assertIn("'candidateSource':'"+entry.CANDIDATE+"'",raw)
        self.assertIn('0.1.0-PG5430',raw);self.assertIn('pg5430-manifest.sig',raw)
        self.assertIn('bootstrap-admin',raw);self.assertIn("'candidatePlaced':False",raw)
        self.assertNotIn(entry.previous.CURRENT,raw);self.assertNotIn('0.1.0-PG4980',raw)
        self.assertEqual(check(raw,'<fresh RO only>'),0)
        self.assertNotIn('systemctl start',raw);self.assertNotIn('INSERT',raw)
        calls=[n for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in('unlink','rename','replace','write_text','write_bytes')]
        self.assertEqual(calls,[])

    def test_missing_or_noncanonical_candidate_bom_refused(self):
        for value in(None,'','C'*64,'c'*63,'../../release'):
            with self.assertRaises(ValueError):entry.payload(value)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
