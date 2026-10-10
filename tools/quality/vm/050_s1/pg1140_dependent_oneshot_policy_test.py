import copy
import unittest
from pg1140_dependent_oneshot_policy import expiry, whole, REQUIRES, EXPIRY, BROKER, CLEANUP, TEN
import pg1133_fixed_broker_policy_test as broker_fixture


class DependencyTest(unittest.TestCase):
    def fixture(self):
        before = dict(Id=EXPIRY, InvocationID='e8bb5cda8e5044d8a541fbe2bbf0f725', Type='oneshot', RemainAfterExit='yes',
                      ActiveState='active', SubState='exited', MainPID='0', ControlPID='0', Job='', Result='success',
                      ExecMainCode='1', ExecMainStatus='0', ExecMainStartTimestampMonotonic='34900018429',
                      ExecMainExitTimestampMonotonic='35016395225', KillMode='control-group')
        after = dict(before, ActiveState='inactive', SubState='dead')
        dependencies = dict(Requires=' '.join(sorted(REQUIRES)), BindsTo='', PartOf='')
        return before, after, dependencies

    def test_only_two_states_change_exact_owner_history_and_requires(self):
        before, after, dependencies = self.fixture(); self.assertTrue(expiry(before, after, dependencies))
        for key in after:
            bad = dict(after); bad[key] = 'foreign'
            with self.subTest(key=key), self.assertRaises(ValueError): expiry(before, bad, dependencies)
        for field, value in [('Requires', 'artemis.service'), ('Requires', ' '.join(REQUIRES) + ' artemis.service'),
                             ('BindsTo', 'artemis.service'), ('PartOf', 'artemis.service')]:
            bad = dict(dependencies); bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): expiry(before, after, bad)
        for value in [None, {}, dict(dependencies, Extra='')]:
            with self.assertRaises(ValueError): expiry(before, after, value)

    def test_ten_unit_kernel_empty_is_not_equated_with_active_exited(self):
        e0, e1, dependencies = self.fixture(); b0, b1 = broker_fixture.BrokerTest().fixture()
        old = {name: dict(MainPID='0', ControlPID='0', Job='', ActiveState='inactive') for name in TEN - {BROKER, EXPIRY}}
        new = copy.deepcopy(old); old.update({EXPIRY:e0, BROKER:b0}); new.update({EXPIRY:e1, BROKER:b1})
        self.assertTrue(whole(old, new, dependencies))
        for name in new:
            bad = copy.deepcopy(new); bad[name]['ActiveState'] = 'active'
            with self.subTest(name=name), self.assertRaises(ValueError): whole(old, bad, dependencies)
        bad = copy.deepcopy(new); bad['caddy.service']['Extra'] = 'changed'
        with self.assertRaises(ValueError): whole(old, bad, dependencies)
        active = dict(MainPID='0', ControlPID='0', Job='', ActiveState='active', SubState='exited',
                      Type='oneshot', RemainAfterExit='yes', InvocationID='48281323ca3743cbbaddd706e0c4edc5',
                      ExecMainStartTimestampMonotonic='34688004646', ExecMainExitTimestampMonotonic='34751080043',
                      ExecMainCode='1', ExecMainStatus='0')
        old[CLEANUP] = active; new[CLEANUP] = copy.deepcopy(active)
        self.assertTrue(whole(old, new, dependencies, cleanup_active=True))
        with self.assertRaises(ValueError): whole(old, new, dependencies)
        for key in active:
            bad = copy.deepcopy(new); bad[CLEANUP][key] = 'foreign'
            with self.subTest(cleanupField=key), self.assertRaises(ValueError): whole(old, bad, dependencies, cleanup_active=True)
        for value in [None, 1]:
            with self.assertRaises(ValueError): whole(old, new, dependencies, cleanup_active=value)


if __name__ == '__main__': unittest.main()
