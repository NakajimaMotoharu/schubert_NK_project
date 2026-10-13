import unittest
from pg2402_morning_observation_selected import server, native_input, FILES


class Selected(unittest.TestCase):
    def test_full_real_pg_and_fixed_same_main_paths(self):
        raw = server()
        for value in ['source-full-PG2300', 'PG2402-selected-v1', 'SCHUBERT_PG_ROOT',
                      'Pg2402MorningObservationLauncher', "'tests':'2'", 'len(native_streams)==18',
                      'classByteMismatch', 'extra_library_hashes', 'fixture_xml_sha']:
            self.assertIn(value, raw)
        self.assertNotIn('source-full-PG2228', raw)
        self.assertNotIn("INPUT['native']['files']", raw)
        self.assertEqual(18, sum(len(p['files']) for p in native_input()['paths']))
        self.assertTrue(FILES[1].endswith('Pg2402MorningObservationLauncher.java'))


if __name__ == '__main__':
    unittest.main()
