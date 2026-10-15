"""SSC276 single queued read-only proof for current failed3064 owner; no recovery signal."""
import inspect
import types
import pg2960_retained_resume_readonly as previous

SLOT = 'pg3070-retained-browser-readonly-v1'
BODY = previous.BODY.replace('pg2960-retained-resume-readonly-v1', SLOT).replace('Pg2950FreshResumePreparation', 'Pg3060FreshResumePreparation').replace('pg2954-current-cold-resume-preparation-v1', 'pg3064-browser-resume-preparation-v1')


def host_owner(path):
    raw = inspect.getsource(previous.host_owner)
    for old, new in [('77110', '114601'), ('1738713', '2519587'), ('f84e090d6bc59d98c4573aa768fc100b25812be80d6b164cc18812f463d7d971', 'b5645b75775303c81513c61dd2c4662941477d2f0aa7422569945e06ff06e2a3')]:
        raw = raw.replace(old, new)
    ns = dict(previous.__dict__)
    exec(compile(raw, '<actual retained host wrapper identity>', 'exec'), ns)
    return ns['host_owner'](path)


def main():
    fn = previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'BODY': BODY, 'host_owner': host_owner}, 'current_browser_retained_readonly')()


if __name__ == '__main__':
    raise SystemExit(main())
