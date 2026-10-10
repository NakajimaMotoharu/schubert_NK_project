import copy
import unittest
from pg1188_current_native_targets import targets


class CurrentTargetsTest(unittest.TestCase):
    def fixture(self):
        return {'schubert-nk-api.service': '1'*32, 'schubert-nk-web.service': '2'*32,
                'schubert-nk-inbox-inspector.service': '3'*32}

    def test_complete_literal_nine_current_streams(self):
        actual = targets(self.fixture())
        expected = ('backup/backup.exec','cleanup/cleanup.exec','expiry/expiry.exec','parent/parent.exec',
                    'ordinary-api193/'+('1'*32)+'.terminal.exec','root-api193/'+('1'*32)+'.before-exec.exec',
                    'ordinary-web193/'+('2'*32)+'.terminal.exec','root-web193/'+('2'*32)+'.before-exec.exec',
                    'ordinary-inspector196/'+('3'*32)+'.terminal.exec')
        self.assertEqual(actual, expected)
        self.assertEqual(len(set(actual)), 9)

    def test_null_missing_unknown_and_legacy_scope_rejected(self):
        value = self.fixture()
        for bad in [None, {}, [], {k:v for k,v in value.items() if 'inspector' not in k}, dict(value, foreign='4'*32)]:
            with self.assertRaises(ValueError):targets(bad)

    def test_each_generation_type_format_zero_and_duplicate_rejected(self):
        value = self.fixture()
        for key in value:
            for bad in [None, True, 1, '', '0'*32, 'A'*32, '1'*31, '1'*33, '../file', '1'*32+'\n']:
                with self.subTest(key=key,bad=bad), self.assertRaises(ValueError):targets(dict(value, **{key:bad}))
        for other in ['schubert-nk-web.service','schubert-nk-inbox-inspector.service']:
            with self.assertRaises(ValueError):targets(dict(value, **{other:value['schubert-nk-api.service']}))

    def test_generations_bound_separately_and_input_unchanged(self):
        value = self.fixture();before = copy.deepcopy(value)
        first = targets(value);self.assertEqual(value, before)
        for key, count in [('schubert-nk-api.service',2),('schubert-nk-web.service',2),('schubert-nk-inbox-inspector.service',1)]:
            changed = targets(dict(value, **{key:'4'*32}))
            self.assertEqual(sum(a != b for a,b in zip(first,changed)), count)
            self.assertEqual(value, before)


if __name__ == '__main__':unittest.main()
