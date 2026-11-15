"""BUG3024: reconcile current forecast references without changing prices or input history."""
import copy
from decimal import Decimal
from fractions import Fraction

DIMENSIONS = ("low", "base", "high")


def _prices(value):
    if not isinstance(value, dict) or set(value) != set(DIMENSIONS):
        raise ValueError("explicit three-price object required")
    result = {}
    for name in DIMENSIONS:
        amount = value[name]
        if type(amount) not in (int, float):
            raise ValueError("finite numeric price required; unknown is not zero")
        parsed = Decimal(str(amount))
        if not parsed.is_finite():
            raise ValueError("finite numeric price required; unknown is not zero")
        result[name] = Fraction(parsed)
    return result


def reconcile_current_bridge(forecast):
    """Check the exact decimal-price identity and return a new current bridge, never new costs."""
    if not isinstance(forecast, dict):
        raise ValueError("forecast object required")
    bridge = forecast.get("currentFullForecastBudgetBridge")
    if not isinstance(bridge, dict):
        raise ValueError("explicit forecast bridge required")
    revision = forecast.get("revision")
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError("explicit current forecast revision required")
    original = _prices(forecast.get("remainingOriginalPlanPricePp"))
    if original != _prices(bridge.get("remainingCanonicalOriginalPricePp")):
        raise ValueError("canonical original prices disagree")
    additional = _prices(forecast.get("additionalDiscoveredRemainingPp"))
    adjustment = _prices(bridge.get("historicalPartialAdjustmentPp"))
    expected = {name: original[name] + additional[name] + adjustment[name] for name in DIMENSIONS}
    if expected != _prices(forecast.get("revisedRemainingPp")):
        raise ValueError("current three-component forecast identity failed")
    result = copy.deepcopy(bridge)
    result["additionalRemainingPp"] = copy.deepcopy(forecast["additionalDiscoveredRemainingPp"])
    result["currentRevisedRemainingPp"] = copy.deepcopy(forecast["revisedRemainingPp"])
    result["asOfRevision"] = revision
    return result
