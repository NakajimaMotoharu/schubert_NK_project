"""BUG3194/YKT2661: adapt an already verified end receipt to the legacy event fields.

Pure metadata only: no API, clock, reset, event append or cost allocation. Full
observations remain in quotaReceipt; only the primary window fields are flattened.
"""
import copy
from pmo_quota_binding import KEYS, digest, require, window


def metric_end_fields(values, before):
    require(type(values) is dict and type(before) is dict, 'explicit verified end and start receipt')
    after = values.get('quotaAfter')
    require(type(after) is dict and set(after) == KEYS and set(before) == KEYS,
            'full sanitized observations required before flattening')
    require(after['schema'] == before['schema'] == 'PGPT_FRESH_QUOTA_V1', 'observation schema')
    require(values.get('postTerminalReceiptVerified') is True, 'verified post-terminal binding required')
    receipt = values['quotaReceipt']
    require(receipt['observation'] == after and receipt['sha256'] == digest(after),
            'end observation/receipt digest mismatch')
    first, last = window(before['primary']), window(after['primary'])
    same = first is not None and last is not None and all(
        first[k] == last[k] for k in ('resetsAt', 'windowDurationMins'))
    delta = last['usedPercent'] - first['usedPercent'] if same else None
    require(delta is None or delta >= 0, 'same-window usage cannot decrease')
    require(values['sameQuotaWindow'] is same, 'verified window comparison mismatch')
    actual = values['observedSharedPp']
    require((actual is None and delta is None) or
            (type(actual) in (int, float) and actual == delta), 'verified shared delta mismatch')
    require('quotaBefore' not in values or values['quotaBefore'] == first,
            'caller quotaBefore disagrees with bound start observation')
    result = copy.deepcopy(values)
    result.update(quotaBefore=first, quotaAfter=last,
                  quotaAfterLegacyPrimaryOnly=True, fullObservationPreservedInReceipt=True)
    return result
