"""New candidate RO graph after actual unused post; old completed tuple remains data."""
import inspect
import json
import pg3780_hygiene_ro_sources as previous
import pg3982_literal_invariant_unused_sources as unused
from immutable_payload_binding import bind_preserving_payloads

W = unused.W
CURRENT, SOURCE, BOM, BEFORE = unused.CURRENT, unused.SOURCE, unused.BOM, unused.BEFORE
TOOLS = 'pg3994-literal-invariant-ro-tools-v1'; SAVE = 'pg3998-literal-invariant-ro-completed-v1'; CLASS = 'Pg3994CandidateRo'
BASE = previous.BASE


def qualify():
    unused.qualify()
    proof = json.loads((W / 'pg3988-hygiene-unused-post-v1/manifest.safe.json').read_bytes())
    result = proof.get('result', {})
    flags = ['candidateUnusedOnly', 'candidate187SignatureVerified', 'current187SignatureVerified', 'configuration32EveryFieldUnchanged',
             'all24TablesEqualTwice', 'allClientAdvisoryMA0', 'newTenReferencesReturnedNormally', 'native46Preserved', 'runtimeStartupAndApprovalEpochUnchanged']
    if not (proof.get('actualExit') == result.get('actualExit') == 0 and result.get('candidateSource') == SOURCE and result.get('currentSource') == CURRENT
            and result.get('candidateManifestSha256') == BOM and all(result.get(flag) is True for flag in flags)):
        raise ValueError('genuine current/native46/unused candidate full post required')
    return result


def bind(raw):
    raw = unused.role_text(raw)
    for old, new in [('pg3442-current-outbox-ro-tools-v1', TOOLS), ('pg3446-current-outbox-ro-completed-v1', SAVE),
                     ('pg3442', 'pg3994'), ('Pg3442', 'Pg3994'), ('PG3442', 'PG3994'),
                     ('pg3444', 'pg3996'), ('PG3444', 'PG3996'), ('pg3446', 'pg3998'), ('PG3446', 'PG3998')]: raw = raw.replace(old, new)
    return raw


def alias(raw): return bind_preserving_payloads(raw, lambda text: text.replace('pg3982', 'pg3994').replace('PG3982', 'PG3994'))


def sources(bom=BOM, before=BEFORE):
    namespace = {**previous.__dict__, 'W': W, 'CURRENT': CURRENT, 'SOURCE': SOURCE, 'BOM': BOM, 'BEFORE': BEFORE, 'TOOLS': TOOLS,
                 'SAVE': SAVE, 'CLASS': CLASS, 'BASE': BASE, 'qualify': qualify, 'mapping': unused, 'unused': unused, 'bind': bind, 'alias': alias}
    raw = inspect.getsource(previous.sources)
    for old, new in [('pg3780', 'pg3994'), ('Pg3780', 'Pg3994'), ('pg3766', 'pg3982'), ('Pg3766', 'Pg3982'), ('PG3766', 'PG3982')]: raw = raw.replace(old, new)
    marker = "normal['pg3982_'+suffix].replace('pg3982','pg3994').replace('PG3982','PG3780')"
    # This translation changes namespace tokens, never frozen oracle values.
    raw = raw.replace('PG3780', 'PG3994')
    marker = marker.replace('PG3780', 'PG3994')
    if raw.count(marker) != 1: raise ValueError('one protected latest parent/projection alias boundary')
    raw = raw.replace(marker, "alias(normal['pg3982_'+suffix])")
    exec(compile(raw, '<all eighteen new RO source roles>', 'exec'), namespace)
    return namespace['sources'](bom, before)
