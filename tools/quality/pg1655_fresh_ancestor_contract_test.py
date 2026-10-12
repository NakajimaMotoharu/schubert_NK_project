"""Independent field/race vectors, no Production-derived expected values."""
import copy
import unittest
import pg1655_fresh_ancestor_contract as p


class FreshActorContractTest(unittest.TestCase):
    def actor(self):
        fds = {str(i): {'target': '/file/' + str(i), 'metadata': [28, 100 + i, 0, 0, 33152, 1, 4, 10, 11]} for i in range(97)}
        for n in ['29', '32']:
            fds[n] = {'target': '/run', 'metadata': [28, 1, 0, 0, 16877, 2, 800, 10, 11]}
        return {'pid': 289328, 'ticks': 5627480, 'argvSha256': 'a' * 64, 'authority': {'Uid': '0'}, 'cgroup': 'fixed', 'fds': fds}

    def test_two_times_only_and_exact_fresh_rechecks(self):
        old = self.actor()
        fresh = copy.deepcopy(old)
        for n in ['29', '32']:
            fresh['fds'][n]['metadata'][7:] = [15, 16]
        self.assertTrue(p.validate_actor(old, fresh, 16))
        self.assertTrue(p.same_fresh(fresh, copy.deepcopy(fresh)))
        newer = copy.deepcopy(fresh)
        newer['fds']['29']['metadata'][7] += 1
        with self.assertRaises(ValueError):
            p.same_fresh(fresh, newer)
        self.assertEqual([10, 11], old['fds']['29']['metadata'][7:])

    def test_every_other_field_missing_extra_null_bool_foreign_rejected(self):
        old = self.actor()
        for n in old['fds']:
            for i in range(9):
                bad = copy.deepcopy(old)
                bad['fds'][n]['metadata'][i] += 1
                if n in ['29', '32'] and i in [7, 8]:
                    other = '32' if n == '29' else '29'
                    bad['fds'][other]['metadata'][i] += 1
                    continue
                with self.subTest(fd=n, field=i), self.assertRaises(ValueError):
                    p.validate_actor(old, bad, 99)
        for key in ['pid', 'ticks', 'argvSha256', 'authority', 'cgroup']:
            bad = copy.deepcopy(old)
            bad[key] = None
            with self.assertRaises(ValueError):
                p.validate_actor(old, bad, 99)
        for bad in [None, {}, {**old, 'extra': True}]:
            with self.assertRaises(ValueError):
                p.validate_actor(old, bad, 99)
        for n in ['29', '32']:
            for value in [None, True, -1, 100, 9]:
                bad = copy.deepcopy(old)
                bad['fds'][n]['metadata'][7] = value
                with self.assertRaises(ValueError):
                    p.validate_actor(old, bad, 99)
        bad = copy.deepcopy(old)
        del bad['fds']['0']
        with self.assertRaises(ValueError):
            p.validate_actor(old, bad, 99)


if __name__ == '__main__':
    unittest.main()
