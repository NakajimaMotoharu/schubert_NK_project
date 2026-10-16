"""Actual new-source terminal/all24/whole seal, immutable independent same-day oracle."""
import inspect
import sys
import pg3808_hygiene_acceptance as previous
from pg4012_literal_invariant_current_observer import SOURCE, BOM
from pg4016_literal_invariant_current_noargs_once import SLOT as ONCE
from pg4018_literal_invariant_current_live_binding import SLOT as LIVE
from pg4020_literal_invariant_admission_before import before
from pg4002_literal_invariant_publication_sources import BOOT

TERM = 'pg4022-literal-invariant-current-terminal-v1'
ROWS = 'pg4024-literal-invariant-current-rows-v1'
SEAL = 'pg4026-literal-invariant-current-full-seal-v1'


def namespace():
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'BOM': BOM, 'BOOT': BOOT, 'ONCE': ONCE, 'LIVE': LIVE, 'TERM': TERM, 'ROWS': ROWS, 'SEAL': SEAL, 'before': before}
    for fn in [previous.bind, previous.terminal_payload, previous.rows_payload, previous.seal_payload, previous.entry]:
        raw = inspect.getsource(fn).replace('PG3748', 'PG3976').replace('pg3748-manifest.sig', 'pg3976-manifest.sig').replace('pg3798-parent-watch-v1', 'pg4012-parent-watch-v1')
        exec(compile(raw, '<new source same-day actual acceptance factory>', 'exec'), values)
    return values


def terminal_payload(binding): return namespace()['terminal_payload'](binding)


def rows_payload(): return namespace()['rows_payload']()


def seal_payload(binding): return namespace()['seal_payload'](binding)


def entry(phase): return namespace()['entry'](phase)


if __name__ == '__main__': raise SystemExit(entry(sys.argv[1])())
