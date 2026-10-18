"""Actual newday applicability from sealed BEFORE only; no business/clock changes."""
import types
from pyflakes.api import check
import pg5020_current_query_oracle_preflight as previous
import pg5030_new_day_query_oracle as oracle
from pg4996_resume_connection import authenticate_host

SLOT = 'pg5032-new-day-query-preflight-v1'


def once(raw, before, after):
    if raw.count(before) != 1:
        raise ValueError('one exact independent new-day applicability boundary')
    return raw.replace(before, after, 1)


def payload():
    raw = previous.payload()
    marker = 'import base64,hashlib,os,stat\n'
    if raw.count(marker) != 1:
        raise ValueError('one original current-before/key read boundary')
    raw = oracle.source() + '\n' + raw[raw.index(marker):]
    raw = once(raw, "inbox=classify_query_inbox(before,expected['inbox_scan_candidates'],KEY,LAYOUTS)",
               'inbox=expected_inbox(before,expected)')
    raw = once(raw, "require(all(history.values())and {'CLEAN_SESSION','CLEAN_LOG','CLEAN_NOTIFICATION'}<=skips and 'CLEAN_INBOX_OUTBOX'not in skips)",
               "require(not any(history.values()) and not skips)")
    raw = once(raw, "require(all(max(r['attempt']for r in rows)<99 for rows in history.values()))",
               "require(all(not rows for rows in history.values()))")
    if check(raw, '<newday actual immutable before and authenticated query applicability>'):
        raise ValueError('complete emitted namespace static0')
    compile(raw, '<fresh newday applicability; no DB/clock mutation>', 'exec')
    return raw


def main():
    authenticate_host()
    transport = previous.previous.previous.transport
    execute = types.FunctionType(transport.execute.__code__, {**vars(transport), 'SOURCE': previous.current.SOURCE})
    return execute(SLOT, payload(), 45)


if __name__ == '__main__':
    raise SystemExit(main())
