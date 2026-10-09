"""Independent current21 post profile/literal coverage, no VM action."""
import ast
import unittest
import pg687_completed_post as p


class BindingTest(unittest.TestCase):
    def test_full_live21_and_new_signature_no_mutation(self):
        raw = p.source();compile(raw,'<readonly post>','exec')
        node = next(n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'PAYLOAD' for t in n.targets))
        payload = ast.literal_eval(node.value);compile(payload,'<readonly payload>','exec')
        for expected in ('pg685-completed-', 'pg655-native-stop-v1',
                         "'PG631'if MODE=='verify'else'PG682'", '==514', "'fields':21",
                         'namespace currentBootstrapProofs', "after['dependencies']",
                         "after['parentPid1']", "after['pid1Stop']", "after['caddyPre']",
                         "after['namespace']", "after['currentBootstrapProofs']", "after['approval']",
                         '095f6d1d7f8442b7b2b44ae59a4314f5', '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480',
                         '9bd50536f692610036a0ed8b83e0a8b35fe2a66f', 'resources0'):
            self.assertIn(expected,payload)
        for forbidden in ('os.replace(', 'os.chmod(', 'systemctl start', 'systemctl stop', 'daemon-reload'):
            self.assertNotIn(forbidden,payload)


if __name__ == '__main__':
    unittest.main()
