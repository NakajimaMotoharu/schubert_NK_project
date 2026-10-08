"""Independent literal new exporter delta; not a production/native coverage assertion."""
import copy
import unittest
from pg621_candidate_contract import verify_delta


class CandidateDelta(unittest.TestCase):
    def fixture(self):
        old = {m: {'literal/Main.class': 'a'*64}
               for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')}
        old['bootstrap']['dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'] = 'b'*64
        new = copy.deepcopy(old)
        new['bootstrap']['dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'] = 'c'*64
        new['bootstrap'].update({
            'dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile$NativeIo.class': 'd'*64,
            'dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile$Io.class': 'e'*64})
        return old, new

    def test_literal_one_change_two_additions_only(self):
        old, new = self.fixture()
        self.assertEqual(7, sum(map(len, old.values())))
        self.assertEqual(9, verify_delta(old, new))

    def test_every_unknown_missing_removed_changed_or_malformed_delta_refuses(self):
        for mode in ('missing_module', 'extra_module', 'removed', 'foreign_added',
                     'missing_added', 'foreign_changed', 'unchanged_required', 'empty',
                     'digest_short', 'digest_upper', 'digest_null', 'bad_name'):
            old, new = self.fixture()
            if mode == 'missing_module':
                del new['web']
            elif mode == 'extra_module':
                new['foreign'] = {'x.class': 'a'*64}
            elif mode == 'removed':
                del new['api']['literal/Main.class']
            elif mode == 'foreign_added':
                new['bootstrap']['foreign.class'] = 'a'*64
            elif mode == 'missing_added':
                del new['bootstrap']['dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile$Io.class']
            elif mode == 'foreign_changed':
                new['web']['literal/Main.class'] = 'f'*64
            elif mode == 'unchanged_required':
                new['bootstrap']['dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'] = 'b'*64
            elif mode == 'empty':
                new['api'] = {}
            elif mode == 'digest_short':
                new['api']['literal/Main.class'] = 'a'*63
            elif mode == 'digest_upper':
                new['api']['literal/Main.class'] = 'A'*64
            elif mode == 'digest_null':
                new['api']['literal/Main.class'] = None
            else:
                new['api'] = {None: 'a'*64}
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                verify_delta(old, new)
        for old, new in ((None, {}), ({}, None), ([], {})):
            with self.assertRaises(ValueError):
                verify_delta(old, new)


if __name__ == '__main__':
    unittest.main()
