import unittest
from pg2610_cleanup_readback_selected import METHOD, native_input, server


class CleanupReadback(unittest.TestCase):
    def test_actual_handoff_required(self):
        self.assertEqual('67f469dc24f5cee65995eb6afe718e76550f9136c791df18b9ed46c83df3ee9a',
                         native_input()['handoffServerManifestSha256'])

    def test_exact_one_literal_selection_and_input(self):
        raw = server()
        self.assertEqual(1, raw.count(METHOD))
        for marker in ['PG2610-selected-v1', 'PG2608-selected-v1', 'source-full-PG2600',
                       "str(xml),'PG2610','dev.codex.schubert.nk.batch.repository.MorningExpirySessionTest'",
                       'str(handoff_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
