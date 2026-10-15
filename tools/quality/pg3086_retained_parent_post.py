"""Separate full current original and exact retained-parent-only prepare post."""
import inspect
import pg3066_browser_resume_post as previous
from pg3080_retained_parent_resume_sources import bind

SLOT = 'pg3086-retained-parent-independent-post-v1'


def payload(seals):
    return bind(previous.payload(seals)).replace(previous.SLOT, SLOT).replace('PG3066-browser-resume-independent-post-v1', 'PG3086-retained-parent-independent-post-v1')


def main():
    raw = inspect.getsource(previous.main).replace('pg3064-prepare-resume-v1.safe.json', 'pg3084-prepare-resume-v1.safe.json')
    ns = {**previous.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<normal retained-parent prepare and all-original post>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
