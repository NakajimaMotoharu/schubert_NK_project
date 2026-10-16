"""BUG1331 new-only full readiness after observer stage terminal; never weaken shared gate."""
import inspect
import pg4014_literal_invariant_browser_ready as previous

SOURCE = previous.SOURCE
SLOT = 'pg4029-literal-invariant-browser-ready-serial-v1'
PINNED = [name.replace('pg4014_literal_invariant_browser_ready.py', 'pg4029_literal_invariant_browser_ready_serial.py') for name in previous.PINNED]


def require_ready():
    values = {**previous.previous.previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'PINNED': PINNED}
    exec(compile(inspect.getsource(previous.previous.previous.require_ready), '<actual new serial Browser prerequisite>', 'exec'), values)
    return values['require_ready']()


def main():
    values = {**previous.previous.previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'PINNED': PINNED}
    exec(compile(inspect.getsource(previous.previous.previous.main), '<new-only Browser readiness no parallel manager>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
