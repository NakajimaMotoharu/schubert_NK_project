"""New-source A01 and actual client path qualification, no network."""
import ast
from pathlib import Path
import unittest

R=Path(__file__).resolve().parent


class Test(unittest.TestCase):
    def test_a01_only_scope_names_source_and_ownership_guards_changed(self):
        old=(R/'pg575_a01_when_ready.py').read_text()
        for a,b in (
            ('969d8ded10c0bf5841d9e3a5c531e922caf4a24a','23b14a44b10504172e030bbd6625926bf049fb5c'),
            ('a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b','a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f'),
            ('0.1.0-PG548','0.1.0-PG600'),('PG573','PG605'),
            ('pg573-fresh-parent-v2','pg605-fresh-parent-v2'),('pg573-start-v2','pg605-start-v2'),
            ('pg574-watch-private-v1','pg606-watch-private-v1'),('pg574-observer-v1','pg606-observer-v1'),
            ('PG575-native-a01-v1','PG607-native-a01-v1'),('pg575-chr-a01-native-v1','pg607-chr-a01-native-v1')):
            old=old.replace(a,b)
        new=(R/'pg607_a01_when_ready.py').read_text();self.assertEqual(new,old)
        tree=ast.parse(new)
        guard=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GUARD'for t in n.targets))
        ast.parse(guard)
        self.assertIn('+1800000000',guard)
        self.assertIn("m['InvocationID']==issued['InvocationID']",guard)
        self.assertIn("'sharedCurrentDriver':True",new)
        self.assertIn("'formalAccepted':False",new)

    def test_client_uses_same_new_guard_but_independent_unchanged_oracles(self):
        old=(R/'pg576_capture_client.py').read_text()
        for a,b in (('pg575_a01_when_ready','pg607_a01_when_ready'),('pg575-chr-a01-native-v1','pg607-chr-a01-native-v1'),
                    ('pg576-client-v1','pg608-client-v1'),('PG576-client-v1','PG608-client-v1'),
                    ('969d8ded10c0bf5841d9e3a5c531e922caf4a24a','23b14a44b10504172e030bbd6625926bf049fb5c')):
            old=old.replace(a,b)
        new=(R/'pg608_capture_client.py').read_text();self.assertEqual(new,old);ast.parse(new)
        self.assertIn("pg576_client_oracle.py",new);self.assertIn('pg564_log_session_oracle.py',new)
        self.assertIn("root/'request-reserved.private.json'",new)
        self.assertIn("logs[0]['details']['responseBytes']==len(body)",new)


if __name__=='__main__':unittest.main()
