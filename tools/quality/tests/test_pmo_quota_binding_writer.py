"""QUOTA-WRITER001..004: self-owned temporary public metadata and fake append, never real events."""
import json
from pathlib import Path
import tempfile
import unittest
import hashlib
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


class CanonicalEventWriterTest(unittest.TestCase):
    """BUG2356: real writer against a temporary ledger, never the shared live ledger."""
    def exercise(self, callback):
        live = pg998_metrics.EVENTS
        original = hashlib.sha256(live.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix='pgpt-owned-event-writer-') as directory:
            events = Path(directory) / 'events.jsonl'
            events.write_text(json.dumps(dict(eventId='PGPT-20261008-0001'))+'\n')
            with patch.object(pg998_metrics,'EVENTS',events),patch.object(pg998_metrics.subprocess,'check_output',return_value='a'*40):
                callback(events)
        self.assertEqual(live, pg998_metrics.EVENTS)
        self.assertEqual(original, hashlib.sha256(live.read_bytes()).hexdigest())

    def values(self):
        return dict(costRevision='WBS-cost-v2-20261007-PMO',workCategory='ADMIN',
                    wbsLeafIds=['WBS-K03.02'],estimateAtGroupStartPp=dict(low=.25,base=.75,high=2))

    def test_005_current_cost_revision_and_hash_are_explicit(self):
        values=self.values()
        revision,digest_value=pg998_metrics.estimate_identity(values)
        expected=hashlib.sha256((pg998_metrics.ROOT/'documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json').read_bytes()).hexdigest()
        self.assertEqual(values['costRevision'],revision)
        self.assertEqual(expected,digest_value)
        with self.assertRaises(ValueError):
            pg998_metrics.estimate_identity(dict(values,estimateRevisionSha256='0'*64))
        with self.assertRaises(ValueError):
            pg998_metrics.estimate_identity(dict(values,costRevision='UNKNOWN'))

    def test_006_legacy_end_becomes_registered_checkpoint_with_same_estimate(self):
        def check(events):
            values=self.values()
            self.assertEqual('PGPT-20261008-0002',pg998_metrics.append('OWNED','GROUP_END',values))
            record=json.loads(events.read_text().splitlines()[-1])
            self.assertEqual('CHECKPOINT',record['eventType'])
            self.assertEqual('GROUP_END',record['requestedLegacyEventType'])
            self.assertEqual('END',record['groupBoundary'])
            self.assertEqual('ADMIN',record['workCategory'])
            self.assertEqual(values['estimateAtGroupStartPp'],record['estimateAtGroupStartPp'])
            self.assertEqual('PGPT-20261008-0001',record['previousEventId'])
            self.assertIsNone(record['actualAllocatedPp'])
        self.exercise(check)

    def test_007_unregistered_category_type_parent_and_identity_never_write(self):
        def check(events):
            original=events.read_bytes()
            variants=[('CHECKPOINT',dict(self.values(),workCategory='DETAIL_NOT_REGISTERED')),
                      ('UNKNOWN',self.values()),
                      ('CHECKPOINT',dict(self.values(),wbsLeafIds=['WBS-P018-04'])),
                      ('CHECKPOINT',dict(self.values(),eventId='old')),
                      ('CHECKPOINT',dict(self.values(),timeJST=AT))]
            for event_type,values in variants:
                with self.assertRaises(ValueError):pg998_metrics.append('OWNED',event_type,values)
                self.assertEqual(original,events.read_bytes())
        self.exercise(check)

    def test_008_corrected_coarse_category_keeps_detail_separate(self):
        def check(events):
            values=dict(self.values(),workCategory='CONTRACT_AUDIT',workDetailCategory='ORIGINAL_PLAN_CONTRACT_ORACLE_TRACE_REUSE')
            pg998_metrics.append('OWNED','CHECKPOINT',values)
            record=json.loads(events.read_text().splitlines()[-1])
            self.assertEqual('CONTRACT_AUDIT',record['workCategory'])
            self.assertEqual(values['workDetailCategory'],record['workDetailCategory'])
            self.assertEqual(values['wbsLeafIds'],record['wbsLeafIds'])
        self.exercise(check)

    def test_009_current_cost_file_cannot_be_relabelled(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-owned-cost-revision-') as directory:
            root=Path(directory)
            file=root/'documents/400_PGPT/470_PMO/484_WBSコスト枠・細分化.json'
            file.parent.mkdir(parents=True)
            file.write_text(json.dumps(dict(revision='DIFFERENT')))
            with patch.object(pg998_metrics,'ROOT',root):
                with self.assertRaises(ValueError):
                    pg998_metrics.estimate_identity(self.values())

if __name__=='__main__':unittest.main()
