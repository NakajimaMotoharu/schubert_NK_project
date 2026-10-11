"""Independent Java/wrapper candidate vectors and actual sent predicate."""
import ast
import unittest
import pg1351_bootstrap_failed_owner_proof_v2 as p

class Test(unittest.TestCase):
    def test_exe_and_argv_selected_together(self):
        argv = b'/opt/jdk-25.0.4/bin/java\0-cp\0FIXED\0Pg1348BootstrapExisting\0verify\0'
        self.assertTrue(p.candidate(argv, '/opt/jdk-25.0.4/bin/java'))
        for exe in ('/usr/bin/sudo', '/usr/bin/ssh', '/usr/bin/python3.14', '', None):
            self.assertFalse(p.candidate(argv, exe))
        for bad in (None, b'', b'Pg1348BootstrapExisting verify', argv.replace(b'verify', b'execute')):
            self.assertFalse(p.candidate(bad, '/opt/jdk-25.0.4/bin/java'))
        raw = p.payload(dict.fromkeys(p.prior.prior.previous.transport.previous.SEALS, 'b' * 64))
        parsed = ast.parse(raw)
        predicate = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'candidate')
        scope = {};exec(compile(ast.Module(body=[predicate], type_ignores=[]), '<sent candidate>', 'exec'), scope)
        self.assertTrue(scope['candidate'](argv, '/opt/jdk-25.0.4/bin/java'))
        self.assertFalse(scope['candidate'](argv, '/usr/bin/sudo'))
        self.assertIn('len(candidates)==1', raw)
        self.assertNotIn('pidfd_send_signal', raw)

if __name__ == '__main__':
    unittest.main()
