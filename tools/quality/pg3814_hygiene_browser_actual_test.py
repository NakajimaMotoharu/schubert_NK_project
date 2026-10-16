import ast
import unittest
import pg3814_hygiene_browser_actual as tool


class BrowserGuard(unittest.TestCase):
    def test_same_owner_tls_source_and_real_terminal_required(self):
        binding=tool.live()['binding']
        seal={'actualExit':0,'productionSource':tool.SOURCE,'observedOwned':{}}
        terminal={'actualExit':0,'productionSource':tool.SOURCE,'genuineParentDone':True,'proofHashes':{'done.private':'a'*64}}
        raw=tool.guard(seal,terminal,binding);ast.parse(raw)
        for marker in [tool.SOURCE,tool.BOM,binding['activation'],'PG3748','independent_tls_peer','ssl.CERT_REQUIRED','artemis.service','argv_sha','DONE_SHA']:self.assertTrue(marker in raw,marker)
        for change in [{'actualExit':1},{'genuineParentDone':False},{'productionSource':'f'*40}]:
            with self.assertRaises(ValueError):tool.guard(seal,{**terminal,**change},binding)
        self.assertNotIn('PG3420',raw)


if __name__=='__main__':unittest.main()
