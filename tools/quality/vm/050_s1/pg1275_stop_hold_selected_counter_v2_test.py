import unittest
from pg1275_stop_hold_selected_counter_v2 import qualify


class LateDumpSessionTest(unittest.TestCase):
    def test_independent_three_jvm_and_retained_late_dump_records(self):
        counters=''.join('<counter type="'+k+'" missed="0" covered="1"/>'for k in ['LINE','METHOD','CLASS','BRANCH'])
        start='<report><sessioninfo id="parent" start="1000" dump="1100"/><sessioninfo id="ordering-child" start="1010" dump="1090"/><sessioninfo id="refusal-child" start="1020" dump="1040"/>'
        tail='<package><class name="dev/codex/schubert/nk/bootstrap/FixedNativeCoverageStopHold">'+counters+'</class></package></report>'
        self.assertEqual(qualify((start+tail).encode(),1000,1100)['sessionCount'],3)
        extra='<sessioninfo id="refusal-child" start="1020" dump="1080"/>'
        self.assertEqual(qualify((start+extra+tail).encode(),1000,1100)['rawSessionRecords'],4)
        for bad in [(start+extra+tail).replace('start="1020" dump="1080"','start="1030" dump="1080"'),(start+tail).replace('id="refusal-child"','id="parent"'),(start+tail).replace('missed="0"','missed="1"'),start+extra+extra+tail]:
            with self.assertRaises(ValueError):qualify(bad.encode(),1000,1100)


if __name__=='__main__':unittest.main()
