"""New unused-role graph; latest completed Root stays historical data, not start authority."""
import inspect
import json
import re
from functools import lru_cache
import pg3756_hygiene_unused_sources as previous
import pg3876_current_resume_owned_sources as completed
from immutable_payload_binding import bind_preserving_payloads
from bundle_hash_contract import unbind
from pg3976_literal_invariant_signed_candidate import SOURCE, OLD_SOURCE as CURRENT, OLD_BOM as CURRENT_BOM

W = previous.W
BOM = '0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'
BEFORE = '60b53f6b877e979f2931a03ab55eb15892f1aeb9450ee6a6d39007adc9ea8b88'
BOOT = previous.BOOT
TOOLS = 'pg3982-literal-invariant-unused-tools-v1'
SAVE = 'pg3986-literal-invariant-unused-placement-v1'
ARCHIVE = 'pg3986-literal-invariant-release-v1.tar'
REMOTE = '/home/ubuntu/pg3986-literal-invariant-input-v1'
VIEW_LOCAL = W / 'pg3980-current-before-view-v1/manifest.safe.json'
BASE = previous.BASE
LATEST = W / completed.TOOLS
pinned = previous.pinned


def candidate_bom():
    value = json.loads((W / 'pg3976-candidate-build-v1.safe.json').read_bytes())
    if not (value['actualExit'] == 0 and value['candidateSource'] == SOURCE and value['signatureVerified'] and value['candidateNotDeployed'] and value['manifestSha256'] == BOM):
        raise ValueError('one actual new-source host signature receipt required')
    return value['manifestSha256']


def production(): return SOURCE


def qualify():
    readonly = json.loads((W / 'pg3978-current-preservation-readonly-v1/manifest.safe.json').read_bytes())
    view = json.loads(VIEW_LOCAL.read_bytes()); candidate_bom()
    r = readonly['result']; v = view['result']
    if not (readonly['actualExit'] == view['actualExit'] == 0 and r['deployedSource'] == v['productionSource'] == CURRENT and r['BOM'] == v['BOM'] == CURRENT_BOM
            and r['native46Preserved'] and v['privateBeforeSha256'] == BEFORE and v['nativePhysicalFilesPreserved'] == 46
            and v['dataOnlyNotRuntimeAuthority'] and not v['nativeCandidateCredit'] and r['currentOriginalClosedAndNoIntent']):
        raise ValueError('separate fresh preserved old data and new unused candidate authorities required')


def normalized_text(raw):
    pairs = {previous.CURRENT: CURRENT, previous.SOURCE: SOURCE, previous.CURRENT_BOM: CURRENT_BOM, previous.BOM: candidate_bom(), previous.BEFORE: BEFORE,
             'PG3748': 'PG3976', 'pg3748': 'pg3976', 'PG3420': 'PG3748', 'pg3420': 'pg3748',
             'pg3754-current-4856-before-view-v1': 'pg3980-current-7fff-before-view-v1',
             'pg3754-current-before-view-v1': 'pg3980-current-before-view-v1',
             previous.TOOLS: TOOLS, previous.SAVE: SAVE, previous.ARCHIVE: ARCHIVE, previous.REMOTE: REMOTE,
             'pg3756': 'pg3982', 'Pg3756': 'Pg3982', 'PG3756': 'PG3982', 'pg3758': 'pg3984', 'PG3758': 'PG3984',
             'pg3760': 'pg3986', 'PG3760': 'PG3986', 'pg3762': 'pg3988', 'PG3762': 'PG3988'}
    pattern = '|'.join(re.escape(key) for key in sorted(pairs, key=len, reverse=True))
    def replace(match):
        old = match.group(); first, last = match.span()
        if re.fullmatch('[a-f0-9]{40,64}', old) and ((first > 0 and raw[first - 1] in '0123456789abcdefABCDEF') or (last < len(raw) and raw[last] in '0123456789abcdefABCDEF')):
            return old
        return pairs[old]
    return re.sub(pattern, replace, raw)


def role_text(raw): return normalized_text(previous.role_text(raw))


@lru_cache(maxsize=1)
def current_tuple():
    values = {**previous.__dict__, 'LATEST': LATEST, 'completed': completed, 'BOOT': BOOT}
    raw = inspect.getsource(previous.current_tuple.__wrapped__).replace('pg3600_parent_receipt.py', 'pg3876_parent_receipt.py')
    exec(compile(raw, '<latest genuinely completed current Root data>', 'exec'), values)
    return values['current_tuple']()


def native_refs(raw):
    values = {**previous.__dict__, 'current_tuple': current_tuple}
    exec(compile(inspect.getsource(previous.native_refs), '<latest completed ref data only>', 'exec'), values)
    return values['native_refs'](raw)


def latest_alias(raw):
    return bind_preserving_payloads(raw, lambda text: text.replace('pg3876', 'pg3982').replace('PG3876', 'PG3982'))


def sources(bom=None, before=None):
    qualify(); actual = candidate_bom()
    if bom is not None and bom != actual or before is not None and before != BEFORE:
        raise ValueError('one fixed actual candidate/current data role')
    namespace = {**previous.__dict__, 'CURRENT': CURRENT, 'CURRENT_BOM': CURRENT_BOM, 'SOURCE': SOURCE, 'BOM': actual, 'BEFORE': BEFORE, 'BOOT': BOOT,
                 'TOOLS': TOOLS, 'SAVE': SAVE, 'ARCHIVE': ARCHIVE, 'REMOTE': REMOTE, 'BASE': BASE, 'LATEST': LATEST,
                 'qualify': qualify, 'role_text': role_text, 'current_tuple': current_tuple, 'native_refs': native_refs, 'latest_alias': latest_alias}
    raw = inspect.getsource(previous.sources)
    raw = raw.replace('bom=BOM,before=BEFORE', 'bom=None,before=None')
    raw = raw.replace('if bom!=BOM or before!=BEFORE:', 'if bom is not None and bom!=BOM or before is not None and before!=BEFORE:')
    for old, new in [('pg3756', 'pg3982'), ('Pg3756', 'Pg3982'), ('PG3756', 'PG3982'), ('pg3600', 'pg3876'), ('Pg3600', 'Pg3876'), ('PG3600', 'PG3876')]: raw = raw.replace(old, new)
    marker = "pinned(LATEST,'pg3876_'+suffix+'.py').replace('pg3876','pg3982').replace('PG3876','PG3982')"
    if raw.count(marker) != 1: raise ValueError('one protected latest receipt namespace boundary')
    raw = raw.replace(marker, "latest_alias(pinned(LATEST,'pg3876_'+suffix+'.py'))")
    exec(compile(raw, '<all eighteen new unused source roles>', 'exec'), namespace)
    values = namespace['sources']()
    for name in ['pg3982_native_refs.py', 'pg3982_input_preflight.py']:
        values[name] = unbind(values[name])
    return values


if __name__ == '__main__': raise SystemExit('factory only; no VM operation')
