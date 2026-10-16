import ast
import copy
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg3830_hygiene_native_catalog as catalog
import pg3832_hygiene_native_qualified as qualified


class NewSourceNative(unittest.TestCase):
    def test_same_source_context_and_no_old_cohort_cache(self):
        binding={'boot':catalog.BOOT.replace('-',''),'run':'11111111-1111-4111-8111-111111111111','cutoff':'2026-10-16T00:42:20.585755Z','activation':'22222222-2222-4222-8222-222222222222','job':'124886','invocation':'a'*32,'start':110588829449}
        live={'actualExit':0,'binding':binding,'productionSource':catalog.SOURCE};terminal={'actualExit':0,'productionSource':catalog.SOURCE,'genuineParentDone':True,'endMonotonicUs':binding['start']+100000000}
        catalog.qualify_context(live,terminal,binding,terminal['endMonotonicUs'])
        for key in binding:
            bad=copy.deepcopy(binding);bad[key]=None
            with self.assertRaises(ValueError):catalog.qualify_context(live,terminal,bad,terminal['endMonotonicUs'])
        for end in [None,True,terminal['endMonotonicUs']+1]:
            with self.assertRaises(ValueError):catalog.qualify_context(live,terminal,binding,end)
        receipt="def completed(*args):raise ValueError('fixture classifier never executed')\n"
        with patch.object(catalog,'current'),patch.object(catalog,'before',return_value='b'*64):raw=catalog.catalog_source(receipt,binding,terminal['endMonotonicUs'])
        self.assertTrue(raw.startswith(receipt+'\n'));self.assertEqual(0,check('SEALS={}\n'+raw,'<whole new native catalog>'))
        for marker in ['len(old)==34','len(selected)==10',catalog.SOURCE,catalog.BOM,'all34BeforeCopiesPreserved',catalog.ONCE]:self.assertTrue(marker in raw,marker)
        server=qualified.server();transport=qualified.source();ast.parse(server);ast.parse(transport)
        for marker in ['PG3734','3714',catalog.SOURCE,'classByteMismatch','NativeSessions571Test','NativePointDominanceTest']:self.assertTrue(marker in server,marker)
        for marker in ['PG3832-native-input-v1.tar','pg3738-hygiene-whole-qualified-v1','pg3830-hygiene-native-catalog-v1']:self.assertTrue(marker in transport,marker)
        for marker in ['PG3412','PG3532','PG2798','old_input','previous=W']:self.assertFalse(marker in server+transport,marker)
        self.assertIn("r=subprocess.run(SSH+['sudo','-n','cat'",transport)


if __name__=='__main__':unittest.main()
