"""Finite new code-only publication graph; completed prior tuple is never a new Root start."""
import inspect
import json
import pg3788_hygiene_publication_sources as previous
import pg3994_literal_invariant_ro_sources as ro
from immutable_payload_binding import bind_preserving_payloads

W = ro.W
CURRENT, CURRENT_BOM, SOURCE, BOM, BEFORE, BOOT = ro.CURRENT, ro.unused.CURRENT_BOM, ro.SOURCE, ro.BOM, ro.BEFORE, ro.unused.BOOT
TOOLS = 'pg4002-literal-invariant-publication-tools-v1'; SAVE = 'pg4006-literal-invariant-publication-v1'; CLASS = 'Pg4002OrdinaryPublication'
BASE = previous.BASE


def qualify():
    ro.qualify()
    proof = json.loads((W / 'pg4000-literal-invariant-ro-independent-post-v1/manifest.safe.json').read_bytes()); result = proof.get('result', {})
    if not (proof.get('actualExit') == result.get('actualExit') == 0 and result.get('candidateHostReadonlyVerified') is True and result.get('candidateSource') == SOURCE
            and result.get('currentSource') == CURRENT and result.get('candidateManifestSha256') == BOM and result.get('allClientAdvisoryMA0') is True and result.get('newTenReferencesReturnedNormally') is True):
        raise ValueError('actual same-source new RO/full current post required')
    return result


def bind(raw):
    raw = ro.unused.role_text(raw)
    for old, new in [('pg3450-current-outbox-publication-tools-v1', TOOLS), ('pg3456-current-outbox-publication-v1', SAVE),
                     ('pg3446-current-outbox-ro-completed-v1', ro.SAVE), ('pg3450', 'pg4002'), ('Pg3450', 'Pg4002'), ('PG3450', 'PG4002'),
                     ('pg3452', 'pg4004'), ('PG3452', 'PG4004'), ('pg3454', 'pg4006'), ('PG3454', 'PG4006')]: raw = raw.replace(old, new)
    return raw


def alias(raw): return bind_preserving_payloads(raw, lambda text: text.replace('pg3994', 'pg4002').replace('PG3994', 'PG4002'))


def sources(bom=BOM, before=BEFORE):
    namespace = {**previous.__dict__, 'W': W, 'CURRENT': CURRENT, 'SOURCE': SOURCE, 'BOM': BOM, 'BEFORE': BEFORE, 'TOOLS': TOOLS,
                 'SAVE': SAVE, 'CLASS': CLASS, 'BASE': BASE, 'qualify': qualify, 'mapping': ro.unused, 'ro': ro, 'bind': bind, 'alias': alias}
    raw = inspect.getsource(previous.sources)
    for old, new in [('pg3788', 'pg4002'), ('Pg3788', 'Pg4002'), ('PG3788', 'PG4002'), ('pg3780', 'pg3994'), ('Pg3780', 'Pg3994'), ('PG3780', 'PG3994')]: raw = raw.replace(old, new)
    marker = "normal['pg3994_'+suffix].replace('pg3994','pg4002').replace('PG3994','PG4002')"
    if raw.count(marker) != 1: raise ValueError('one protected completed tuple publication alias boundary')
    raw = raw.replace(marker, "alias(normal['pg3994_'+suffix])")
    exec(compile(raw, '<all twenty-four new finite publication roles>', 'exec'), namespace)
    return namespace['sources'](bom, before)
