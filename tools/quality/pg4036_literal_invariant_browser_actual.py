"""Same four actual owners/twelve independent Browser cases; no start, stop or trust inflation."""
import inspect
import json
import types
import pg3580_current_browser_actual as previous
import pg4022_literal_invariant_acceptance as accepted
import pg4029_literal_invariant_browser_ready_serial as ready
from pg4018_literal_invariant_current_live_binding import SLOT as LIVE
from pg4012_literal_invariant_current_observer import SOURCE, BOM
from pg1446_current_cold_stage import W

SLOT = 'pg4036-literal-invariant-browser-actual-v1'


def live():
    result = json.loads((W / LIVE / 'manifest.safe.json').read_bytes())
    if result.get('actualExit') != 0 or result.get('productionSource') != SOURCE: raise ValueError('actual new Root generation required')
    return result


def guard(seal, terminal, binding):
    raw = previous.bind(previous.template.GUARD)
    for old, new in [('4856b3fcaeb4cae983d77757a38dc0bf56a693e2', SOURCE), ('dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72', BOM), ('PG3420', 'PG3976')]:
        if raw.count(old) != 1: raise ValueError('exact positive new current Browser guard role')
        raw = raw.replace(old, new)
    return types.FunctionType(previous.template.guard.__code__, {**previous.template.__dict__, 'SOURCE': SOURCE, 'GUARD': raw})(seal, terminal, binding)


def main():
    shared = ready.previous.previous.previous
    values = {**previous.__dict__, 'SOURCE': SOURCE, 'SLOT': SLOT, 'guard': guard, 'require_ready': ready.require_ready, 'READY': ready.SLOT,
              'JAVA': shared.JAVA, 'classpath': shared.classpath, 'root': types.SimpleNamespace(SEAL=accepted.SEAL, TERM=accepted.TERM, live=live)}
    exec(compile(inspect.getsource(previous.main), '<new current same-four-owner Browser transport>', 'exec'), values)
    return values['main']()


if __name__ == '__main__': raise SystemExit(main())
