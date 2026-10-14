import unittest
from pg2614_expiry_readback_selected import METHOD, native_input, server


class ExpiryReadback(unittest.TestCase):
    def test_actual_reference_required(self):
        self.assertEqual('a93a42c4643ca43278bdf9ef328af8947d3432477d070f9723ab5dcd25ef7125',
                         native_input()['referenceServerManifestSha256'])

    def test_one_literal_selection(self):
        raw = server()
        self.assertEqual(1, raw.count(METHOD))
        for marker in ['PG2614-selected-v1', 'PG2612-selected-v1', 'source-full-PG2600',
                       "str(xml),'PG2614','dev.codex.schubert.nk.batch.repository.MorningExpirySessionTest'",
                       'str(reference_exec),str(execfile)']:
            self.assertIn(marker, raw)


if __name__ == '__main__':
    unittest.main()
