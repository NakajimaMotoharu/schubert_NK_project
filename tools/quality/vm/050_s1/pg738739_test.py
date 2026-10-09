"""Independent actual actor/before/after/VM signature and single-session vectors."""
import ast
import hashlib
import unittest
from pg738_final import source as post
from pg739_native import source as native


class BindingTest(unittest.TestCase):
    def test_post_uses_actual_root_signature_and_timing(self):
        raw=post();tree=ast.parse(raw)
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)
                     and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        ast.parse(payload)
        for text in ('pg737-bootstrap-existing-v1','82316ed36abbedd2f85f1e26ca35cd2f10e4c1ac5c7deabc4454bcc5203257d4',
                     '25e00f13202b08b8db34a8c95b77933ff44cd71d5c37de0fa3cc9aacd5c0609e',
                     '0d42d02df3a44b7bb036140f6cc076cf','138755','130424890693','130426534781','2793207','13042489',
                     'pg715-manifest.sig',"'batchRows':534","initial['currentBootstrapProofs']"):
            self.assertIn(text,payload)
        self.assertNotIn('pg715-manifest-v1.sig',payload)
        self.assertIn('pg738-bootstrap-final-v1',raw)

    def test_native_exact_current_and_session_refusals(self):
        raw=native();env={'__file__':__file__};exec(compile(raw,'<inert current9>', 'exec'),env)
        valid=env['session_valid'];bounds={'lowerMs':1000,'upperMs':2000}
        value={'sessions':1,'sessionIdSha256':hashlib.sha256(b'BOOTSTRAP-0d42d02df3a44b7bb036140f6cc076cf-ordinary').hexdigest(),'startMs':1000,'dumpMs':2000}
        self.assertTrue(valid(value,bounds))
        for key,bad in {'sessions':True,'sessionIdSha256':hashlib.sha256(b'API-0d42d02df3a44b7bb036140f6cc076cf-ordinary').hexdigest(),'startMs':999,'dumpMs':2001}.items():
            self.assertFalse(valid({**value,key:bad},bounds))
        for key in value:
            bad=dict(value);del bad[key];self.assertFalse(valid(bad,bounds))
        for bad in (None,{**value,'dumpMs':999}):self.assertFalse(valid(bad,bounds))
        for text in ('pg738-bootstrap-final-v1','pg713-expiry-six-host-v1','pg730-current-eight-native-v1',
                     '2f575a4bbd2dd3ae83eb493c12aef0899c3702b6f9bf04bdf5bd46449facb500',"'qualifiedSingleSessions':9"):
            self.assertIn(text,raw)
        for old in ('pg680','pg698','pg703','9bd505','d420de','==524'):self.assertNotIn(old,raw)
        self.assertEqual('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',env['SOURCE'])


if __name__=='__main__':unittest.main()
