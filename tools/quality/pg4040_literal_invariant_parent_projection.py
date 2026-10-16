"""Actual same-source parent18 after whole Root/Browser seal, before any owned stop."""
import inspect
import pg2706_operation_current_parent_projection as previous
import pg4022_literal_invariant_acceptance as root
import pg4038_literal_invariant_browser_composite as composite
from pg4012_literal_invariant_current_observer import SOURCE, BOM

SLOT = 'pg4040-literal-invariant-parent-projection-v1'


def payload(digest, bom=None):
    if bom is not None and bom != BOM: raise ValueError('exact current BOM required')
    return root.bind(previous.payload(digest, BOM)).replace(root.SEAL, composite.SLOT)


def main():
    raw = inspect.getsource(previous.main).replace('pg2704-operation-current-full-seal-v1', composite.SLOT)
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'payload': payload}
    exec(compile(raw, '<new actual composite parent18>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
