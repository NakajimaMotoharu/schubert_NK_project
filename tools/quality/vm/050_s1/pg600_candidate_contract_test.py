"""Literal candidate delta normal/foreign/missing/malformed vectors; PT credit zero."""
import copy
import unittest
from pg600_candidate_contract import verify_delta


class CandidateDelta(unittest.TestCase):
    def fixture(self):
        old = {m: {'literal/Main.class': 'a' * 64}
               for m in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')}
        old['bootstrap'].update({
            'dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint.class': 'b' * 64,
            'dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent.class': 'b' * 64,
            'dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class': 'b' * 64})
        new = copy.deepcopy(old)
        for name in tuple(new['bootstrap']):
            if name != 'literal/Main.class': new['bootstrap'][name] = 'c' * 64
        new['bootstrap'].update({
            'dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent$Classes.class': 'd' * 64,
            'dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent$Sources.class': 'd' * 64,
            'dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent$Invocation.class': 'd' * 64})
        return old, new

    def test_exact_closed_three_changes_three_additions(self):
        old, new = self.fixture()
        self.assertEqual(12, verify_delta(old, new))
        self.assertEqual(9, sum(map(len, old.values())))

    def test_module_and_class_delta_refusal(self):
        for mode in ('missing_module', 'extra_module', 'removed', 'foreign_added',
                     'missing_added', 'foreign_changed', 'unchanged_required', 'empty',
                     'digest_short', 'digest_upper', 'digest_null', 'bad_name'):
            with self.subTest(mode=mode):
                old, new = self.fixture()
                if mode == 'missing_module': del new['web']
                elif mode == 'extra_module': new['foreign'] = {'x.class': 'a' * 64}
                elif mode == 'removed': del new['api']['literal/Main.class']
                elif mode == 'foreign_added': new['bootstrap']['foreign.class'] = 'a' * 64
                elif mode == 'missing_added':
                    del new['bootstrap']['dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent$Classes.class']
                elif mode == 'foreign_changed': new['web']['literal/Main.class'] = 'e' * 64
                elif mode == 'unchanged_required':
                    new['bootstrap']['dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.class'] = 'b' * 64
                elif mode == 'empty': new['api'] = {}
                elif mode == 'digest_short': new['api']['literal/Main.class'] = 'a' * 63
                elif mode == 'digest_upper': new['api']['literal/Main.class'] = 'A' * 64
                elif mode == 'digest_null': new['api']['literal/Main.class'] = None
                else: new['api'] = {None: 'a' * 64}
                with self.assertRaises(ValueError): verify_delta(old, new)
        for old, new in ((None, {}), ({}, None), ([], {})):
            with self.assertRaises(ValueError): verify_delta(old, new)


if __name__ == '__main__': unittest.main()
