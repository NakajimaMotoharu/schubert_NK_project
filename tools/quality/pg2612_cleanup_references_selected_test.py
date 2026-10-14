import unittest
from pg2612_cleanup_references_selected import METHOD, native_input, server


class CleanupReferences(unittest.TestCase):
    def test_actual_cleanup_required(self):
        self.assertEqual('6afcbcca413f0b31cb71d766bfb58aea3cb9e8dee53e28f4c3f457e58dd00196',
                         native_input()['cleanupServerManifestSha256'])

    def test_exact_one_literal_selection_and_input(self):
        raw = server()
        self.assertEqual(1, raw.count(METHOD))
        for marker in ['PG2612-selected-v1', 'PG2610-selected-v1', 'source-full-PG2600',
                       "str(xml),'PG2612','dev.codex.schubert.nk.batch.repository.MorningExpirySessionTest'",
                       'str(cleanup_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
