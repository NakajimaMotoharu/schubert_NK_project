import unittest
from pg1273_stop_hold_selected_counter import qualify


class ExactClassSessionTest(unittest.TestCase):
    def test_independent_class_and_owned_two_session_bounds(self):
        counters=''.join('<counter type="'+k+'" missed="0" covered="1"/>'for k in ['LINE','METHOD','CLASS','BRANCH'])
        raw=('<report><sessioninfo id="parent" start="1000" dump="1100"/><sessioninfo id="ownedchild" start="1010" dump="1090"/><package><class name="dev/codex/schubert/nk/bootstrap/FixedNativeCoverageStopHold">'+counters+'</class></package></report>').encode()
        self.assertEqual(qualify(raw,1000,1100)['sessionCount'],2)
        for bad in [raw.replace(b'missed="0"',b'missed="1"'),raw.replace(b'start="1010"',b'start="900"'),raw.replace(b'id="ownedchild"',b'id="parent"'),raw.replace(b'FixedNativeCoverageStopHold',b'Foreign')]:
            with self.assertRaises(ValueError):qualify(bad,1000,1100)


if __name__=='__main__':unittest.main()
