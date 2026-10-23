"""QUOTA-GUARD001..010: owned metadata only, no live quota/network/job operations."""
import copy
import unittest
from pmo_quota_binding import digest,receipt,start_fields

AT='2026-10-23T14:00:00+00:00'
NOW='2026-10-23T14:00:01+00:00'

def api(used=24,secondary=None):
    return dict(ordinaryUsageAllowed=True,rateLimits=dict(primary=dict(usedPercent=used,resetsAt=1793306748,windowDurationMins=10080),secondary=secondary))

def bound(value,**kwargs):
    return start_fields('OWNED_TEST_GROUP',{},value,digest(value),NOW,**kwargs)

class QuotaBindingTest(unittest.TestCase):
    def test_001_actual24_is_bound_without_old23_literal(self):
        value=receipt(api(),AT);out=bound(value)
        self.assertEqual(dict(usedPercent=24,remainingPercent=76,resetsAt=1793306748),out['quotaBefore'])
        self.assertIsNone(out['quotaReceipt']['observation']['secondary'])

    def test_002_old_literal_is_rejected_not_overwritten_silently(self):
        value=receipt(api(),AT)
        with self.assertRaises(ValueError):start_fields('G',dict(quotaBefore=dict(usedPercent=23,remainingPercent=77,resetsAt=1793306748)),value,digest(value),NOW)

    def test_003_weekly10_or_less_blocks_new_group(self):
        for used in (90,91,100):
            with self.subTest(used=used),self.assertRaises(ValueError):bound(receipt(api(used),AT))
        self.assertEqual(89.9,bound(receipt(api(89.9),AT))['quotaBefore']['usedPercent'])

    def test_004_relevant_secondary10_blocks_even_with_weekly76(self):
        short=dict(usedPercent=90,resetsAt=1793306748,windowDurationMins=300)
        with self.assertRaises(ValueError):bound(receipt(api(secondary=short),AT))

    def test_005_unknown_or_disallowed_is_not_zero(self):
        for raw in ({},dict(ordinaryUsageAllowed=True),dict(ordinaryUsageAllowed=False,rateLimits=api()['rateLimits'])):
            with self.subTest(raw=raw),self.assertRaises(ValueError):bound(receipt(raw,AT))

    def test_006_stale_future_and_expired_marker_rejected(self):
        for observed in ('2026-10-23T13:57:00Z','2026-10-23T14:00:02Z'):
            with self.subTest(observed=observed),self.assertRaises(ValueError):bound(receipt(api(),observed))
        expired=api();expired['rateLimits']['primary']['resetsAt']=1
        with self.assertRaises(ValueError):bound(receipt(expired,AT))

    def test_007_invalid_numbers_and_markers_rejected(self):
        for used in (-1,101,True,float('nan'),float('inf')):
            with self.subTest(used=used),self.assertRaises(ValueError):receipt(api(used),AT)
        for key in ('resetsAt','windowDurationMins'):
            invalid=api();invalid['rateLimits']['primary'][key]=0
            with self.subTest(key=key),self.assertRaises(ValueError):receipt(invalid,AT)

    def test_008_duplicate_receipt_and_group_rejected(self):
        value=receipt(api(),AT)
        with self.assertRaises(ValueError):bound(value,used_receipts=[digest(value)])
        with self.assertRaises(ValueError):bound(value,used_groups=['OWNED_TEST_GROUP'])

    def test_009_mutated_value_and_remaining_rejected(self):
        value=receipt(api(),AT);changed=copy.deepcopy(value);changed['primary']['usedPercent']=23
        with self.assertRaises(ValueError):start_fields('G',{},changed,digest(value),NOW)
        with self.assertRaises(ValueError):bound(changed)

    def test_010_codex_bucket_preferred_and_unneeded_account_fields_dropped(self):
        raw=api(23);raw.update(accountId='DROP_THIS_FIXTURE',credits={'balance':'DROP_THIS_FIXTURE'})
        raw['rateLimitsByLimitId']={'codex':api(24)['rateLimits']}
        value=receipt(raw,AT)
        self.assertEqual(24,bound(value)['quotaBefore']['usedPercent'])
        self.assertNotIn('DROP_THIS_FIXTURE',str(value))
        with self.assertRaises(ValueError):receipt(api(),'2026-10-23T14:00:00')

if __name__=='__main__':unittest.main()
