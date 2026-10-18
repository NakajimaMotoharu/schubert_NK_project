import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pg5412_work_category_correction as entry


class CategoryGuard(unittest.TestCase):
    def test_invalid_future_category_never_opens_or_changes_events(self):
        with tempfile.TemporaryDirectory() as directory:
            events=Path(directory)/'events.jsonl';events.write_bytes(b'fixture immutable prefix\n')
            with patch.object(entry.metrics,'EVENTS',events):
                for invalid in ('SOURCE_REQUALIFICATION','full_regression',123,False):
                    with self.assertRaises(ValueError):entry.metrics.append('fixture','CHECKPOINT',{'workCategory':invalid})
            self.assertEqual(events.read_bytes(),b'fixture immutable prefix\n')

    def test_correction_retains_original_source_time_and_frozen_nonadditive_budget(self):
        row={'eventId':entry.TARGET,'groupId':'fixture','eventType':'GROUP_START','timeJST':'original-time',
            'source':'a'*40,'workCategory':'SOURCE_REQUALIFICATION','primaryWbs':'WBS-P018-04.03',
            'groupStartEstimatePp':{'low':1,'base':3,'high':8},'costRevision':'frozen','estimateRevisionSha256':'b'*64}
        raw=json.dumps(row).encode()+b'\n';result=entry.values(row,raw)
        self.assertEqual(result['source'],row['source']);self.assertEqual(result['originalTimeJST'],'original-time')
        self.assertEqual(result['groupStartEstimatePp'],row['groupStartEstimatePp'])
        self.assertEqual(result['workCategory'],'FULL_REGRESSION');self.assertEqual(result['newBudgetAddedPp'],0)
        self.assertEqual(result['newOutcomesAdded'],0);self.assertIsNone(result['actualAllocatedPp'])
        self.assertEqual(row['workCategory'],'SOURCE_REQUALIFICATION')
        for key,value in [('eventId','other'),('workCategory','unknown')]:
            invalid=dict(row);invalid[key]=value
            with self.assertRaises(ValueError):entry.values(invalid,raw)


if __name__=='__main__':unittest.main()
