"""Independent new archive/root-seal profile only, no VM action."""
import ast
import unittest
import pg689_backup_preserve as p


class BindingTest(unittest.TestCase):
    def test_literal_current_backup_source_and_new_only(self):
        raw=p.source();compile(raw,'<current archive>','exec')
        node=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
        value=ast.literal_eval(node.value);compile(value,'<private archive>','exec')
        for text in ('pg685-completed-activate-v1','f69b52ee024ca670723d077dd34b20a2f62803f6575e4ba02d886d395f124187',
                     '9bd50536f692610036a0ed8b83e0a8b35fe2a66f',"'eligibleBundles':7"):
            self.assertIn(text,value)
        self.assertIn('pg689-prior-seven-backups.private.tar',raw)
        self.assertIn('len(directories)==12 and len(regular)==35 and len(members)==47',raw)
        for old in ('pg626','pg624','72fb744','11675ec0'):self.assertNotIn(old,raw)
        for forbidden in ('systemctl start','os.unlink(', 'os.replace(', 'DELETE FROM'):
            self.assertNotIn(forbidden,value)


if __name__=='__main__':unittest.main()
