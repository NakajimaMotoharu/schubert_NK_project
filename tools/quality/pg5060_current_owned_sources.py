"""Normal a2ecc owned graph; immutable newday SQL/Browser capsules never rebound."""
import inspect
import json
import pg4916_current_owned_sources as previous
import pg5036_current_admission_image as admission
import pg5038_current_genuine_terminal as acceptance
import pg5048_current_same_owner_browser as actual
import pg5050_current_browser_composite as composite
import pg5052_current_parent_projection as projection
from immutable_payload_binding import bind_preserving_payloads

SOURCE, BOM = admission.SOURCE, admission.BOM
TOOLS = 'pg5060-current-owned-tools-v1'


def composite_payload(binding):
    return composite.payload(binding)


class Current:
    SOURCE = SOURCE
    BOM = BOM
    SEAL = composite.SLOT
    TERM = acceptance.TERM
    terminal_payload = staticmethod(acceptance.payload)
    seal_payload = staticmethod(composite_payload)


current = Current


def role_text(raw):
    pairs = [(previous.SOURCE, SOURCE), (previous.BOM, BOM), (previous.TOOLS, TOOLS),
             (previous.composite.SLOT, composite.SLOT), (previous.acceptance.TERM, acceptance.TERM),
             (previous.admission.LIVE, admission.LIVE), (previous.projection.SLOT, projection.SLOT),
             ('PG4860', 'PG4980'), ('pg4860', 'pg4980'),
             ('pg4920-current-owned-stage-v1', 'pg5064-current-owned-stage-v1'),
             ('pg4922-current-owned-post-v1', 'pg5066-current-owned-post-v1'),
             ('PG4922-current-owned-post-v1', 'PG5066-current-owned-post-v1'),
             ('pg4916', 'pg5060'), ('Pg4916', 'Pg5060'), ('PG4916', 'PG5060'),
             ('pg4918', 'pg5062'), ('pg4920', 'pg5064'), ('pg4921', 'pg5063'), ('pg4923', 'pg5065')]
    for a, b in pairs:
        raw = raw.replace(a, b)
    return raw


def bind(raw):
    return bind_preserving_payloads(previous.bind(raw), role_text)


def final_bind(raw):
    return bind_preserving_payloads(previous.final_bind(raw), role_text)


def candidate_bom():
    return BOM


def namespace():
    composer = previous.previous.composer
    ns = {**vars(composer), 'SOURCE': SOURCE, 'BOM': BOM, 'TOOLS': TOOLS, 'bind': bind,
          'current': current, 'candidate_bom': candidate_bom}
    exec(compile(inspect.getsource(composer.namespace), '<currenta2ecc normal owned graph>', 'exec'), ns)
    result = ns['namespace']()
    result['terminal_payload'] = acceptance.payload
    return result


def context():
    seal, term = actual.receipt(composite.SLOT), actual.receipt(acceptance.TERM)
    if not (seal['sqlOracleQualified'] and seal['currentFourOwnedLive'] and term['normalUnit0or10']
            and seal['businessOracle']['exactRootBrowserCurrentChain']):
        raise ValueError('actual current Root/Browser/exact24 normal chain first')
    return seal['privateBeforeSha256'], seal['observedOwned'], seal['genuineCompletion'], seal['doneEndUtc']


def emit(ctx, binding, state, fields):
    return {final_bind(name): final_bind(raw) for name, raw in namespace()['emit'](ctx, binding, state, fields).items()}


def sources():
    b = admission.live()
    binding = {'binding': {k: v for k, v in b.items() if k != 'rootPid'}, 'rootPid': b['rootPid']}
    term = actual.receipt(acceptance.TERM)
    proof = json.loads((admission.W / projection.SLOT / 'manifest.safe.json').read_bytes())
    ctx = context()
    if not (type(proof['actualExit']) is int and proof['actualExit'] == 0 and proof['source'] == SOURCE
            and proof['result']['sealedBeforeSha256'] == ctx[0]):
        raise ValueError('actual current exact parent18 projection')
    return emit(ctx, binding, term['parentState'], proof['result']['parentState18'])
