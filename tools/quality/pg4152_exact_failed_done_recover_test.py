import ast
import inspect
import json
import unittest
import pg4152_exact_failed_done_recover as subject


class RecoveryEntryTest(unittest.TestCase):
    def result(self):
        return {'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
                'BOM':'0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
                'boot':'79a3260a-e16d-42bf-942a-b914ed144c28','mode':'recover',
                'oldParentNormal':False,'formalAccepted':False,'oldRoot143StillFailed':True,
                'recoverySixNormal':True,'canonicalEpochRevoked':True,'newScopeNormalClose':True,
                'all33StartupEntriesPreserved':True,'independentPostRequired':True}

    def encode(self,result,units=None):
        expected=['caddy.service','schubert-nk-web.service','schubert-nk-api.service',
                  'schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-cleanup.service']
        return ('\n'.join('SSC287_STOPPED unit='+u+' generationVerified=true'for u in (expected if units is None else units))+'\n'+json.dumps(result)+'\n').encode()

    def test_original_six_and_exact_normal_new_scope_without_formal_or_old_success(self):
        result=self.result();self.assertEqual(result,subject.completed_output(self.encode(result)))

    def test_missing_false_null_foreign_source_and_fake_exit_never_accept(self):
        result=self.result()
        for key in result:
            for bad in [None,'foreign',1]if type(result[key])is not int else[None,False,1]:
                changed=dict(result);changed[key]=bad
                with self.subTest(field=key,value=bad),self.assertRaises(ValueError):subject.completed_output(self.encode(changed))
            changed=dict(result);del changed[key]
            with self.assertRaises(ValueError):subject.completed_output(self.encode(changed))
        for raw in [None,b'',self.encode(result)[:-1],self.encode(result)+b'\n',self.encode(result).replace(b'\n',b'\r\n'),self.encode(result,[]),self.encode(result,list(reversed(subject.ORDER)))]:
            with self.assertRaises(ValueError):subject.completed_output(raw)
        duplicated=self.encode(result).replace(b'"actualExit": 0',b'"actualExit": 0, "actualExit": 0')
        with self.assertRaises(ValueError):subject.completed_output(duplicated)

    def test_entry_has_durable_reservation_and_observer_without_automatic_kill(self):
        raw=inspect.getsource(subject);tree=ast.parse(raw)
        self.assertTrue("OUT.mkdir(mode=0o700)"in raw)
        self.assertTrue("durable(OUT/'start.safe.json'"in raw)
        self.assertTrue("durable(OUT/'ssh.private.json'"in raw)
        self.assertTrue("child.wait()"in raw)
        calls=[n.func.attr for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)]
        self.assertFalse(any(x in calls for x in ['kill','terminate','send_signal']))
        self.assertTrue('post prepared first'in raw)


if __name__=='__main__':unittest.main()
