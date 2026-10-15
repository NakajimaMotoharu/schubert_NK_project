"""Read-only genuine terminal for only the newly reserved browser-cohort Root."""
import inspect
import pg2992_current_resume_terminal as previous

SLOT = 'pg3130-browser-resume-terminal-v1'


def payload(binding):
    if binding.get('activation') in {'74729e17-91c0-43e7-b01f-74f9e6461d6a', '0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf'}:
        raise ValueError('neither historical completed activation is fresh')
    return previous.payload(binding).replace(previous.SLOT, SLOT)


def main():
    raw = inspect.getsource(previous.main).replace('pg2990-current-resume-live-binding-v1', 'pg3124-browser-resume-live-binding-v1').replace('pg2982-parent-watch-v1', 'pg3120-parent-watch-v1')
    ns = {**previous.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<new browser Root genuine terminal dispatcher>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
