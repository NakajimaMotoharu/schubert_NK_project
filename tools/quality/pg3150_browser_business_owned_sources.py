"""One current ownership graph from the composite Root/Browser seal, no Root replay."""
import inspect
import pg3006_current_resume_owned_sources as previous
import pg3130_browser_resume_terminal as terminal
from pg3120_prepared_browser_observer import SOURCE, BOM

TOOLS = 'pg3150-browser-business-owned-stop-tools-v1'


def bind(raw):
    raw = previous.bind(raw)
    for old, new in [
        (previous.TOOLS, TOOLS), ('pg3000-current-resume-full-seal-v1', 'pg3146-browser-business-full-seal-v1'),
        ('pg2992-current-resume-terminal-v1', terminal.SLOT), ('pg2990-current-resume-live-binding-v1', 'pg3124-browser-resume-live-binding-v1'),
        ('pg3004-current-resume-parent-projection-v1', 'pg3148-browser-business-parent-projection-v1'),
        ('pg3010-current-resume-owned-stage-v1', 'pg3154-browser-business-owned-stage-v1'),
        ('pg3012-current-resume-owned-post-v1', 'pg3156-browser-business-owned-post-v1'),
        ('PG3012-current-resume-owned-post-v1', 'PG3156-browser-business-owned-post-v1'),
        ('pg3006', 'pg3150'), ('Pg3006', 'Pg3150'), ('PG3006', 'PG3150'),
        ('pg3008', 'pg3152'), ('pg3010', 'pg3154'), ('pg3011', 'pg3155'), ('pg3013', 'pg3157'),
    ]:
        raw = raw.replace(old, new)
    return raw


def namespace():
    base = previous.previous.prior.previous
    ns = {**base.__dict__, 'SOURCE': SOURCE, 'TOOLS': TOOLS, 'terminal_payload': terminal.payload, 'candidate_bom': lambda: BOM}
    for fn in [base.context, base.emit_receipt, base.emit, base.sources]:
        exec(compile(bind(inspect.getsource(fn)), '<actual composite Browser owned graph>', 'exec'), ns)
    return ns


def context():
    return namespace()['context']()


def sources():
    return {bind(name): bind(raw) for name, raw in namespace()['sources']().items()}


def emit(ctx, live, state, fields):
    return {bind(name): bind(raw) for name, raw in namespace()['emit'](ctx, live, state, fields, BOM).items()}
