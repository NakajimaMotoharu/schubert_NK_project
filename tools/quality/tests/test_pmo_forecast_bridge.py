"""Independent literal price identities; tool tests, never application PT."""
import copy
import unittest

from pmo_forecast_bridge import reconcile_current_bridge


def fixture():
    return {
        "revision": "CURRENT-TEST",
        "remainingOriginalPlanPricePp": {"low": 100, "base": 200, "high": 300},
        "additionalDiscoveredRemainingPp": {"low": 3, "base": 4, "high": 5},
        "revisedRemainingPp": {"low": 101, "base": 201, "high": 301},
        "currentFullForecastBudgetBridge": {
            "remainingCanonicalOriginalPricePp": {"low": 100, "base": 200, "high": 300},
            "additionalRemainingPp": {"low": 90, "base": 90, "high": 90},
            "historicalPartialAdjustmentPp": {"low": -2, "base": -3, "high": -4},
            "currentRevisedRemainingPp": {"low": 999, "base": 999, "high": 999},
            "asOfRevision": "OLD-TEST",
            "history": {"retained": [17]},
        },
    }


class ForecastBridgeTest(unittest.TestCase):
    def test_stale_total_and_revision_are_replaced_without_mutating_history(self):
        value = fixture()
        before = copy.deepcopy(value)
        actual = reconcile_current_bridge(value)
        self.assertEqual({"low": 101, "base": 201, "high": 301}, actual["currentRevisedRemainingPp"])
        self.assertEqual({"low": 3, "base": 4, "high": 5}, actual["additionalRemainingPp"])
        self.assertEqual("CURRENT-TEST", actual["asOfRevision"])
        self.assertEqual({"retained": [17]}, actual["history"])
        self.assertEqual(before, value)
        actual["history"]["retained"].append(19)
        self.assertEqual([17], value["currentFullForecastBudgetBridge"]["history"]["retained"])

    def test_decimal_identity_is_exact_without_binary_float_rounding(self):
        value = fixture()
        value["remainingOriginalPlanPricePp"] = {"low": .1, "base": .2, "high": .3}
        value["currentFullForecastBudgetBridge"]["remainingCanonicalOriginalPricePp"] = {"low": .1, "base": .2, "high": .3}
        value["additionalDiscoveredRemainingPp"] = {"low": .2, "base": .3, "high": .4}
        value["currentFullForecastBudgetBridge"]["historicalPartialAdjustmentPp"] = {"low": -.1, "base": -.2, "high": -.3}
        value["revisedRemainingPp"] = {"low": .2, "base": .3, "high": .4}
        self.assertEqual({"low": .2, "base": .3, "high": .4}, reconcile_current_bridge(value)["currentRevisedRemainingPp"])

    def test_each_mismatched_total_is_rejected(self):
        for name in ("low", "base", "high"):
            with self.subTest(name=name):
                value = fixture()
                value["revisedRemainingPp"][name] += 1
                with self.assertRaisesRegex(ValueError, "identity failed"):
                    reconcile_current_bridge(value)

    def test_original_canonical_disagreement_is_rejected(self):
        value = fixture()
        value["currentFullForecastBudgetBridge"]["remainingCanonicalOriginalPricePp"]["base"] = 201
        with self.assertRaisesRegex(ValueError, "original prices disagree"):
            reconcile_current_bridge(value)

    def test_forecast_and_bridge_must_be_explicit_objects(self):
        for value in (None, [], "forecast"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "forecast object"):
                reconcile_current_bridge(value)
        for bridge in (None, [], "bridge"):
            value = fixture()
            value["currentFullForecastBudgetBridge"] = bridge
            with self.subTest(bridge=bridge), self.assertRaisesRegex(ValueError, "explicit forecast bridge"):
                reconcile_current_bridge(value)

    def test_missing_and_extra_price_dimensions_are_not_inferred(self):
        for prices in (None, [], {"low": 100}, {"low": 100, "base": 200, "high": 300, "extra": 1}):
            value = fixture()
            value["remainingOriginalPlanPricePp"] = prices
            with self.subTest(prices=prices), self.assertRaisesRegex(ValueError, "three-price"):
                reconcile_current_bridge(value)

    def test_bool_nonfinite_string_and_null_amounts_are_rejected(self):
        for amount in (True, False, float("nan"), float("inf"), -float("inf"), "4", None):
            value = fixture()
            value["additionalDiscoveredRemainingPp"]["base"] = amount
            with self.subTest(amount=amount), self.assertRaisesRegex(ValueError, "finite numeric"):
                reconcile_current_bridge(value)

    def test_revision_must_be_nonempty_text(self):
        for revision in (None, False, 17, "", " "):
            value = fixture()
            value["revision"] = revision
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, "current forecast revision"):
                reconcile_current_bridge(value)


if __name__ == "__main__":
    unittest.main()
