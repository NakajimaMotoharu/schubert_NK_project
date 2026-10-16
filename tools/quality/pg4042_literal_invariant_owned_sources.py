"""New composite/parent18-bound owned stop; immutable nested data never rewritten."""
import inspect
import re
import pg3822_hygiene_owned_sources as previous
import pg4022_literal_invariant_acceptance as acceptance
import pg4038_literal_invariant_browser_composite as composite
from immutable_payload_binding import bind_preserving_payloads

SOURCE, BOM = acceptance.SOURCE, acceptance.BOM
TOOLS = 'pg4042-literal-invariant-owned-tools-v1'


class Current:
    SOURCE = SOURCE; BOM = BOM; SEAL = composite.SLOT; TERM = acceptance.TERM
    terminal_payload = staticmethod(acceptance.terminal_payload)
    seal_payload = staticmethod(composite.payload)


current = Current


def role_text(raw):
    pairs = {previous.TOOLS: TOOLS, previous.SOURCE: SOURCE, previous.BOM: BOM,
             previous.composite.SLOT: composite.SLOT, previous.acceptance.TERM: acceptance.TERM, previous.acceptance.LIVE: acceptance.LIVE,
             'PG3748': 'PG3976', 'pg3748': 'pg3976', 'pg3818-hygiene-parent-projection-v1': 'pg4040-literal-invariant-parent-projection-v1',
             'pg3826-hygiene-owned-stage-v1': 'pg4046-literal-invariant-owned-stage-v1', 'pg3828-hygiene-owned-post-v1': 'pg4048-literal-invariant-owned-post-v1',
             'PG3828-hygiene-owned-post-v1': 'PG4048-literal-invariant-owned-post-v1', 'pg3822': 'pg4042', 'Pg3822': 'Pg4042', 'PG3822': 'PG4042',
             'pg3824': 'pg4044', 'pg3826': 'pg4046', 'pg3827': 'pg4047', 'pg3829': 'pg4049'}
    pattern = '|'.join(re.escape(k) for k in sorted(pairs, key=len, reverse=True))
    def replace(match):
        old = match.group(); first, last = match.span()
        if re.fullmatch('[a-f0-9]{40,64}', old) and ((first > 0 and raw[first - 1] in '0123456789abcdefABCDEF') or (last < len(raw) and raw[last] in '0123456789abcdefABCDEF')): return old
        return pairs[old]
    return re.sub(pattern, replace, raw)


def final_bind(raw): return bind_preserving_payloads(raw, lambda text: role_text(previous.final_bind(text)))


def bind(raw): return bind_preserving_payloads(raw, lambda text: role_text(previous.bind(text)))


def candidate_bom(): return BOM


def namespace():
    original = previous.previous.original
    values = {**original.__dict__, 'SOURCE': SOURCE, 'BOM': BOM, 'TOOLS': TOOLS, 'bind': bind, 'current': current}
    exec(compile(inspect.getsource(original.namespace), '<whole new current owned graph>', 'exec'), values)
    return values['namespace']()


def context(): return namespace()['context']()


def sources(): return {final_bind(name): final_bind(raw) for name, raw in namespace()['sources']().items()}
