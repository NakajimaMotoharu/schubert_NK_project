"""Independent exact current dependency matrix, guards and complete new transport identity."""
import inspect
import unittest
from pyflakes.api import checkPath
import pg4932_current_bootstrap_test as previous
import pg5082_current_bootstrap_sources as role
import pg5084_current_bootstrap_compile as compiler
import pg5086_current_bootstrap_dispatch as dispatch
import pg4822_new_current_bootstrap_compile as compile_template


def matrix():
    raw = inspect.getsource(previous.CurrentBootstrap)
    changes = [('Pg4932', 'Pg5082'), ('pg4932', 'pg5082'), ('PG4932', 'PG5082'),
               ('==884', '==894'), ('199849150395', '306951851178'),
               ('7fe303d625de4a83b23d23fca4eca2bb', 'abe95f4c09b849a8a2304e94a3cb8165'),
               ('7bae6042-b79f-4fb2-9d9f-edf47b428cbe', 'b683da46-df42-4e52-8379-5ac8bfbca0ae'),
               ('4e220f3b-fbb4-411c-b5c4-7ca1371daa20', '15322936-6512-4550-8123-a3ef688dc1da'),
               ('pg4916', 'pg5060'), ('actual4930', 'actual5080'),
               ('pg4918', 'pg5062'), ('pg4860', 'pg4980'), ('PG4860', 'PG4980'),
               ('pg4934', 'pg5084'),
               ('inspect.getsource(compiler.previous.previous)', 'inspect.getsource(compile_template)')]
    for old, new in changes:
        raw = raw.replace(old, new)
    ns = {**vars(previous), '__file__': __file__, 'role': role, 'compiler': compiler,
          'dispatch': dispatch, 'compile_template': compile_template}
    exec(compile(raw, '<current independent existing20 matrix>', 'exec'), ns)
    return ns['CurrentBootstrap']


CurrentBootstrap = matrix()


class CompleteTransport(unittest.TestCase):
    def test_full_stage_uses_actual_release_not_old_namespace(self):
        for value in ('/opt/schubert-nk/releases/0.1.0-PG4980', 'BOM', 'REMOTE', 'GUEST', 'ARCHIVE', 'FILES'):
            self.assertIn(value, dispatch.STAGE)
        for value in ('PG4860', 'PG4702'):
            self.assertNotIn(value, dispatch.STAGE)
        ns = dispatch.namespace()
        self.assertIs(ns['authenticate_host'], role.before.admission.authenticate_host)
        self.assertEqual(role.SOURCE, compiler.role.SOURCE)
        self.assertEqual(0, checkPath(__file__))
        self.assertEqual(0, checkPath(role.__file__))
        self.assertEqual(0, checkPath(compiler.__file__))
        self.assertEqual(0, checkPath(dispatch.__file__))


if __name__ == '__main__':
    unittest.main()
