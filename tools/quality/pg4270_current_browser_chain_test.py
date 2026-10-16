"""Independent finite Browser guard/composite generation; no actual HTTP/login."""
import ast
import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg4270_current_same_owner_browser as actual
import pg4272_current_browser_composite as composite
from pg4260_stable_admission_image import live,before,SOURCE,BOM
from pg3870_current_resume_composite_test import constants


class CurrentChain(unittest.TestCase):
    def test_guard_requires_genuine_same_current_terminal_and_tls(self):
        seal={'actualExit':0,'productionSource':SOURCE,'observedOwned':{},'genuineCompletion':{'genuineRootDone':True,'completionCode':10}}
        term={'actualExit':0,'productionSource':SOURCE,'genuineParentDone':True,'completionCode':10,'proofHashes':{'done.private':'a'*64}}
        with patch.object(actual,'receipt',side_effect=[seal,term]):raw=actual.guard()
        self.assertEqual(check(raw,'<current Browser guard>'),0)
        for value in [SOURCE,BOM,live()['activation'],'ssl.CERT_REQUIRED','independent_tls_peer','DONE_SHA']:self.assertIn(value,raw)
        for changed in [{'genuineParentDone':False},{'completionCode':0},{'productionSource':'f'*40},{'actualExit':1}]:
            with self.subTest(changed=changed):
                with patch.object(actual,'receipt',side_effect=[seal,{**term,**changed}]):
                    with self.assertRaises(ValueError):actual.guard()

    def test_composite_keeps_original_oracles_and_nested_historical_values(self):
        original=composite.root.seal_payload(live(),before())
        chain={'before':{'history':[{'source':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2','text':composite.root.SEAL}]},'after':{},'context':{}}
        result=composite.compose(original,chain,'b'*64)
        self.assertEqual(check(result,'<complete current composite>'),0)
        outer=constants(result);inner=constants(outer['ORACLE'])
        self.assertEqual(inner['CHAIN'],chain)
        self.assertEqual(inner['ROOT_ORACLE'],constants(original)['ORACLE'])
        self.assertEqual(outer['GUARD'],constants(original)['GUARD'])
        root_hash=next(ast.literal_eval(n.value)for n in ast.parse(outer['ORACLE']).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROOT_SHA'for t in n.targets))
        self.assertEqual(root_hash,'b'*64)
        save=[n for n in ast.parse(result).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SAVE'for t in n.targets)][-1]
        self.assertIn(composite.SLOT,ast.unparse(save))


if __name__=='__main__':unittest.main()
