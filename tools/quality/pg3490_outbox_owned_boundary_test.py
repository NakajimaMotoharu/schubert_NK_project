import ast
import inspect
import unittest
import tempfile
from pathlib import Path
import pg3490_outbox_owned_sources as role
import pg3494_outbox_owned_dispatch as dispatch
import pg3496_outbox_owned_post as post
from pg1674_critical_management_gate import management_gate


class ExactOwnedBoundaries(unittest.TestCase):
    def test_real_delegated_main_alone_owns_dispatch_and_post_gate(self):
        base = dispatch.old.previous.previous.prior.previous.prior.prior.prior.prior
        self.assertEqual(1, inspect.getsource(base.main).count('with management_gate('))
        self.assertNotIn('with management_gate(', inspect.getsource(dispatch.main))
        self.assertIn('management_gate', post.entry().__code__.co_names)
        with tempfile.TemporaryDirectory(prefix='pg3494-gate-') as temporary:
            path = Path(temporary) / 'private.lock'
            with management_gate(path):
                with self.assertRaises(BlockingIOError):
                    with management_gate(path):
                        self.fail('separate file descriptions must not nest this lock')
    def test_factory_uses_actual_new_live_terminal_seal_and_parent18(self):
        ns = role.namespace()
        self.assertEqual(role.TOOLS, ns['TOOLS'])
        self.assertEqual(role.SOURCE, ns['SOURCE'])
        for name in ['context', 'emit_receipt', 'emit', 'sources']:
            self.assertIn(name, ns)
        raw = '\n'.join(role.bind(inspect.getsource(fn)) for fn in [role.old.previous.context,
                         role.old.previous.emit_receipt, role.old.previous.emit, role.old.previous.sources])
        for marker in [role.current.TERM, role.current.SEAL, role.current.LIVE,
                       'pg3478-outbox-parent-projection-v1']:
            self.assertTrue(marker in raw, marker)

    def test_standalone_stage_and_complete_operator_keep_new_roles(self):
        for raw in [dispatch.stage(), dispatch.run_source()]:
            ast.parse(raw)
            self.assertNotIn('PG2654', raw)
            self.assertNotIn('b2d6f605', raw)
        stage = dispatch.stage()
        for marker in [dispatch.REMOTE, role.TOOLS, 'PG3420']:
            self.assertTrue(marker in stage, marker)
        run = dispatch.run_source()
        for marker in ['pg3492', 'pg3494', 'Pg3490']:
            self.assertTrue(marker in run, marker)
        self.assertNotIn('management_gate', run)


if __name__ == '__main__':
    unittest.main()
