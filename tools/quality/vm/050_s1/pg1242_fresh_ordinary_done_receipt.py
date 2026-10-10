"""Actual PG1240 new-day parent receipt; unchanged independent PID1/DONE oracle."""
import inspect
import pg1117_current_done_probe as transport
from pg1194_completed_resume_receipt_v2 import payload as previous

REPLACEMENTS = [
    ('a14cc600a4fd4f2e9d8c4731ad9d754b', '2914e843f73d48dd93198dbdcae0f735'),
    ("'81093'", "'100948'"), ('51172132518', '61234139496'),
    ('343a5a1b-d064-47d5-88c2-31c36d7ba7a4', '9f651096-aef9-4fba-90b0-a653e99f035a'),
    ('2026-10-10T12:40:27.396847Z', '2026-10-10T20:03:22.718197Z'),
    ('ada3f7ff-8287-48d7-9ba9-5cce71f61bd3', '27accac0-c118-4c98-9244-02625a2d88a7'),
    ('2026, 10, 10, 12, 40, 25', '2026, 10, 10, 20, 3, 17'),
    ('pg1194-completed-resume-receipt-v2', 'pg1242-fresh-ordinary-done-receipt-v1'),
]

def payload():
    s = previous()
    for old, new in REPLACEMENTS:
        if old not in s:
            raise ValueError('fixed actual new-day parent binding required')
        s = s.replace(old, new)
    compile(s, '<actual new-day receipt>', 'exec')
    return s

def main():
    entry = inspect.getsource(transport.main)
    entry = entry.replace('pg1112-parent-watch-v1.private.jsonl', 'pg1237-parent-watch-v1.private.jsonl')
    entry = entry.replace('pg1117-current-done-receipt-v1', 'pg1242-fresh-ordinary-done-receipt-v1')
    entry = entry.replace('PG1117-current-done-receipt-v1', 'PG1242-fresh-ordinary-done-receipt-v1')
    env = dict(transport.__dict__)
    env['payload'] = payload
    exec(compile(entry, '<new-only actual parent receipt transport>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
