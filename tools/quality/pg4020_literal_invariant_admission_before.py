"""Immutable ordinary pre-start image and same-day eligibility; no live DB mutation."""
import inspect
import pg3806_hygiene_admission_before as previous
from pg4012_literal_invariant_current_observer import SOURCE
from pg4016_literal_invariant_current_noargs_once import SLOT as ONCE
from pg4018_literal_invariant_current_live_binding import SLOT as LIVE

SLOT = 'pg4020-literal-invariant-admission-before-v1'
AFTER = '33b24b767326879adff27c1ee38aaa08102e347d04d631947047ef667f3352c6'


def namespace():
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'ONCE': ONCE, 'LIVE': LIVE, 'SLOT': SLOT, 'AFTER': AFTER}
    for fn in [previous.payload, previous.before, previous.main]:
        raw = inspect.getsource(fn).replace('pg3794-hygiene-publication-independent-post-v1', 'pg4008-literal-invariant-publication-independent-post-v1')
        raw = raw.replace("==34)", "==46)").replace("'execEntries':34", "'execEntries':46")
        exec(compile(raw, '<new immutable admission native46 image>', 'exec'), values)
    return values


def before(): return namespace()['before']()


def main(): return namespace()['main']()


if __name__ == '__main__': raise SystemExit(main())
