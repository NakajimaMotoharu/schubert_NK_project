"""Exact independent stage/post/sig/row/private roots/immutable metadata binding."""
import ast
import unittest
from pg754_stage_candidate import source as stage
from pg755_completed_post import source as post
from pg752_native import source as native
import pg752_sources as profile


class Test(unittest.TestCase):
    def test_sequential_markers_resolve_all_surfaces_and_new_v2_only(self):
        fields=(profile.java(),profile.java_test(),profile.receipt(),profile.contract(),profile.refs(),
                profile.compile_script(),native(),stage(),post())
        for raw in fields:
            self.assertNotIn('NEXT_RELEASE_752',raw)
            self.assertNotIn('NEXT_SOURCE_752',raw)
            self.assertNotIn('NEXT_BOM_752',raw)
            self.assertNotIn('pg752-completed-tools-v1',raw)
        self.assertEqual('0.1.0-PG750 0.1.0-PG715',profile.bind('0.1.0-PG715 0.1.0-PG682'))
        self.assertEqual('8d4b68b4f1449932ebe506aaf08e584bbfea8dd2 1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',profile.bind('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172 9bd50536f692610036a0ed8b83e0a8b35fe2a66f'))
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG750',profile.java())
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG715',profile.java())
        self.assertIn(profile.SOURCE,profile.java())
        self.assertIn(profile.DIGEST,profile.java())
    def payload(self,raw):
        tree=ast.parse(raw)
        node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        value=ast.literal_eval(node.value);ast.parse(value);return value

    def test_unused_release_and_nine_private_roots_before_current_switch(self):
        value=self.payload(stage())
        for s in ('pg751-completed-baseline-v1','8c722e15a3bc9b6e311fe69cef0cd2aa3a954e87586c861cafa7279cd3dab6c0',
                  'pg750-manifest.sig','pg750-manifest-v1.sig','0.1.0-PG715','0.1.0-PG750','==534',
                  'before=protected()','assert protected()==before'):
            self.assertIn(s,value)
        for group in ('664','702','737'):
            for kind in ('tools','verify','existing'):self.assertIn('pg'+group+'-bootstrap-'+kind+'-v1',value)

    def test_independent_post_and_actual_immutable_sources(self):
        value=self.payload(post())
        for s in ('pg752-completed-',"'PG715'if MODE=='verify'else'PG750'","'fields':21",'==534',"'batchRows':534",'resources0',
                  'pg737-bootstrap-existing-v1','pg728-native-stop-v1','2aff8ecf3b7d4d15b24a8af0f73a8745'):
            self.assertIn(s,value)
        for forbidden in ('os.replace(', 'systemctl start','systemctl stop','daemon-reload'):
            self.assertNotIn(forbidden,value)
        raw=native();ast.parse(raw)
        self.assertIn('pg752-frozen-v2.safe.json',raw)
        self.assertIn("files[name] = W/'pg752-completed-tools-v2'/name",raw)
        self.assertIn('pg464-code-tools-v2',raw)


if __name__=='__main__':unittest.main()
