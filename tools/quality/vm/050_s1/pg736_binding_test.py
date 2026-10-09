"""Inert new source snapshot graph: actual current manifest/stop, six roots, no mutator."""
import ast
import unittest
from pg736_current_baseline import source


class BindingTest(unittest.TestCase):
    def test_current_full21_source_and_preserved_six(self):
        raw=source();tree=ast.parse(raw)
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)
                     and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        ast.parse(payload)
        for text in ('pg728-native-stop-v1','3dc7e756a77c066f53c7503f8109564c559475ffda98e157c1eb2b0ee62e5c32',
                     '2aff8ecf3b7d4d15b24a8af0f73a8745','0.1.0-PG715','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5',
                     '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',"'batchRows':534",'len(v)==21'):
            self.assertIn(text,payload)
        for cohort in ('pg664','pg702'):
            for kind in ('tools','verify','existing'):
                self.assertIn(cohort+'-bootstrap-'+kind+'-v1',payload)
        self.assertIn('pg729-terminal-final-v1.exit',raw)
        for forbidden in ('systemctl start','systemctl stop','DELETE FROM','os.unlink(','os.replace('):
            self.assertNotIn(forbidden,payload)


if __name__=='__main__':unittest.main()
