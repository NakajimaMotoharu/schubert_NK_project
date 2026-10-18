"""All24 raw-first SQL and independent newday/session/query cleanup postconditions."""
import inspect
import pg4756_new_current_same_day_rows as previous
import pg5036_current_admission_image as admission
import pg5038_current_genuine_terminal as terminal
import pg5030_new_day_query_oracle as oracle

SLOT = 'pg5040-current-newday-all24-v1'
key_source = previous.key_source


def payload(observed, before_hash):
    ns = {**vars(previous), 'admission': admission, 'terminal': terminal, 'SLOT': SLOT, 'key_source': key_source}
    exec(compile(inspect.getsource(previous.payload), '<actual captured24 raw-first transport>', 'exec'), ns)
    raw = ns['payload'](observed, before_hash)
    old = previous.oracle.source()
    if raw.count(old) != 1:
        raise ValueError('one independent query oracle boundary')
    raw = raw.replace(old, oracle.source(), 1)
    marker = 'result=qualify(before,now,BINDING'
    if raw.count(marker) != 1:
        raise ValueError('one newday qualification call')
    raw = raw.replace(marker, 'result=qualify_current(before,now,BINDING', 1)
    raw = raw.replace("inbox=classify_query_inbox(before,expected['inbox_scan_candidates'],KEY,LAYOUTS)",
                      'inbox=expected_inbox(before,expected)')
    return raw.replace("'retainedNotificationCandidates':", "'expectedNotificationDeleted':")


def main():
    ns = {**vars(previous), 'admission': admission, 'terminal': terminal, 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(previous.main), '<actual newday terminal before24>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
