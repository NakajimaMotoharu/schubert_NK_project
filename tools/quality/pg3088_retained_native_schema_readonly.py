"""Single queued current3084 read-only identity proof; no previous owner reused."""
import inspect
import types
import pg2960_retained_resume_readonly as previous
import pg3070_retained_browser_readonly as template

SLOT = 'pg3088-retained-native-schema-readonly-v1'
BODY = template.BODY.replace('pg3070-retained-browser-readonly-v1', SLOT).replace('Pg3060FreshResumePreparation', 'Pg3080FreshResumePreparation').replace('pg3064-browser-resume-preparation-v1', 'pg3084-retained-parent-resume-preparation-v1')


def host_owner(path):
    raw = inspect.getsource(previous.host_owner)
    for old, new in [('77110', '119896'), ('1738713', '2601236'), ('f84e090d6bc59d98c4573aa768fc100b25812be80d6b164cc18812f463d7d971', '9d39566e9169273588f5bd141bc633ec2bb3f08991e0a5326f9c8e03d3e66fca')]:
        raw = raw.replace(old, new)
    ns = dict(previous.__dict__)
    exec(compile(raw, '<actual new119896 retained owner>', 'exec'), ns)
    return ns['host_owner'](path)


def main():
    fn = previous.main
    return types.FunctionType(fn.__code__, {**fn.__globals__, 'SLOT': SLOT, 'BODY': BODY, 'host_owner': host_owner}, 'new_native_schema_retained_readonly')()


if __name__ == '__main__':
    raise SystemExit(main())
