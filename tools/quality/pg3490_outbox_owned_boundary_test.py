import ast
import inspect
import unittest
import pg3490_outbox_owned_sources as role
import pg3494_outbox_owned_dispatch as dispatch


class ExactOwnedBoundaries(unittest.TestCase):
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
