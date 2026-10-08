"""SSC227 closed source/run/ABI and external dependency labels; no VM mutation."""
import ast
from pathlib import Path
import unittest

R=Path(__file__).resolve().parent


def constant(path,name):
    node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
    return ast.literal_eval(node.value)


class Binding(unittest.TestCase):
    def test_external_versions_preserved_new_host_and_guest_differ_intentionally(self):
        old=R/'pg549_completed_native_v5.py';new=R/'pg604_completed_native.py'
        self.assertEqual(constant(old,'prefixes')[1:],constant(new,'PREFIXES')[1:])
        self.assertEqual(constant(old,'host_prefixes'),constant(new,'HOST_PREFIXES'))
        self.assertEqual('pg604-completed-tools-v1',constant(new,'PREFIXES')[0])
        self.assertIn('0.1.0-PG548/operations/batch.jar',new.read_text())
        compile_script=(R/'pg603_compile_contract_v1.sh').read_text()
        self.assertIn('pg599-candidate-bootstrap-six-host-v1',compile_script)
        self.assertIn('set -euC',compile_script)

    def test_golden_complete_ids_and_limits_are_not_prefix_substitutions(self):
        java=(R/'Pg604CompletedDeployment.java').read_text()
        for literal in ('b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e','57f0e73d-d334-4882-9284-04246011da54','2026-10-08T07:36:21.802335Z','2026-10-08T08:02:11.015742Z','23b14a44b10504172e030bbd6625926bf049fb5c','a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f'):
            self.assertIn(literal,java)
        self.assertNotIn('57f0e73d-5b77',java)
        body=java[java.index('public static void main'):]
        self.assertLess(body.index('var refs=new References'),body.index('immutableCandidate();'))
        self.assertLess(body.index('immutableCandidate();'),body.index('phase="CANDIDATE_TYPED_BOM"'))
        self.assertLess(body.index('phase="CANDIDATE_TYPED_BOM"'),body.index('publish(next)'))
        self.assertIn('if(result==0)require',java)
        self.assertIn('else Pg387TrustedDeployment.freezeCandidate();',java)
        refs=(R/'pg604_completed_refs.py').read_text()
        self.assertIn('PG604-completed-codeonly',refs)
        self.assertIn('str(backend)+" and a.datname',refs)
        self.assertIn("same_value(value['rows'],baseline['rows'])",refs)
        self.assertIn("sources({u:show(u,{'FragmentPath','DropInPaths'})",refs)
        self.assertIn('for fd in reversed(fds):os.close(fd)',refs)


if __name__=='__main__':unittest.main()
