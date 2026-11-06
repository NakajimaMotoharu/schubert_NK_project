"""Bind sanitized fresh API observations to new group starts; never estimate tokens or reset quota."""
import datetime as dt
import fcntl
import hashlib
import json
import math
from pathlib import Path

KEYS={'schema','observedAtUTC','ordinaryUsageAllowed','primary','secondary'}

def require(value,message):
    if not value:raise ValueError(message)

def utc(value):
    instant=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    require(instant.tzinfo is not None,'aware observation time required')
    return instant.astimezone(dt.timezone.utc)

def window(value):
    if value is None:return None
    used=value['usedPercent'];marker=value['resetsAt'];length=value['windowDurationMins']
    require(type(used) in (int,float) and math.isfinite(used) and 0<=used<=100,'valid observed percentage, never inferred')
    require(type(marker) is int and marker>0 and type(length) is int and length>0,'explicit positive reset marker/window')
    return dict(usedPercent=used,remainingPercent=100-used,resetsAt=marker,windowDurationMins=length)

def receipt(api,observed_at):
    allowed=api.get('ordinaryUsageAllowed');require(allowed is None or type(allowed) is bool,'explicit allowed state')
    buckets=api.get('rateLimitsByLimitId') or {}
    limits=buckets.get('codex') or api.get('rateLimits') or {}
    return dict(schema='PGPT_FRESH_QUOTA_V1',observedAtUTC=utc(observed_at).isoformat(),ordinaryUsageAllowed=allowed,
      primary=window(limits.get('primary')),secondary=window(limits.get('secondary')))

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def start_fields(group,values,observed,expected_digest,now,used_receipts=(),used_groups=()):
    require(set(observed)==KEYS and observed['schema']=='PGPT_FRESH_QUOTA_V1','exact sanitized receipt schema')
    require(digest(observed)==expected_digest,'receipt immutable byte identity')
    age=(utc(now)-utc(observed['observedAtUTC'])).total_seconds()
    require(0<=age<=120,'fresh receipt within120s, no future or stale replay')
    require(observed['ordinaryUsageAllowed'] is True and observed['primary'] is not None,'available primary and ordinary usage required')
    for key in ('primary','secondary'):
        item=observed[key]
        if item is None:continue
        require(window(item)==item,'remaining derived from actual used value, not a caller literal')
        require(item['resetsAt']>utc(now).timestamp() and item['remainingPercent']>10,'no expired marker or10percent reserve override')
    require(expected_digest not in used_receipts and group not in used_groups,'no duplicate receipt or group start')
    primary=observed['primary'];actual={k:primary[k] for k in ('usedPercent','remainingPercent','resetsAt')}
    require('quotaBefore' not in values or values['quotaBefore']==actual,'reject stale caller quota literal')
    result=dict(values);result.update(quotaBefore=actual,quotaReceipt=dict(sha256=expected_digest,observation=observed,
      vendorSignatureAvailable=False,origin='FRESH_GET_USAGE_LIMITS_TOOL_RESPONSE_SANITIZED_NOT_VENDOR_ATTESTATION'))
    return result

def append_start(group,values,receipt_path,expected_digest,now):
    # Only actual API-response capture calls this. This guard proves binding/freshness/replay safety,
    # not a vendor signature: callers must not manufacture or re-date an old API response.
    from pg998_metrics import EVENTS,append
    path=Path(receipt_path);require(path.is_file() and path.stat().st_size<16384,'bounded saved public receipt')
    observed=json.loads(path.read_bytes())
    with (EVENTS.parent/'quota-binding.lock').open('a+b') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        rows=[json.loads(line) for line in EVENTS.read_bytes().splitlines()]
        used=[r.get('quotaReceipt',{}).get('sha256') for r in rows if r.get('eventType')=='GROUP_START']
        groups=[r['groupId'] for r in rows if r.get('eventType')=='GROUP_START']
        bound=start_fields(group,values,observed,expected_digest,now,used,groups)
        bound['quotaReceipt']['path']=str(path)
        return append(group,'GROUP_START',bound)


def end_fields(before, observed, expected_digest, now, terminal_at, cap_pp):
    """BUG2322/YKT2067: bind a fresh post-terminal receipt; allow reserve-only preservation.

    No API requests, resets, event appends, quota attribution or token estimation occur here.
    A reset changes the measurement domain; its percentages cannot be subtracted.
    """
    require(set(observed)==KEYS and observed['schema']=='PGPT_FRESH_QUOTA_V1','exact sanitized receipt schema')
    require(digest(observed)==expected_digest,'receipt immutable byte identity')
    observed_at=utc(observed['observedAtUTC']);current=utc(now);terminal=utc(terminal_at)
    require(type(cap_pp) in (int,float) and math.isfinite(cap_pp) and 0<cap_pp<=10,'explicit group cap within10pp')
    require(0<=(current-observed_at).total_seconds()<=120,'fresh end receipt within120s')
    require(terminal<=observed_at,'end receipt must follow the actual terminal')
    require(observed['ordinaryUsageAllowed'] is None or type(observed['ordinaryUsageAllowed']) is bool,'explicit allowed state')
    for key in ('primary','secondary'):
        value=observed[key]
        if value is not None:require(window(value)==value,'derived observed window, never caller literals')
    primary=observed['primary'];previous=window(before.get('primary'))
    same=primary is not None and previous is not None and all(primary[k]==previous[k] for k in ('resetsAt','windowDurationMins'))
    delta=None
    if same:
        delta=primary['usedPercent']-previous['usedPercent']
        require(delta>=0,'same-window usage cannot decrease; no reset inference')
    quota_allows=observed['ordinaryUsageAllowed'] is True and primary is not None
    quota_allows=quota_allows and all(w['remainingPercent']>10 and w['resetsAt']>current.timestamp() for w in (observed['primary'],observed['secondary']) if w is not None)
    return dict(quotaAfter=observed,quotaReceipt=dict(sha256=expected_digest,observation=observed,
      vendorSignatureAvailable=False,origin='FRESH_GET_USAGE_LIMITS_TOOL_RESPONSE_SANITIZED_NOT_VENDOR_ATTESTATION'),
      observedSharedPp=delta,sameQuotaWindow=same,groupCapExceeded=delta is not None and delta>cap_pp,
      newImplementationAllowedByQuota=quota_allows,attribution='UNKNOWN',actualAllocatedPp=None,
      tokenTotals=None,terminalAtUTC=terminal.isoformat(),postTerminalReceiptVerified=True,
      missingOrChangedWindowIsNotZero=delta is None)
