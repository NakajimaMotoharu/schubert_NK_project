"""Finite code-only publication after actual RO post; prior Root remains history."""
import inspect
import json
import pg4880_ssc301_302_publication_sources as previous
import pg5000_ssc304_ro_sources as ro
from immutable_payload_binding import bind_preserving_payloads

W = ro.W
CURRENT, CURRENT_BOM, SOURCE, BOM, BEFORE, BOOT = ro.CURRENT, ro.unused.CURRENT_BOM, ro.SOURCE, ro.BOM, ro.BEFORE, ro.unused.BOOT
TOOLS = 'pg5008-ssc304-publication-tools-v1'
SAVE = 'pg5012-ssc304-publication-v1'
CLASS = 'Pg5008OrdinaryPublication'
BASE = previous.BASE


def qualify():
    ro.qualify()
    outer = json.loads((W / 'pg5006-ssc304-ro-independent-post-v1/manifest.safe.json').read_bytes())
    r = outer.get('result', {})
    if not (type(outer.get('actualExit')) is int and outer['actualExit'] == 0
            and type(r.get('actualExit')) is int and r['actualExit'] == 0
            and r.get('candidateHostReadonlyVerified') is True and r.get('candidateSource') == SOURCE
            and r.get('currentSource') == CURRENT and r.get('candidateManifestSha256') == BOM
            and r.get('allClientAdvisoryMA0') is True and r.get('newTenReferencesReturnedNormally') is True
            and r.get('native80Preserved') is True):
        raise ValueError('actual PID1 RO/full80 independent post first')
    return r


def bind(raw):
    raw = ro.unused.role_text(raw)
    for a, b in [('pg3450-current-outbox-publication-tools-v1', TOOLS), ('pg3456-current-outbox-publication-v1', SAVE),
                 ('pg3446-current-outbox-ro-completed-v1', ro.SAVE), ('pg3450', 'pg5008'), ('Pg3450', 'Pg5008'), ('PG3450', 'PG5008'),
                 ('pg3452', 'pg5010'), ('PG3452', 'PG5010'), ('pg3454', 'pg5012'), ('PG3454', 'PG5012')]:
        raw = raw.replace(a, b)
    return raw


def alias(raw):
    return bind_preserving_payloads(raw, lambda v: v.replace('pg5000', 'pg5008').replace('PG5000', 'PG5008'))


def sources(bom=BOM, before=BEFORE):
    ns = {**vars(previous), 'ro': ro, 'W': W, 'CURRENT': CURRENT, 'SOURCE': SOURCE, 'BOM': BOM,
          'BEFORE': BEFORE, 'TOOLS': TOOLS, 'SAVE': SAVE, 'CLASS': CLASS, 'BASE': BASE,
          'qualify': qualify, 'bind': bind, 'alias': alias}
    raw = inspect.getsource(previous.sources)
    for a, b in [('pg4880', 'pg5008'), ('Pg4880', 'Pg5008'), ('PG4880', 'PG5008'),
                 ('pg4872', 'pg5000'), ('Pg4872', 'Pg5000'), ('PG4872', 'PG5000')]:
        raw = raw.replace(a, b)
    exec(compile(raw, '<finite current04bb/candidatea2ecc24>', 'exec'), ns)
    return ns['sources'](bom, before)


if __name__ == '__main__':
    raise SystemExit('pure factory; no guest action')
