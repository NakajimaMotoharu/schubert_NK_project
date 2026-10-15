"""Fresh Root-only binding; prior completed activations never become current authority."""
import inspect
import pg2990_current_resume_live_binding as previous

SLOT = 'pg3124-browser-resume-live-binding-v1'


def body():
    raw = previous.body()
    # The complete validator still supplies the old completed activation as a
    # rejection value, not a guessed new activation. New identity comes from PID1.
    old = '74729e17-91c0-43e7-b01f-74f9e6461d6a'
    if old not in raw:
        raise ValueError('previous completed activation rejection required')
    return raw.replace(old, '0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf')


def main():
    raw = inspect.getsource(previous.main).replace('pg2984-current-fresh-resume-once-v1', 'pg3144-current-parent-receipt-resume-once-v1')
    ns = {**previous.__dict__, 'SLOT': SLOT, 'body': body}
    exec(compile(raw, '<fresh actual browser-cohort Root binding>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
