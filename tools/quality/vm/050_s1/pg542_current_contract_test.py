"""PG542 literal loaded/Id/idle negatives; management only, Production credit0."""
import copy
import unittest
from pg542_current_contract import current_units, post_retirement_schema


class CurrentUnitsTest(unittest.TestCase):
    def test_post_retirement_has_no_runtime_preparation_current_field(self):
        fields=('backup', 'bootstrapOldProofs', 'bootstrapTools', 'configuration', 'credentials',
                'dependencies', 'native', 'oldProofs', 'originals', 'parentPid1', 'pid1Stop',
                'rows', 'runtime', 'startup', 'units')
        value={name:{} for name in fields}
        self.assertTrue(post_retirement_schema(value))
        for invalid in (None, [], {}, {**value, 'current':'/foreign'}, {**value,'units':None}):
            with self.assertRaises(ValueError):
                post_retirement_schema(invalid)
        for name in fields:
            broken=dict(value);del broken[name]
            with self.assertRaises(ValueError):
                post_retirement_schema(broken)

    def fixture(self):
        names = ('caddy.service', 'schubert-nk-web.service', 'schubert-nk-api.service',
                 'schubert-nk-cleanup.service', 'schubert-nk-inbox-inspector.service',
                 'schubert-nk-expiry-cleanup.service', 'schubert-nk-backup.service',
                 'artemis.service', 'schubert-nk-morning-controller.service',
                 'schubert-nk-bootstrap-admin.service')
        return {n: {'Id': n, 'LoadState': 'loaded', 'MainPID': '0', 'ControlPID': '0',
                    'Job': '', 'ActiveState': 'failed' if n in names[1:3] else 'inactive'} for n in names}

    def test_exact_loaded_ten_and_preserved_failed_term_states(self):
        self.assertTrue(current_units(self.fixture()))

    def test_unknown_alias_null_missing_extra_and_stub_never_prove_stopped(self):
        for real, alias in (('schubert-nk-expiry-cleanup.service', 'schubert-nk-expiry.service'),
                            ('schubert-nk-bootstrap-admin.service', 'schubert-nk-bootstrap.service')):
            rows = self.fixture(); rows[alias] = rows.pop(real); rows[alias]['Id'] = alias
            with self.subTest(alias=alias), self.assertRaises(ValueError):
                current_units(rows)
        for wrong in (None, {}, [], {**self.fixture(), 'foreign.service': {}}):
            with self.assertRaises(ValueError):
                current_units(wrong)
        for name in self.fixture():
            for key, value in (('Id', 'foreign.service'), ('LoadState', 'not-found'),
                               ('LoadState', 'masked'), ('MainPID', '42'), ('MainPID', None),
                               ('ControlPID', '1'), ('Job', '42'), ('ActiveState', 'active')):
                rows = copy.deepcopy(self.fixture()); rows[name][key] = value
                with self.subTest(name=name, key=key), self.assertRaises(ValueError):
                    current_units(rows)
            rows=self.fixture();del rows[name]
            with self.assertRaises(ValueError):
                current_units(rows)


if __name__ == '__main__':
    unittest.main()
