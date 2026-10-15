import ast
import inspect
import unittest
from pyflakes.api import check
import pg3490_outbox_owned_sources as old
import pg3520_outbox_owned_sources_v2 as role
import pg3524_outbox_owned_dispatch_v2 as dispatch
import pg3526_outbox_owned_post_v2 as post


class ActualEmittedRoles(unittest.TestCase):
    def test_old_failure_is_independently_reproduced_in_frozen_factory(self):
        raw = old.sources()['Pg3490NativeStop.java']
        self.assertIn('Pg387TrustedDeployment.STEM="pg2654"', raw)
        self.assertIn('epoch.boot().toString().equals("b2d6f605-61cf-425f-8fbd-12d606f6ee66")', raw)

    def test_all_final_outputs_and_current_tuple_independent_golden(self):
        values = role.sources()
        self.assertEqual(15, len(values))
        golden = ['79a3260a-e16d-42bf-942a-b914ed144c28', 'e1ee096d-370b-4ab9-915a-7c124207e854',
                  '225691a3-e748-42c4-8972-5ffda5de893d', '2026-10-15T16:49:02.160964Z',
                  '2026-10-15T17:16:54.836275Z']
        for name, raw in values.items():
            for old_role in ['b2d6f605', 'pg2654', 'PG2654', 'pg3490', 'Pg3490']:
                self.assertNotIn(old_role, raw, name)
            if name.endswith('.py'):
                ast.parse(raw)
                self.assertEqual(0, check(raw, name))
        stop = values['Pg3520NativeStop.java']
        fixture = values['Pg3520OriginalTupleTest.java']
        for expected in golden:
            self.assertIn(expected, stop)
            self.assertIn(expected, fixture)
        self.assertIn('Pg387TrustedDeployment.STEM="pg3420"', stop)
        self.assertIn('Pg387TrustedDeployment.LABEL="PG3420"', stop)
        self.assertIn('4856b3fcaeb4cae983d77757a38dc0bf56a693e2', stop)

    def test_standalone_and_delegated_main_have_one_gate(self):
        for raw in [dispatch.stage(), dispatch.run_source()]:
            ast.parse(raw)
            for old_role in ['b2d6f605', 'pg2654', 'pg3494', 'Pg3490']:
                self.assertNotIn(old_role, raw)
        self.assertIn('pg3524', dispatch.run_source())
        self.assertIn('Pg3520', dispatch.run_source())
        self.assertNotIn('management_gate', inspect.getsource(dispatch.main))
        delegated = dispatch.previous.old.previous.previous.prior.previous.prior.prior.prior.prior
        self.assertEqual('pg2092_current_newrun_owned_stop_dispatch', delegated.__name__)
        self.assertEqual(1, inspect.getsource(delegated.main).count('with management_gate('))
        self.assertIn('management_gate', post.entry().__code__.co_names)


if __name__ == '__main__':unittest.main()
