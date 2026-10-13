import unittest
from pg2500_current_boundary_native_qualification import server, source


class Bridge(unittest.TestCase):
    def test_all_members_latest_streams_and_no_guest_recapture(self):
        code = server()
        for marker in ['PG2500-native-v1', 'source-full-PG2494', 'source-full-PG2404',
                       'identical_main==1643', 'images[0]==images[1]', 'len(streams)==9',
                       'sameSessionProbeMonotonic', "'qualified2494Tests':3649", 'classByteMismatch']:
            self.assertIn(marker, code)
        transport = source()
        self.assertIn('pg2474-question-current-native-qualified-v1', transport)
        self.assertIn('pg2495-current-boundary-full-qualified-v1', transport)
        self.assertNotIn('SSH+', transport)
        self.assertNotIn("'/run/schubert-nk/pt-coverage/'", transport)


if __name__ == '__main__':
    unittest.main()
