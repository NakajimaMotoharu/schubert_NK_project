"""Normal completed current data plus distinct SSC299 unused candidate: no failed-parent role."""
import inspect
import json
import re
from functools import lru_cache
import pg3982_literal_invariant_unused_sources as previous
import pg4652_current_owned_sources as completed
from immutable_payload_binding import bind_preserving_payloads
from pg4694_ssc299_full import SOURCE, W

CURRENT = completed.SOURCE
CURRENT_BOM = completed.BOM
BEFORE = '612beec0ca58fcf4ecc7a15e21f4dfedd574608ba3ce947d20c6d3be728d3b90'
BOOT = previous.BOOT
TOOLS = 'pg4706-ssc299-unused-tools-v1'
SAVE = 'pg4710-ssc299-unused-placement-v1'
ARCHIVE = 'pg4710-ssc299-release-v1.tar'
REMOTE = '/home/ubuntu/pg4710-ssc299-input-v1'
VIEW_LOCAL = W / 'pg4704-current-preservation-readonly-v1/manifest.safe.json'
BASE, pinned = previous.BASE, previous.pinned
LATEST = W / completed.TOOLS


def candidate_bom():
    value = json.loads((W / 'pg4702-candidate-build-v1.safe.json').read_bytes())
    if not (type(value['actualExit']) is int and value['actualExit'] == 0
            and value['candidateSource'] == SOURCE and value['priorSource'] == CURRENT
            and value['signatureVerified'] is True and value['candidateNotDeployed'] is True
            and value['formalAccepted'] is False and value['allSixFormatBeforeAnyPt'] is False):
        raise ValueError('actual distinct host-signed candidate, not formal or old runtime authority')
    return value['manifestSha256']


def production(): return SOURCE


def qualify():
    outer = json.loads(VIEW_LOCAL.read_bytes()); v = outer['result']; candidate_bom()
    expected = {'actualExit': 0, 'productionSource': CURRENT, 'freshCurrentPreservation': True,
                'all24UnchangedTwice': True, 'allTenUnitsKernelEmpty': True, 'allActorGone': True,
                'allClientAdvisoryFlock0': True, 'whole187SignedArtifactBytesVerified': True,
                'normalCurrentOwnedStopScopesSealed': True, 'currentNormalWarningParentProof': True,
                'normalNewMetadataScopes': True, 'nativePhysicalFiles': 64,
                'privateBeforeSha256': BEFORE, 'dataOnlyNotRuntimeAuthority': True,
                'nativeCandidateCredit': False, 'currentOriginalClosedAndNoIntent': True,
                'runtimeConfigFilesToRetire': 0}
    if type(outer['actualExit']) is not int or outer['actualExit'] != 0 or outer['source'] != CURRENT:
        raise ValueError('actual fresh normal current proof required')
    if any(type(v.get(k)) is not type(x) or v[k] != x for k,x in expected.items()):
        raise ValueError('every normal stopped data criterion must match')


def normalized_text(raw):
    pairs = {previous.CURRENT: CURRENT, previous.SOURCE: SOURCE, previous.CURRENT_BOM: CURRENT_BOM,
             previous.BOM: candidate_bom(), previous.BEFORE: BEFORE,
             'PG3976': 'PG4702', 'pg3976': 'pg4702', 'PG3748': 'PG4432', 'pg3748': 'pg4432',
             'pg3980-current-7fff-before-view-v1': 'pg4704-current-preservation-readonly-v1',
             'pg3980-current-before-view-v1': 'pg4704-current-preservation-readonly-v1',
             previous.TOOLS: TOOLS, previous.SAVE: SAVE, previous.ARCHIVE: ARCHIVE, previous.REMOTE: REMOTE,
             'pg3982': 'pg4706', 'Pg3982': 'Pg4706', 'PG3982': 'PG4706',
             'pg3984': 'pg4708', 'PG3984': 'PG4708', 'pg3986': 'pg4710', 'PG3986': 'PG4710',
             'pg3988': 'pg4712', 'PG3988': 'PG4712'}
    pattern = '|'.join(re.escape(k) for k in sorted(pairs, key=len, reverse=True))
    def replace(match):
        token = match.group(); first, last = match.span()
        if re.fullmatch('[a-f0-9]{40,64}', token) and ((first and raw[first-1] in '0123456789abcdefABCDEF') or (last < len(raw) and raw[last] in '0123456789abcdefABCDEF')):
            return token
        return pairs[token]
    return re.sub(pattern, replace, raw)


def role_text(raw): return normalized_text(previous.role_text(raw))


@lru_cache(maxsize=1)
def current_tuple():
    current = previous.previous.previous.binding(pinned(LATEST, 'pg4652_parent_receipt.py'))
    _, _, summary, ended = completed.context()
    if current['boot'] != BOOT.replace('-', '') or summary['genuineParentDone'] is not True or summary['completionCode'] != 10:
        raise ValueError('actual completed current normal tuple is historical data only')
    return current, summary, ended


def native_refs(raw):
    ns = {**vars(previous.previous), 'current_tuple': current_tuple}
    exec(compile(inspect.getsource(previous.previous.native_refs), '<current normal original tuple fields>', 'exec'), ns)
    return ns['native_refs'](raw)


def latest_alias(raw):
    return bind_preserving_payloads(raw, lambda text: text.replace('pg4652','pg4706').replace('PG4652','PG4706'))


def sources(bom=None, before=None):
    qualify(); actual = candidate_bom()
    if bom is not None and bom != actual or before is not None and before != BEFORE:
        raise ValueError('one exact normal current/candidate role')
    ns = {**vars(previous), 'CURRENT':CURRENT,'CURRENT_BOM':CURRENT_BOM,'SOURCE':SOURCE,'BOM':actual,
          'BEFORE':BEFORE,'BOOT':BOOT,'TOOLS':TOOLS,'SAVE':SAVE,'ARCHIVE':ARCHIVE,'REMOTE':REMOTE,
          'BASE':BASE,'LATEST':LATEST,'qualify':qualify,'role_text':role_text,
          'current_tuple':current_tuple,'native_refs':native_refs,'latest_alias':latest_alias,
          'candidate_bom':candidate_bom}
    raw = inspect.getsource(previous.sources)
    for old,new in [('pg3982','pg4706'),('Pg3982','Pg4706'),('PG3982','PG4706'),
                    ('pg3876','pg4652'),('Pg3876','Pg4652'),('PG3876','PG4652')]: raw = raw.replace(old,new)
    exec(compile(raw, '<normal current SSC299 unused eighteen roles>', 'exec'), ns)
    return ns['sources']()


if __name__ == '__main__': raise SystemExit('pure factory; no VM action')
