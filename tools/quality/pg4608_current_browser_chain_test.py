"""Pure same-owner guard/composite oracles; no actual login, DB or Root operations."""
import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4604_current_same_owner_browser as actual
import pg4606_current_browser_composite as composite
import pg4602_current_browser_ready as ready
import pg4584_current_admission_image as admission
import pg4586_current_independent_acceptance as root
import pg4610_current_parent_progress_read as progress
from pg3870_current_resume_composite_test import constants


class BrowserChain(unittest.TestCase):
    def test_current_guard_real_done_source_bom_tls_and_rejections(self):
        seal={'actualExit':0,'productionSource':admission.SOURCE,'observedOwned':{},'genuineCompletion':{'genuineRootDone':True,'completionCode':10}}
        term={'actualExit':0,'productionSource':admission.SOURCE,'genuineParentDone':True,'completionCode':10,'proofHashes':{'done.private':'a'*64}}
        with patch.object(actual,'receipt',side_effect=[seal,term]):raw=actual.guard()
        self.assertEqual(0,check(raw,'<same964e Browser guard>'))
        for item in [admission.SOURCE,admission.BOM,admission.live()['activation'],'PG4432','ssl.CERT_REQUIRED','independent_tls_peer','DONE_SHA']:self.assertIn(item,raw)
        for wrong in [{'genuineParentDone':False},{'completionCode':0},{'productionSource':'f'*40},{'actualExit':1}]:
            with self.subTest(wrong=wrong),patch.object(actual,'receipt',side_effect=[seal,{**term,**wrong}]),self.assertRaises(ValueError):actual.guard()

    def test_frozen_nested_root_oracles_and_historical_rows_never_rebound(self):
        raw=root.seal_payload(admission.live(),admission.before())
        chain={'before':{'history':[{'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','text':root.SEAL}]},'after':{},'context':{}}
        result=composite.compose(raw,chain,'b'*64)
        self.assertEqual(0,check(result,'<same-source composite>'))
        outer=constants(result);inner=constants(outer['ORACLE'])
        self.assertEqual(chain,inner['CHAIN']);self.assertEqual(constants(raw)['ORACLE'],inner['ROOT_ORACLE']);self.assertEqual(constants(raw)['GUARD'],outer['GUARD'])
        root_hash=next(ast.literal_eval(n.value)for n in ast.parse(outer['ORACLE']).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROOT_SHA'for t in n.targets))
        self.assertEqual('b'*64,root_hash)
        self.assertIn(composite.SLOT,ast.unparse([n for n in ast.parse(result).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)][-1]))

    def test_ready_identity_only_inputs_and_current_progress_readonly_closure(self):
        ns=ready.namespace();self.assertEqual(admission.SOURCE,ns['SOURCE'])
        self.assertEqual(ready.PINNED,ns['PINNED'])
        for name in ns['JAVA_INPUTS']:
            if name in ns['SHARED']:continue
            raw=(ns['ROOT']/name).read_text();self.assertEqual(1,raw.count('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'))
            rebound=raw.replace('a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25',admission.SOURCE)
            self.assertEqual(raw,rebound.replace(admission.SOURCE,'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'))
        raw=progress.payload({});self.assertEqual(0,check(raw,'<same parent all ten read>'))
        self.assertIn(admission.SOURCE,raw);self.assertIn('observedUnits',raw)
        for forbidden in ['jcmd',"'start'","'stop'","'restart'",'os.kill','deadline+=']:self.assertNotIn(forbidden,raw)
        for name in ['pg4602_current_browser_ready.py','pg4604_current_same_owner_browser.py','pg4606_current_browser_composite.py','pg4608_current_browser_chain_test.py','pg4610_current_parent_progress_read.py']:
            self.assertEqual(0,checkPath('tools/quality/'+name))


if __name__=='__main__':unittest.main()
