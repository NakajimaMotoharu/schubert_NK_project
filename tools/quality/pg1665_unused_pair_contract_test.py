"""Independent typed FD mutation vectors, no production-derived expected values."""
import copy
import unittest
from pg1665_unused_pair_contract import fresh_parent, parent_after_ref


def fixture():
    fds = {str(i): {'target': 'file:' + str(i), 'metadata': [28, i, 0, 0, 33152, 1, 0, 20, 20]} for i in range(101)}
    for i in ['29', '32']:
        fds[i] = {'target': '/run', 'metadata': [28, 3, 0, 0, 16877, 1, 40, 20, 20]}
    fds['17']['target'] = 'pipe:[17]'
    fds['18']['target'] = 'pipe:[18]'
    return {'pid': 291213, 'ticks': 5962776, 'argvSha256': 'fixed', 'authority': {'Uid': '0'}, 'cgroup': 'fixed', 'fds': fds}


class PairContractTest(unittest.TestCase):
    def test_fresh_all_fields_and_legal_chrono(self):
        a = fixture()
        b = copy.deepcopy(a)
        for i in ['29', '32']:
            b['fds'][i]['metadata'][7:] = [21, 22]
        self.assertTrue(fresh_parent(a, b, 22))
        for name in a['fds']:
            for index in range(9):
                v = copy.deepcopy(a)
                v['fds'][name]['metadata'][index] += 1
                with self.assertRaises(ValueError):
                    fresh_parent(a, v, 22)
        for invalid in [None, {}, True, 21.0]:
            with self.assertRaises(ValueError):
                fresh_parent(a, b, invalid)
        with self.assertRaises(ValueError):
            fresh_parent(a, b, 21)

    def test_missing_extra_identity_bool_future_and_regression(self):
        a = fixture()
        for kind in ['missing', 'extra', 'pid', 'ticks', 'argv', 'authority', 'bool', 'target', 'past', 'future']:
            b = copy.deepcopy(a)
            if kind == 'missing': del b['fds']['0']
            elif kind == 'extra': b['fds']['999'] = b['fds']['0']
            elif kind in ['pid', 'ticks']: b[kind] += 1
            elif kind == 'argv': b['argvSha256'] = 'foreign'
            elif kind == 'authority': b['authority']['Uid'] = '1'
            elif kind == 'bool': b['fds']['0']['metadata'][0] = True
            elif kind == 'target': b['fds']['29']['target'] = '/other'
            else:
                for i in ['29', '32']: b['fds'][i]['metadata'][7] = 19 if kind == 'past' else 99
            with self.assertRaises(ValueError): fresh_parent(a, b, 30)

    def test_only_known_pipe_disappearance(self):
        a = fixture()
        pipes = {'pipe:[17]', 'pipe:[18]'}
        for gone in [[], ['17'], ['18'], ['17', '18']]:
            b = copy.deepcopy(a)
            for i in gone: del b['fds'][i]
            self.assertTrue(parent_after_ref(a, b, pipes))
        for kind in ['otherGone', 'new', 'reuse', 'authority', 'pipeNull']:
            b = copy.deepcopy(a)
            if kind == 'otherGone': del b['fds']['34']
            elif kind == 'new': b['fds']['999'] = b['fds']['0']
            elif kind == 'reuse': b['fds']['17']['target'] = 'pipe:[foreign]'
            elif kind == 'authority': b['authority']['Uid'] = '1'
            with self.assertRaises(ValueError): parent_after_ref(a, b, None if kind == 'pipeNull' else pipes)


if __name__ == '__main__':
    unittest.main()
