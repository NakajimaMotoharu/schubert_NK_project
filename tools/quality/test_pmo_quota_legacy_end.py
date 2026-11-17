"""Synthetic pure-schema fixtures; no real account/API/event writes or reset actions."""
import copy
import hashlib
import json
import unittest
from pmo_quota_legacy_end import metric_end_fields
from pg998_metrics import canonical_fields


def observation(used=10, reset=2200000000, length=10080):
    return dict(schema='PGPT_FRESH_QUOTA_V1', observedAtUTC='2030-01-01T00:00:00+00:00',
                ordinaryUsageAllowed=True, secondary=None,
                primary=dict(usedPercent=used, remainingPercent=100-used,
                             windowDurationMins=length, resetsAt=reset))


def fixture(after=None, same=True, delta=0):
    before = observation()
    after = copy.deepcopy(before) if after is None else after
    independent_digest = hashlib.sha256(json.dumps(after, sort_keys=True,
                                      separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    result = dict(quotaAfter=after, quotaReceipt=dict(observation=copy.deepcopy(after),
                  sha256=independent_digest), postTerminalReceiptVerified=True,
                  sameQuotaWindow=same, observedSharedPp=delta,
                  actualAllocatedPp=None, tokenTotals=None, newImplementationAllowedByQuota=False)
    return before, result


class LegacyEndTest(unittest.TestCase):
    def test_same_window_observed_zero_survives_legacy_guard_without_cost_inference(self):
        before, values = fixture(); saved = copy.deepcopy(values)
        result = metric_end_fields(values, before); canonical, _ = canonical_fields(result, 'GROUP_END')
        self.assertEqual(0, canonical['observedSharedPp'])
        self.assertIs(True, canonical['sameQuotaWindow'])
        self.assertIsNone(canonical['actualAllocatedPp']); self.assertIsNone(canonical['tokenTotals'])
        self.assertIs(False, result['newImplementationAllowedByQuota'])
        self.assertEqual(saved, values)
        self.assertEqual(values['quotaReceipt'], result['quotaReceipt'])

    def test_nonzero_shared_difference_is_preserved(self):
        before, values = fixture(observation(12), delta=2)
        result, _ = canonical_fields(metric_end_fields(values, before), 'GROUP_END')
        self.assertEqual(2, result['observedSharedPp'])
        self.assertIsNone(result['actualAllocatedPp'])

    def test_changed_marker_and_window_stay_unknown(self):
        for after in [observation(12, reset=2200000001), observation(12, length=300)]:
            before, values = fixture(after, same=False, delta=None)
            result, _ = canonical_fields(metric_end_fields(values, before), 'GROUP_END')
            self.assertIsNone(result['observedSharedPp'])

    def test_missing_primary_stays_unknown(self):
        after = observation(); after['primary'] = None
        before, values = fixture(after, same=False, delta=None)
        result = metric_end_fields(values, before)
        self.assertIsNone(result['quotaAfter']); self.assertIsNone(result['observedSharedPp'])

    def test_wrong_receipt_shape_digest_comparison_and_bool_delta_fail_closed(self):
        for mode in ['digest', 'observation', 'flat', 'verified', 'window', 'bool']:
            before, values = fixture()
            if mode == 'digest': values['quotaReceipt']['sha256'] = '0'*64
            elif mode == 'observation': values['quotaReceipt']['observation']['primary']['usedPercent'] = 11
            elif mode == 'flat': values['quotaAfter'] = values['quotaAfter']['primary']
            elif mode == 'verified': values['postTerminalReceiptVerified'] = False
            elif mode == 'window': values['sameQuotaWindow'] = False
            else: values['observedSharedPp'] = False
            with self.subTest(mode=mode), self.assertRaises((ValueError, KeyError)):
                metric_end_fields(values, before)

    def test_decrease_or_wrong_before_never_creates_negative_or_fabricated_delta(self):
        before, values = fixture(observation(9), delta=-1)
        with self.assertRaisesRegex(ValueError, 'cannot decrease'):
            metric_end_fields(values, before)
        before, values = fixture(); values['quotaBefore'] = dict(before['primary'], usedPercent=0)
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            metric_end_fields(values, before)


if __name__ == '__main__':
    unittest.main()
