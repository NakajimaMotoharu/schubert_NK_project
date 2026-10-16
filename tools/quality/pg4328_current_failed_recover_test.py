"""Independent complete six-unit receipt and guarded entry checks, no runtime execution."""
import ast
import inspect
import json
import unittest
import pg4328_current_failed_recover as s


class ReceiptTest(unittest.TestCase):
    def result(self):
        return {'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','BOM':'0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
          'boot':'79a3260a-e16d-42bf-942a-b914ed144c28','mode':'recover','oldParentNormal':False,'formalAccepted':False,
          'oldRoot143StillFailed':True,'recoverySixNormal':True,'canonicalEpochRevoked':True,'newScopeNormalClose':True,'all37StartupEntriesPreserved':True,'independentPostRequired':True}

    def encode(self,value,units=None):
        names=['caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-cleanup.service']if units is None else units
        return ('\n'.join('SSC291_STOPPED unit='+u+' generationVerified=true'for u in names)+'\n'+json.dumps(value)+'\n').encode()

    def test_exact_complete_current_six_without_old_normalization(self):
        v=self.result();self.assertEqual(s.completed_output(self.encode(v)),v)

    def test_every_wrong_missing_type_partial_or_legacy_receipt_refused(self):
        value=self.result()
        for key in value:
            for bad in [None,'foreign',1]if type(value[key])is not int else[None,False,1]:
                with self.subTest(key=key,bad=bad),self.assertRaises(ValueError):s.completed_output(self.encode({**value,key:bad}))
            v=dict(value);del v[key]
            with self.assertRaises(ValueError):s.completed_output(self.encode(v))
        for raw in [None,b'',self.encode(value)[:-1],self.encode(value)+b'\n',self.encode(value).replace(b'SSC291',b'SSC287'),self.encode(value,[]),self.encode(value).replace(b'\n',b'\r\n')]:
            with self.assertRaises(ValueError):s.completed_output(raw)

    def test_entry_qualifies_design_post_current_bytes_and_no_auto_kill(self):
        raw=inspect.getsource(s);tree=ast.parse(raw)
        for marker in ['clean fixed current operator','whole3717','published current design','same fixed independent post prepared first','complete current qualification','OUT.mkdir(mode=0o700)','child.wait()']:
            self.assertIn(marker,raw)
        calls=[n.func.attr for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)]
        self.assertFalse(any(v in calls for v in ['kill','terminate','send_signal']))


if __name__=='__main__':unittest.main()
