import ast
import unittest
from pg1341_published_eight_native_counter import catalog,code,BEFORE,AFTER

class CurrentEightNativeQualificationTest(unittest.TestCase):
    def test_actual_catalog_and_sent_session_provenance_and_frozen_host(self):
        cat=catalog();compile(cat,'<actual catalog>','exec')
        names={'backup/backup.exec':'a'*64,'cleanup/cleanup.exec':'a'*64,'expiry/expiry.exec':'a'*64,'parent/parent.exec':'a'*64,
          'ordinary-api193/'+('a'*32)+'.terminal.exec':'a'*64,'root-api193/'+('a'*32)+'.before-exec.exec':'a'*64,
          'ordinary-web193/'+('b'*32)+'.terminal.exec':'a'*64,'root-web193/'+('b'*32)+'.before-exec.exec':'a'*64}
        text=code(names);tree=ast.parse(text)
        payload=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        compile(payload,'<actual current session selection>','exec')
        for piece in [BEFORE,AFTER,'pg1334-native-stop-v1','73654946447','75132489604',"'120359'",'400b2e34105149ff8f3a11c21da0be6a']:
            self.assertTrue(piece in payload,piece)
        for piece in ['pg1279-held-channel-six-host-v1',"tests']==3569",'pg1340-published-terminal-post-v4','PG1341-published-eight-native-v1','classByteMismatch']:
            self.assertTrue(piece in text,piece)
        self.assertTrue('pg1018'not in text)
        self.assertTrue('names.extend'not in payload.split("for name,unit in names:")[1])
        self.assertTrue('ordinary-inspector196'in text)
        for bad in [None,{},dict(names,foreign='a'*64)]:
            with self.assertRaises(ValueError):code(bad)

if __name__=='__main__':unittest.main()
