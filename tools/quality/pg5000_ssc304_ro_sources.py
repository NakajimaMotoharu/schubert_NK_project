"""Same stopped04bb/full80 and distinct a2ecc candidate, RO-only role."""
import inspect
import json
import pg4872_ssc301_302_ro_sources as previous
import pg4986_ssc304_unused_sources as unused
from immutable_payload_binding import bind_preserving_payloads

W = unused.W
CURRENT, SOURCE, BEFORE = unused.CURRENT, unused.SOURCE, unused.BEFORE
BOM = unused.candidate_bom()
TOOLS = 'pg5000-ssc304-ro-tools-v1'
SAVE = 'pg5004-ssc304-ro-completed-v1'
CLASS = 'Pg5000CandidateRo'
BASE = previous.BASE


def qualify():
    unused.qualify()
    outer = json.loads((W / 'pg4992-ssc304-unused-post-v1/manifest.safe.json').read_bytes())
    r = outer.get('result', {})
    flags = ('candidateUnusedOnly', 'candidate187SignatureVerified', 'current187SignatureVerified',
             'configuration32EveryFieldUnchanged', 'all24TablesEqualTwice', 'allClientAdvisoryMA0',
             'newTenReferencesReturnedNormally', 'native80Preserved', 'runtimeStartupAndApprovalEpochUnchanged')
    if not (type(outer.get('actualExit')) is int and outer['actualExit'] == 0
            and type(r.get('actualExit')) is int and r['actualExit'] == 0
            and r.get('candidateSource') == SOURCE and r.get('currentSource') == CURRENT
            and r.get('candidateManifestSha256') == BOM and all(r.get(k) is True for k in flags)):
        raise ValueError('actual independent current04bb/full80 and unused candidate187 post')
    return r


def bind(raw):
    raw = unused.role_text(raw)
    for a, b in [('pg3442-current-outbox-ro-tools-v1', TOOLS), ('pg3446-current-outbox-ro-completed-v1', SAVE),
                 ('pg3442', 'pg5000'), ('Pg3442', 'Pg5000'), ('PG3442', 'PG5000'),
                 ('pg3444', 'pg5002'), ('PG3444', 'PG5002'), ('pg3446', 'pg5004'), ('PG3446', 'PG5004')]:
        raw = raw.replace(a, b)
    return raw


def alias(raw):
    return bind_preserving_payloads(raw, lambda v: v.replace('pg4986', 'pg5000').replace('PG4986', 'PG5000'))


def sources(bom=BOM, before=BEFORE):
    ns = {**vars(previous), 'unused': unused, 'W': W, 'CURRENT': CURRENT, 'SOURCE': SOURCE,
          'BOM': BOM, 'BEFORE': BEFORE, 'TOOLS': TOOLS, 'SAVE': SAVE, 'CLASS': CLASS,
          'BASE': BASE, 'qualify': qualify, 'bind': bind, 'alias': alias}
    raw = inspect.getsource(previous.sources).replace('pg4872', 'pg5000').replace('Pg4872', 'Pg5000').replace('PG4872', 'PG5000')
    raw = raw.replace('pg4864', 'pg4986').replace('Pg4864', 'Pg4986').replace('PG4864', 'PG4986')
    exec(compile(raw, '<actual current04bb/full80 RO role>', 'exec'), ns)
    return ns['sources'](bom, before)


if __name__ == '__main__':
    raise SystemExit('pure factory; no guest action')
