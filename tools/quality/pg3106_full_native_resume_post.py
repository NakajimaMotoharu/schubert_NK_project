"""Separate all24/native16/resources post of exact all11-key retained-parent preparation."""
import inspect
import pg3086_retained_parent_post as previous
from pg3100_full_native_resume_sources import bind

SLOT = 'pg3106-full-native-resume-independent-post-v1'


def payload(seals):
    return bind(previous.payload(seals)).replace(previous.SLOT, SLOT).replace('PG3086-retained-parent-independent-post-v1', 'PG3106-full-native-resume-independent-post-v1')


def main():
    raw = inspect.getsource(previous.main).replace('pg3084-prepare-resume-v1.safe.json', 'pg3104-prepare-resume-v1.safe.json')
    ns = {**previous.__dict__, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<actual full native finite independent post>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
