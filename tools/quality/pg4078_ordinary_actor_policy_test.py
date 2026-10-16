import unittest
from pg4078_ordinary_actor_policy import identity


class ActorIdentityTest(unittest.TestCase):
    def fixture(self):
        return {'Uid': '999\t999\t999\t999', 'Gid': '981\t981\t981\t981',
                'Groups': '980 981 982 986', 'NoNewPrivs': '1',
                **{k: '0000000000000000' for k in ['CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb']}}

    def test_fixed_owner_all_four_ids_and_exact_required_groups(self):
        self.assertTrue(identity(self.fixture(), 999, 981, [980, 981, 982, 986]))

    def test_privilege_group_missing_extra_unknown_and_null_refused(self):
        for key, raw in [('Uid', '0 0 0 0'), ('Uid', '999 999 0 999'), ('Gid', '981 981 981'),
                         ('Groups', '981 982 986'), ('Groups', '980 981 982 986 987'),
                         ('Groups', '980 981 981 982 986'), ('Groups', '0980 981 982 986'),
                         ('CapBnd', '0000000000000001'), ('CapEff', None), ('NoNewPrivs', '0')]:
            v = self.fixture(); v[key] = raw
            with self.subTest(key=key), self.assertRaises(ValueError):
                identity(v, 999, 981, [980, 981, 982, 986])
        for args in [(None, 999, 981, [981]), (self.fixture(), None, 981, [981]),
                     (self.fixture(), 999, 981, None), (self.fixture(), 999, 981, [None, 981])]:
            with self.assertRaises(ValueError): identity(*args)


if __name__ == '__main__': unittest.main()
