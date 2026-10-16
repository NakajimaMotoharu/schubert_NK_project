"""Independent ABI auxiliary mapping and unchanged analyzer contracts."""
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg4424_shared_manager_static as tool


class CurrentAbi(unittest.TestCase):
    def fixture(self):
        old = {'/old/schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar': 'a' * 64 for m in tool.MODULES}
        old['/third-party/unchanged.jar'] = 'b' * 64
        qualified = {m: str(i) * 64 for i, m in enumerate(tool.MODULES)}
        return old, qualified

    def test_exact_six_and_all_third_party_preserved_without_mutating_old(self):
        old, qualified = self.fixture(); before = dict(old)
        actual = tool.current_auxiliary(old, qualified)
        expected = {'/home/mini/schubert-nk-pgpt/source-full-PG4420/src/schubert-nk-' + m + '/target/schubert-nk-' + m + '-0.1.0-SNAPSHOT.jar': qualified[m] for m in tool.MODULES}
        expected['/third-party/unchanged.jar'] = 'b' * 64
        self.assertEqual(expected, actual); self.assertEqual(before, old)

    def test_missing_duplicate_or_unknown_project_auxiliary_never_accepted(self):
        old, qualified = self.fixture()
        broken = [dict(old), dict(old), dict(old)]
        broken[0].pop('/old/schubert-nk-api-0.1.0-SNAPSHOT.jar')
        broken[1]['/duplicate/schubert-nk-api-0.1.0-SNAPSHOT.jar'] = 'a' * 64
        broken[2]['/old/schubert-nk-unknown-0.1.0-SNAPSHOT.jar'] = 'a' * 64
        for values in broken:
            with self.assertRaises(ValueError): tool.current_auxiliary(values, qualified)
        with self.assertRaises(ValueError): tool.current_auxiliary(old, {'api': 'a' * 64})

    def test_all_emitted_rules_hashes_and_full_849_contract_remain(self):
        raw = tool.server_source({})
        compile(raw, '<same-source static>', 'exec')
        self.assertEqual(0, check(raw, '<same-source static>', Reporter(io.StringIO(), io.StringIO())))
        # Binding assignment contributes two, verification/classpath/stability three,
        # final manifest contributes one. Every original use observes the new map.
        self.assertEqual(6, raw.count("old['auxJarSha256']"))
        for literal in ['original pinned PMD7.28.0', 'all category rules unchanged', 'same fixed Checkstyle/rules', 'source-full-PG4420', 'all849AppliedSourceExact', 'F03Accepted=False', 'sameCurrentSixJarAbi']:
            self.assertIn(literal, raw)


if __name__ == '__main__':
    unittest.main()
