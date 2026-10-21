"""Management-only quota marker guard: no quota redemption, billing or event append."""
import copy
import unittest
from pyflakes.api import checkPath
import pg998_metrics as subject


class Marker(unittest.TestCase):
    def test_forward_reverse_one_second_and_missing_marker_stay_unknown(self):
        for first,last,spent in ((1793082864,1793082865,1),(1793082865,1793082864,0),(None,1793082865,1),(None,None,0)):
            values=dict(quotaBefore=dict(primaryUsedPercent=38,resetsAt=first),
                quotaAfter=dict(primaryUsedPercent=39,resetsAt=last),sameQuotaWindow=True,observedSharedPp=spent,
                groupStartEstimatePp=dict(low=.5,base=2,high=6),actualAllocatedPp=None)
            original=copy.deepcopy(values);actual,_=subject.canonical_fields(values,'CHECKPOINT')
            self.assertEqual(original,values)
            self.assertEqual(original['quotaBefore'],actual['quotaBefore']);self.assertEqual(original['quotaAfter'],actual['quotaAfter'])
            self.assertIsNone(actual['sameQuotaWindow']);self.assertIsNone(actual['observedSharedPp'])
            self.assertEqual(dict(sameQuotaWindow=True,observedSharedPp=spent),actual['quotaWindowReportedBeforeGuard'])
            self.assertEqual(original['groupStartEstimatePp'],actual['estimateAtGroupStartPp'])
            self.assertIsNone(actual['actualAllocatedPp'])

    def test_exact_marker_preserves_reported_comparison_not_invented_delta(self):
        values=dict(quotaBefore=dict(resetsAt=1793082865,primaryUsedPercent=38),
            quotaAfter=dict(resetsAt=1793082865,primaryUsedPercent=39),sameQuotaWindow=True,observedSharedPp=1)
        actual,_=subject.canonical_fields(values,'CHECKPOINT')
        self.assertTrue(actual['sameQuotaWindow']);self.assertEqual(1,actual['observedSharedPp'])
        self.assertNotIn('quotaWindowReportedBeforeGuard',actual)

    def test_no_requested_comparison_never_infers_window_or_spend(self):
        actual,_=subject.canonical_fields(dict(quotaBefore=dict(resetsAt=1),quotaAfter=dict(resetsAt=1)),'CHECKPOINT')
        self.assertNotIn('sameQuotaWindow',actual);self.assertNotIn('observedSharedPp',actual)
        for path in (subject.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
