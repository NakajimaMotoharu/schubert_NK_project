import ast
import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5432_current_vm_reauthentication as entry


class FreshVmRead(unittest.TestCase):
    def test_current187_signature_and_exact_guest_binding_have_no_mutating_fallback(self):
        raw=entry.payload();self.assertEqual(check(raw,'<complete fresh readonly>'),0)
        self.assertIn(entry.CURRENT,raw);self.assertIn(entry.CURRENT_BOM,raw)
        self.assertIn('pg4980-manifest.sig',raw);self.assertIn('79a3260a-e16d-42bf-942a-b914ed144c28',raw)
        self.assertIn('bootstrap-admin',raw);self.assertIn("'candidatePlaced':False",raw)
        self.assertNotIn('0.1.0-PG2802',raw);self.assertNotIn("'-sign'",raw)
        tree=ast.parse(raw)
        command_words=[node.value for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str)]
        self.assertFalse({'start','stop','restart','daemon-reload','poweroff','reboot','migrate'}&set(command_words))
        self.assertIn('authenticate_host()',inspect.getsource(entry.main))
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
