"""Independent SS341/V013 deletion plus SS314/324/351/352 current Log cohort.

Retains the prior immutable session population for addition classification. Removed
rows are selected from pre-Root expiry, never inferred from the resulting DB.
The observed journal cohort proves causality, not external request completeness.
"""
import copy
from pg1243_fresh_day_rows_oracle import deleted_sessions, instant
from pg583_log_oracle import verify


def verify_fresh(old, current, events, log_key, session_key, cutoff, count):
    if type(old) is not dict or type(current) is not dict or type(events) is not list or type(count) is not int or count <= 0:
        raise ValueError('fresh causal cohort contract refused')
    table = 'schubert_web_session.web_http_sessions'
    prior = old[table]
    now = current[table]
    expired = deleted_sessions(table, prior, instant(cutoff))
    ids = [r['id'] for r in prior]
    now_ids = [r['id'] for r in now]
    if len(set(ids)) != len(ids) or len(set(now_ids)) != len(now_ids):
        raise ValueError('duplicate session identity refused')
    gone = {r['id'] for r in expired}
    if any(r['id'] in gone for r in now):
        raise ValueError('independently expired session retained or recreated')
    retained = [r for r in prior if r['id'] not in gone]
    if any(r not in now for r in retained):
        raise ValueError('retained session mutation refused')
    # Existing verify's full prior-row invariant includes the explicitly removed
    # cohort via a local synthetic view, not a write or an altered expected DB.
    view = copy.copy(current)
    view[table] = now + expired
    result = verify(old, view, events, log_key, session_key, {('/login', 'GET', 200): count}, count)
    result.update(independentExpiredSessionCount=len(expired), priorRetainedSessionCount=len(retained),
                  externalFixtureRequestCountKnown=False, qa051FinalPass=False,
                  acceptanceScope='CAUSAL_WIRE_DB_LOCAL_SESSION_CRYPTO_ONLY')
    return result
