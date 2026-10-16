import copy
import stat
import unittest
import pg4378_half_handoff_contract as subject


class RemainingOwner(unittest.TestCase):
    def fixture(self):
        targets = ['pipe:[13981587]', 'pipe:[13981588]', 'pipe:[13981589]',
                   '/usr/lib/x86_64-linux-gnu/libffi.so.8.2.0', 'socket:[13984223]']
        return {'pid': 817783, 'ticks': 15666115,
                'argvSha256': 'a9deeaa12bc32f5bf4d7df54a844424f97f0f10811bbaf6546a578058c78988a',
                'authority': {'PPid': '817781', 'Uid': '0 0 0 0', 'Gid': '0 0 0 0', 'Groups': '0',
                              'NoNewPrivs': '0', 'CapInh': '0000000000000000', 'CapAmb': '0000000000000000',
                              'CapBnd': '000001ffffffffff', 'CapPrm': '000001ffffffffff', 'CapEff': '000001ffffffffff'},
                'children': [], 'cgroup': '0::/user.slice/user-1000.slice/session-986.scope\n',
                'fds': {str(n): {'target': target, 'metadata': [1, n + 1, 0, 0,
                         stat.S_IFIFO | 0o600 if n < 3 else stat.S_IFREG | 0o644 if n == 3 else stat.S_IFSOCK | 0o777,
                         1, 0, 20, 21], 'fdinfo': 'flags:\t01\n'} for n, target in enumerate(targets)}}

    def test_only_two_remaining_targets_never_java_or_root(self):
        for pair in [(815643, 15408795), (817783, 15666115)]: self.assertTrue(subject.target(*pair))
        for pair in [(815726, 15409721), (795724, 14962226), (808868, 15101177), (817783, 1), (True, 15666115), (None, None)]:
            with self.subTest(pair=pair), self.assertRaises(ValueError): subject.target(*pair)

    def test_exact_five_fd_metadata_owner(self):
        fixed = self.fixture(); self.assertTrue(subject.stable_retainer(fixed, copy.deepcopy(fixed)))
        for fd in fixed['fds']:
            for key, wrong in [('target', '/foreign'), ('metadata', None), ('fdinfo', 'foreign')]:
                after = copy.deepcopy(fixed); after['fds'][fd][key] = wrong
                with self.subTest(fd=fd, key=key), self.assertRaises(ValueError): subject.stable_retainer(fixed, after)
        for key in fixed['authority']:
            after = copy.deepcopy(fixed); after['authority'][key] = 'foreign'
            with self.subTest(key=key), self.assertRaises(ValueError): subject.stable_retainer(fixed, after)
        for key, wrong in [('pid', 1), ('ticks', 1), ('argvSha256', 'f' * 64), ('children', [1]), ('cgroup', 'foreign')]:
            after = copy.deepcopy(fixed); after[key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError): subject.stable_retainer(fixed, after)

    def test_invalid_trusted_baseline_shape_not_a_target(self):
        for fd in range(5):
            fixed = self.fixture(); fixed['fds'][str(fd)]['target'] = '/foreign'
            with self.assertRaises(ValueError): subject.stable_retainer(fixed, copy.deepcopy(fixed))
        with self.assertRaises(ValueError): subject.stable_retainer(None, self.fixture())


if __name__ == '__main__':
    unittest.main()
