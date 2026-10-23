"""QUOTA-WRITER001..004: self-owned temporary public metadata and fake append, never real events."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pg998_metrics
from pmo_quota_binding import append_start,digest,receipt

AT='2026-10-23T14:00:00Z'
NOW='2026-10-23T14:00:01Z'

def observed(used=24):
    return receipt(dict(ordinaryUsageAllowed=True,rateLimits=dict(primary=dict(usedPercent=used,
      resetsAt=1793306748,windowDurationMins=10080),secondary=None)),AT)

class QuotaWriterTest(unittest.TestCase):
    def exercise(self,callback,prior=()):
        original=pg998_metrics.EVENTS
        with tempfile.TemporaryDirectory(prefix='pgpt-owned-quota-') as directory:
            root=Path(directory);events=root/'events.jsonl';events.write_text(''.join(json.dumps(r)+'\n' for r in prior))
            file=root/'receipt.json';value=observed();file.write_text(json.dumps(value));calls=[]
            def fake_append(group,kind,values):
                calls.append(dict(groupId=group,eventType=kind,**values));return 'OWNED_APPEND_ONLY'
            with patch.object(pg998_metrics,'EVENTS',events),patch.object(pg998_metrics,'append',fake_append):
                callback(file,value,calls)
        self.assertEqual(original,pg998_metrics.EVENTS)

    def test_001_saved_fresh24_reaches_writer_unchanged(self):
        def check(file,value,calls):
            self.assertEqual('OWNED_APPEND_ONLY',append_start('G',{},file,digest(value),NOW))
            self.assertEqual(1,len(calls));self.assertEqual('GROUP_START',calls[0]['eventType'])
            self.assertEqual(dict(usedPercent=24,remainingPercent=76,resetsAt=1793306748),calls[0]['quotaBefore'])
            self.assertEqual(str(file),calls[0]['quotaReceipt']['path'])
        self.exercise(check)

    def test_002_old_literal_and_tampered_receipt_never_append(self):
        def check(file,value,calls):
            with self.assertRaises(ValueError):append_start('G',dict(quotaBefore=dict(usedPercent=23,remainingPercent=77,resetsAt=1793306748)),file,digest(value),NOW)
            file.write_text(json.dumps(observed(23)))
            with self.assertRaises(ValueError):append_start('G',{},file,digest(value),NOW)
            self.assertEqual([],calls)
        self.exercise(check)

    def test_003_previous_group_or_receipt_is_rejected(self):
        value=observed()
        def check(file,value,calls):
            with self.assertRaises(ValueError):append_start('SAME',{},file,digest(value),NOW)
            with self.assertRaises(ValueError):append_start('OTHER',{},file,digest(value),NOW)
            self.assertEqual([],calls)
        self.exercise(check,[dict(eventType='GROUP_START',groupId='SAME',quotaReceipt=dict(sha256=digest(value)))])

    def test_004_low_unknown_stale_and_missing_inputs_never_append(self):
        def check(file,value,calls):
            for candidate in (observed(90),receipt({},AT)):
                file.write_text(json.dumps(candidate))
                with self.assertRaises(ValueError):append_start('G',{},file,digest(candidate),NOW)
            file.write_text(json.dumps(value))
            with self.assertRaises(ValueError):append_start('G',{},file,digest(value),'2026-10-23T14:03:00Z')
            with self.assertRaises(ValueError):append_start('G',{},file.parent/'absent',digest(value),NOW)
            self.assertEqual([],calls)
        self.exercise(check)

if __name__=='__main__':unittest.main()
