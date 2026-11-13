"""Independent planning arithmetic examples; no product tests or acceptance credits."""
import unittest
from pgpt_preparation_price_bridge import preparation_deduction


class PreparationPriceBridgeTest(unittest.TestCase):
    def setUp(self):
        self.price = dict(low=1.5, base=4, high=8)
        self.forecast = dict(completedPlanWorkIds=[], estimateRevisions=[
            dict(id='WBS-F03', baseDifferencePp=-4)])

    def bridge(self, removed):
        self.forecast['canonicalPreparationBudgetBridges'] = {'WBS-F03/1': dict(
            status='PROVEN_PREPARATION_PREDEBIT', canonicalRowPricePp=self.price,
            alreadyDebitedPp=removed,
            evidence=dict(path='evidence/01_PT/example/manifest.json', sha256='a' * 64))}

    def test_fresh_original_preparation_debits_its_full_price(self):
        actual = preparation_deduction({}, 'WBS-P017-03.01', self.price)
        self.assertEqual(dict(low=1.5, base=4, high=8), actual)

    def test_old_four_point_repricing_cannot_silently_debit_four_again(self):
        with self.assertRaisesRegex(ValueError, 'explicit preparation price bridge'):
            preparation_deduction(self.forecast, 'WBS-F03', self.price)

    def test_proven_full_predebit_keeps_ninety_six_instead_of_ninety_two(self):
        self.bridge(dict(low=1.5, base=4, high=8))
        actual = preparation_deduction(self.forecast, 'WBS-F03', self.price)
        self.assertEqual(dict(low=0, base=0, high=0), actual)
        self.assertEqual(96, 100 - 4 - actual['base'])

    def test_partial_predebit_preserves_the_unfinished_price(self):
        self.bridge(dict(low=.5, base=1, high=2))
        self.assertEqual(dict(low=1, base=3, high=6),
                         preparation_deduction(self.forecast, 'WBS-F03', self.price))

    def test_increase_and_other_parent_repricing_do_not_claim_prepaid_work(self):
        self.forecast['estimateRevisions'] = [dict(id='WBS-F03', baseDifferencePp=2),
                                             dict(id='WBS-C02', baseDifferencePp=-3)]
        self.assertEqual(self.price, preparation_deduction(self.forecast, 'WBS-F03', self.price))

    def test_completed_canonical_row_cannot_replay_credit(self):
        self.forecast['completedPlanWorkIds'] = ['WBS-F03/1']
        with self.assertRaisesRegex(ValueError, 'already completed'):
            preparation_deduction(self.forecast, 'WBS-F03', self.price)

    def test_missing_evidence_or_wrong_original_price_is_rejected(self):
        for field, value in [('evidence', {}), ('canonicalRowPricePp', dict(low=1, base=3, high=7))]:
            with self.subTest(field=field):
                self.bridge(dict(low=1.5, base=4, high=8))
                self.forecast['canonicalPreparationBudgetBridges']['WBS-F03/1'][field] = value
                with self.assertRaises(ValueError):
                    preparation_deduction(self.forecast, 'WBS-F03', self.price)

    def test_negative_nonfinite_and_excess_predebits_are_rejected(self):
        for value in [-1, 'NaN', 'Infinity', 5]:
            with self.subTest(value=value):
                self.bridge(dict(low=1.5, base=value, high=8))
                with self.assertRaises(ValueError):
                    preparation_deduction(self.forecast, 'WBS-F03', self.price)

    def test_legacy_preparation_without_a_revision_still_requires_a_bridge(self):
        legacy = dict(completedPreparationWorkIds=['WBS-P005-01/1'])
        with self.assertRaisesRegex(ValueError, 'explicit preparation price bridge'):
            preparation_deduction(legacy, 'WBS-P005-01', dict(low=.087, base=.227, high=.455))

    def test_legacy_reference_with_proven_zero_predebit_retains_full_price(self):
        self.forecast['estimateRevisions'] = []
        self.forecast['completedPreparationWorkIds'] = ['WBS-F03/1']
        self.bridge(dict(low=0, base=0, high=0))
        self.assertEqual(self.price, preparation_deduction(self.forecast, 'WBS-F03', self.price))


if __name__ == '__main__':
    unittest.main()
