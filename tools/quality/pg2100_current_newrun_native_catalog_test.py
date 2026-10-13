"""Actual ten-point full catalog and immutable old-negative new-positive identity boundary."""
import unittest
from pg2100_current_newrun_native_catalog import catalog_source,entry,SLOT
from pg2090_current_newrun_owned_stop_sources import receipt_source


class Native(unittest.TestCase):
    def test_actual_receipt_and_current_points(self):
        receipt=receipt_source();raw=catalog_source(receipt)
        self.assertTrue(raw.startswith(receipt+'\n'))
        for marker in ['len(old)==32','pg2090-native-stop-v1','2aae1ec09dc34e6281742e0127ceee25','205206','205353','113070840714','114755353173']:
            self.assertTrue(marker in raw,marker)
        self.assertEqual(SLOT,entry().__globals__['SLOT'])


if __name__=='__main__':unittest.main()
