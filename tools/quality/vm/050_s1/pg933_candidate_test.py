"""Independent literal delta and build/source/pin contract, signing not performed by tests."""
import ast,unittest
import pg931_candidate_contract as p
from pg932_candidate_build import source
class Test(unittest.TestCase):
    def test_literal_four_classes_only(self):
        literal={'bootstrap':{'dev/codex/schubert/nk/bootstrap/ChildStartupContext.class','dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo.class'},'api':{'dev/codex/schubert/nk/api/file/InspectorApplication.class'},'batch':{'dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.class'}}
        self.assertEqual(literal,p.CHANGED);self.assertEqual({},p.ADDED)
        old={m:{'stable.class':'0'*64}for m in p.MODULES};new={m:dict(v)for m,v in old.items()}
        for module,names in literal.items():
            for name in names:old[module][name]='1'*64;new[module][name]='2'*64
        self.assertEqual(10,p.verify_delta(old,new))
        for module,names in literal.items():
            for name in names:
                wrong={m:dict(v)for m,v in new.items()};wrong[module][name]='1'*64
                with self.assertRaises(ValueError):p.verify_delta(old,wrong)
        for module in p.MODULES:
            for extra in (False,True):
                wrong={m:dict(v)for m,v in new.items()};wrong[module]['foreign.class'if extra else 'stable.class']='3'*64
                with self.assertRaises(ValueError):p.verify_delta(old,wrong)
    def test_signed_candidate_pins_and_new_only_paths(self):
        raw=source();tree=ast.parse(raw);data={}
        for n in tree.body:
            if isinstance(n,ast.Assign)and isinstance(n.value,ast.Constant):
                for t in n.targets:
                    if isinstance(t,ast.Name):data[t.id]=n.value.value
        self.assertEqual('40ef6e894573d2ffab1d1732124960f9c98d5f97',data['SOURCE']);self.assertEqual('e01612fcd7f2752df5ae0836b78538fd5e87f120',data['OLD_SOURCE'])
        for marker in ("OLD = W / 'pg862-release-v1'","FROZEN = W / 'pg926-body-six-host-v1'","NEXT = W / 'pg932-release-v1'","SIG = P / 'pg932-manifest-v1.sig'","assert not NEXT.exists() and not SIG.exists()","'changedClasses': 4","'artifacts': 187","'tests': 3560, 'suites': 523","'guestMutations0': True","'candidateNotDeployed': True","'formalAccepted': False"):
            self.assertIn(marker,raw)
        self.assertNotIn('ssh',raw);self.assertNotIn('systemctl',raw)
if __name__=='__main__':unittest.main()
