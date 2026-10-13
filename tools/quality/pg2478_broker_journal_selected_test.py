import unittest
from pathlib import Path
from pg2478_broker_journal_selected import FILES, SOURCE, native_input, server


class Selected(unittest.TestCase):
    def test_current_main_latest_nine_and_independent_isolated_methods(self):
        raw = server()
        for marker in ['source-full-PG2404', 'PG2478-selected-v3', 'PG2474-native-v1',
                       'len(native_streams)==9', "'tests':'4'", 'classByteMismatch',
                       'MainRecompiled', 'fixturesUnchanged', 'extra_library_hashes', 'fixture_xml_sha', 'com/google/code/gson/gson/']:
            self.assertIn(marker, raw)
        self.assertNotIn('source-full-PG2124', raw)
        self.assertEqual(9, len(native_input()['files']))
        self.assertEqual('cdbc07cdf77370d521e64de8b327da7f6752139b', SOURCE)
        launcher = Path(FILES[1]).read_text()
        for n in range(1, 5):
            self.assertEqual(1, launcher.count('bj247800' + str(n)))
        self.assertIn('parallel.enabled", "false"', launcher)
        self.assertIn('tests=\\"4\\"', launcher)


if __name__ == '__main__':
    unittest.main()
