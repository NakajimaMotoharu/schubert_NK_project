"""Same-run PID1/DONE independent oracle for Source2741 ordinary Root."""
import inspect
import json
import pg1601_current_newrun_done_receipt as prior
from pg1700_new_source_live_binding import SOURCE

EXPECTED = {'boot':'3d69f5af6bac46b1a5407591c4a79a0d',
            'invocation':'fe43e94b1fbf4886bb4ab3922fd16f9c','job':'106924',
            'start':66941284515,'run':'02e941b9-1c52-4018-a193-63dd00b269af',
            'cutoff':'2026-10-12T14:19:28.968927Z',
            'activation':'40da389f-23fc-4ad4-a71b-cf72a6bd5a62'}


def payload():
    raw = prior.payload()
    changes = [('e4d891c38dde4e16a5c848e23ef3f83c', EXPECTED['invocation']),
               ("'71184'", "'106924'"), ('38365395523', '66941284515'),
               ('0be226b1-bbb7-43d3-aa9e-59d0bda70f9a', EXPECTED['run']),
               ('2026-10-12T06:23:13.176261Z', EXPECTED['cutoff']),
               ('d28eead2-941c-4b97-9747-1758c0809e29', EXPECTED['activation']),
               ('2026, 10, 12, 6, 23, 10', '2026, 10, 12, 14, 19, 26'),
               ('pg1601-current-newrun-done-receipt-v1', 'pg1701-new-source-done-receipt-v1')]
    for old, new in changes:
        if old not in raw:
            raise ValueError('actual captured binding boundary missing')
        raw = raw.replace(old, new)
    compile(raw, '<new Source independent actual PID1 DONE>', 'exec')
    return raw


def main():
    transport = prior.prior.transport
    live = json.loads((transport.W/'pg1700-new-source-live-binding-v1.safe.json').read_bytes())
    if live.get('actualExit') != 0 or live.get('productionSource') != SOURCE or live.get('binding') != EXPECTED:
        raise ValueError('qualified actual live binding required')
    raw = inspect.getsource(transport.main)
    raw = raw.replace('pg1112-parent-watch-v1.private.jsonl', 'pg1698-parent-watch-v1.private.jsonl')
    raw = raw.replace('pg1117-current-done-receipt-v1', 'pg1701-new-source-done-receipt-v1')
    raw = raw.replace('PG1117-current-done-receipt-v1', 'PG1701-new-source-done-receipt-v1')
    raw = raw.replace('d5b00104280028d9ea81b44c1d1c805f3c2861ed', SOURCE)
    ns = {**transport.__dict__, 'payload': payload}
    exec(compile(raw, '<new Source readonly DONE transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__': raise SystemExit(main())
