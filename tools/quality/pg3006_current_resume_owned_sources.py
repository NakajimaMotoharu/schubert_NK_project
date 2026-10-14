"""Current fresh resume ownership graph; actual terminal/seal/parent18 required."""
import inspect
import pg2890_network_owned_sources as previous
import pg2992_current_resume_terminal as terminal
from pg2982_current_resume_observer import SOURCE, BOM

TOOLS = 'pg3006-current-resume-owned-stop-tools-v1'


def bind(raw):
    raw = previous.bind(raw)
    for a, b in [(previous.TOOLS, TOOLS), ('pg2902-network-after-chr-full-seal-v1', 'pg3000-current-resume-full-seal-v1'), ('pg2878-network-newcurrent-terminal-v1', terminal.SLOT), ('pg2874-network-newcurrent-live-binding-v1', 'pg2990-current-resume-live-binding-v1'), ('pg2904-network-after-chr-parent-projection-v1', 'pg3004-current-resume-parent-projection-v1'), ('pg2894-network-owned-stage-v1', 'pg3010-current-resume-owned-stage-v1'), ('pg2898-network-owned-post-v1', 'pg3012-current-resume-owned-post-v1'), ('PG2898-network-owned-post-v1', 'PG3012-current-resume-owned-post-v1'), ('pg2890', 'pg3006'), ('Pg2890', 'Pg3006'), ('PG2890', 'PG3006'), ('pg2892', 'pg3008'), ('pg2894', 'pg3010'), ('pg2895', 'pg3011'), ('pg2896', 'pg3013')]:
        raw = raw.replace(a, b)
    return raw


def namespace():
    base = previous.prior.previous
    ns = {**base.__dict__, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'terminal_payload': terminal.payload, 'candidate_bom': lambda: BOM}
    for fn in [base.context, base.emit_receipt, base.emit, base.sources]:
        exec(compile(bind(inspect.getsource(fn)), '<actual current fresh owned graph>', 'exec'), ns)
    return ns


def context():
    return namespace()['context']()


def sources():
    return {bind(n): bind(raw) for n, raw in namespace()['sources']().items()}


def emit(ctx, live, state, fields):
    return {bind(n): bind(raw) for n, raw in namespace()['emit'](ctx, live, state, fields, BOM).items()}
