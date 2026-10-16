"""Independent native scope, immutable receipt and fail-closed prerequisites."""
import copy
import unittest
from pyflakes.api import check,checkPath
import pg4660_current_native_catalog as catalog


class CurrentNative(unittest.TestCase):
    def test_exact_body_roles_and_unmodified_receipt(self):
        receipt='def completed(*args):raise ValueError("immutable negative '+catalog.template.BOOT+' pg2246")'
        binding=catalog.role.admission.live();terminal=catalog.role.actual.receipt(catalog.role.acceptance.TERM)
        raw=catalog.catalog_source(receipt,binding,terminal['endMonotonicUs'])
        self.assertTrue(raw.startswith(receipt+'\n'));body=raw[len(receipt)+1:]
        self.assertNotIn(catalog.template.BOOT,body);self.assertNotIn('pg2246',body)
        self.assertIn("root=base/'pg4652-native-stop-v1'",body)
        self.assertIn('ROOT_START='+str(binding['start']),body);self.assertIn('ROOT_END='+str(terminal['endMonotonicUs']),body)
        self.assertIn('all58BeforeCopiesPreserved',body);self.assertIn('require(len(selected)==10',body)
        self.assertNotIn('currentBootHadNoHistoricalNative',body)
        self.assertIn("issued['oldRunNotResumed']is True",body)
        self.assertEqual(0,check('SEALS={}\n'+raw,'<actual emitted same-source native>'))
        self.assertEqual(0,checkPath(catalog.__file__));self.assertEqual(0,checkPath(__file__))

    def test_prerequisites_reject_foreign_or_incomplete_scope(self):
        post={'actualExit':0,'productionSource':catalog.role.SOURCE,'allClientAdvisoryFlock0':True,'all24UnchangedTwice':True,'allTenUnitsKernelEmpty':True,'normalNewMetadataScopes':True}
        term={'productionSource':catalog.role.SOURCE,'genuineRootDone':True,'completionCode':10}
        catalog.prerequisites(post,term)
        for key in post:
            bad=copy.deepcopy(post);bad.pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):catalog.prerequisites(bad,term)
        for key in term:
            bad=copy.deepcopy(term);bad.pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):catalog.prerequisites(post,bad)


if __name__=='__main__':unittest.main()
