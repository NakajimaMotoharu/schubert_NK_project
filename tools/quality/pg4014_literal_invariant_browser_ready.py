"""Unchanged twelve independent Browser oracles, frozen before new ordinary Root."""
import inspect
import pg3800_hygiene_browser_ready as previous
from pg4002_literal_invariant_publication_sources import SOURCE

SLOT = 'pg4014-literal-invariant-browser-ready-v1'
PINNED = [name.replace('pg3800_hygiene_browser_ready.py', 'pg4014_literal_invariant_browser_ready.py') for name in previous.PINNED]


def require_ready():
    values = {**previous.previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'PINNED': PINNED}
    exec(compile(inspect.getsource(previous.previous.require_ready), '<current7bb Browser prerequisites>', 'exec'), values)
    return values['require_ready']()


def main():
    values = {**previous.previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'PINNED': PINNED}
    exec(compile(inspect.getsource(previous.previous.main), '<new source twelve-case independent browser preflight>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
