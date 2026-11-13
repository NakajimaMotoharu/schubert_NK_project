"""Require evidence before combining canonical preparation credit with earlier repricing."""
from decimal import Decimal, InvalidOperation
import re


def _amount(value):
    try:
        amount = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError('invalid planning price') from error
    if not amount.is_finite() or amount < 0:
        raise ValueError('finite nonnegative planning price required')
    return amount


def preparation_deduction(forecast, leaf, row_price):
    """Return only the not-yet-debited price; never infer overlap from a percentage."""
    work = leaf + '/1'
    if work in forecast.get('completedPlanWorkIds', []):
        raise ValueError('canonical preparation already completed; no replayed credit')
    price = {key: _amount(row_price[key]) for key in ('low', 'base', 'high')}
    prior = [item for item in forecast.get('estimateRevisions', [])
             if item.get('id') in (leaf, work) and item.get('baseDifferencePp', 0) < 0]
    legacy_preparation = work in forecast.get('completedPreparationWorkIds', [])
    if not prior and not legacy_preparation:
        return {key: float(value) for key, value in price.items()}
    bridge = forecast.get('canonicalPreparationBudgetBridges', {}).get(work)
    if not isinstance(bridge, dict) or bridge.get('status') != 'PROVEN_PREPARATION_PREDEBIT':
        raise ValueError('earlier negative repricing requires an explicit preparation price bridge')
    evidence = bridge.get('evidence', {})
    if (not isinstance(evidence, dict) or not isinstance(evidence.get('path'), str)
            or not evidence['path'].startswith('evidence/') or '..' in evidence['path'].split('/')
            or not re.fullmatch(r'[0-9a-f]{64}', str(evidence.get('sha256', '')))):
        raise ValueError('explicit public evidence path and hash required')
    recorded = bridge.get('canonicalRowPricePp', {})
    removed = bridge.get('alreadyDebitedPp', {})
    result = {}
    for key, amount in price.items():
        if key not in recorded or _amount(recorded[key]) != amount or key not in removed:
            raise ValueError('bridge must bind the exact frozen canonical row price')
        debit = _amount(removed[key])
        if debit > amount:
            raise ValueError('predebit exceeds original preparation row price')
        result[key] = float(amount - debit)
    return result
