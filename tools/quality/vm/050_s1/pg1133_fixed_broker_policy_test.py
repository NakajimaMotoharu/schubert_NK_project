import copy
import unittest
from pg1133_fixed_broker_policy import stopped, configuration


class BrokerTest(unittest.TestCase):
    def fixture(self):
        before = dict(MainPID='253968', ControlPID='0', Job='', InvocationID='0f751fba26c94b22ac693a839fced07d',
                      ActiveState='active', SubState='running', Result='success', ExecMainCode='0', ExecMainStatus='0',
                      ExecMainStartTimestampMonotonic='34776223262', ExecMainExitTimestampMonotonic='0',
                      Type='simple', Restart='on-failure', User='artemis')
        after = dict(before, MainPID='0', ActiveState='inactive', SubState='dead', ExecMainCode='1',
                     ExecMainStatus='143', ExecMainExitTimestampMonotonic='40000000000')
        return before, after

    def test_exact_owned_transition_all_immutable_fields_bound(self):
        before, after = self.fixture(); self.assertTrue(stopped(before, after))
        for key in set(before) - {'ExecMainExitTimestampMonotonic'}:
            changed = copy.deepcopy(after); changed[key] = 'foreign'
            with self.subTest(key=key), self.assertRaises(ValueError): stopped(before, changed)
        for value in ['0', 'unknown', '1', None]:
            changed = dict(after, ExecMainExitTimestampMonotonic=value)
            with self.subTest(value=value), self.assertRaises(ValueError): stopped(before, changed)

    def test_primary_declared_argv_start_pid_and_all_other_config_preserved(self):
        before, after = self.fixture()
        records = {'old': ('/bin/java', 'literal argv', 'no', 'start', 'none', '253968', 'none', '0'),
                   'new': ('/bin/java', 'literal argv', 'no', 'start', 'end', '253968', 'exited', '143')}
        old = dict(ExecStart='old', Hardening='literal'); new = dict(ExecStart='new', Hardening='literal')
        self.assertTrue(configuration(old, new, before, after, records.get))
        for index in [0, 1, 2, 3, 5, 6, 7]:
            bad = list(records['new']); bad[index] = 'foreign'
            with self.subTest(index=index), self.assertRaises(ValueError):
                configuration(old, new, before, after, {'old': records['old'], 'new': tuple(bad)}.get)
        with self.assertRaises(ValueError): configuration(old, dict(new, Hardening='changed'), before, after, records.get)
        self.assertTrue(configuration(old, old, before, before, records.get))


if __name__ == '__main__': unittest.main()
