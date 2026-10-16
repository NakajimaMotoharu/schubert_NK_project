"""Reevaluate entire original Root oracle with actual Browser delta, never rewrite snapshots."""
import inspect
import pg3816_hygiene_browser_composite as previous
import pg4022_literal_invariant_acceptance as root
import pg4036_literal_invariant_browser_actual as actual
from pg4012_literal_invariant_current_observer import SOURCE, BOM

SLOT = 'pg4038-literal-invariant-browser-composite-v1'


def namespace():
    values = {**previous.previous.__dict__, 'SOURCE': SOURCE, 'BOM': BOM, 'root': root, 'actual': actual, 'SLOT': SLOT}
    for fn in [previous.previous.compose, previous.previous.payload]: exec(compile(inspect.getsource(fn), '<new immutable Root/Browser chain>', 'exec'), values)
    return values


def compose(raw, chain, digest): return namespace()['compose'](raw, chain, digest)


def payload(binding): return namespace()['payload'](binding)


def main():
    module = root.previous.old_seal; raw = inspect.getsource(module.entry)
    for old, new in [('pg2686-operation-current-live-binding-v1', root.LIVE), ('pg2682-parent-watch-v1', 'pg4012-parent-watch-v1'), ('pg2702-operation-current-rows-v1', root.ROWS), ('pg2700-operation-current-terminal-v1', root.TERM)]: raw = raw.replace(old, new)
    values = {**module.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'TERM': root.TERM, 'payload': payload}
    exec(compile(raw, '<new current Root plus real Browser independent seal>', 'exec'), values)
    return values['entry']()()


if __name__ == '__main__': raise SystemExit(main())
