"""Independent seven finite phases/new signed current; old80 are preservation only."""
import inspect
import json
import types
import pg4886_ssc301_302_publication_post as previous
import pg5008_ssc304_publication_sources as role
from pg4996_resume_connection import authenticate_host

SLOT = 'pg5014-ssc304-publication-independent-post-v1'
FULL_BEFORE = '/var/lib/pgpt-s1-preservation/pg4982-current-preservation-readonly-v1/before.private.json'
FULL_SHA = role.BEFORE


def readonly_source():
    raw = previous.readonly_source()
    changes = {previous.role.SOURCE: role.SOURCE, previous.role.BOM: role.BOM,
               'PG4860': 'PG4980', 'pg4860-manifest.sig': 'pg4980-manifest.sig',
               previous.FULL_BEFORE: FULL_BEFORE, previous.FULL_SHA: FULL_SHA,
               '==72)': '==80)', 'native72Preserved': 'native80Preserved'}
    for a, b in changes.items():
        if a not in raw:
            raise ValueError('one new signed current reader boundary ' + a)
        raw = raw.replace(a, b)
    return raw


def publication():
    template = previous.previous.old
    ns = {**vars(template), 'role': role}
    raw = inspect.getsource(template.publication).replace('pg3788_ordinary_publication_contract', 'pg5008_ordinary_publication_contract')
    exec(compile(raw, '<every finite phase independent oracle>', 'exec'), ns)
    value = ns['publication']()
    if value.count('old_after=after') != 1:
        raise ValueError('one complete current baseline')
    return value.replace('old_after=after', "old_after={**after,'native':expected['native']}", 1)


def payload():
    template = previous.previous
    ns = {**vars(template), 'role': role, 'SLOT': SLOT,
          'readonly_source': readonly_source, 'publication': publication}
    raw = inspect.getsource(template.payload)
    for a, b in [('pg4724-frozen-v1.safe.json', 'pg5010-frozen-v1.safe.json'),
                 ('pg4706_configuration_capture.py', 'pg4986_configuration_capture.py'),
                 ('originalBackupNative64Preserved', 'originalBackupNative80Preserved')]:
        raw = raw.replace(a, b)
    exec(compile(raw, '<full80/new currenta2ecc independent post>', 'exec'), ns)
    return ns['payload']()


def main():
    actual = json.loads((role.W / 'pg5012-activate-v1.safe.json').read_bytes())
    if not (type(actual.get('actualExit')) is int and actual['actualExit'] == 0
            and actual.get('sourceQualified') is True and actual.get('candidateSource') == role.SOURCE
            and actual.get('currentApprovalEpochChanged') is True):
        raise ValueError('actual finite publication first')
    authenticate_host()
    transport = previous.previous.transport
    execute = types.FunctionType(transport.execute.__code__, {**vars(transport), 'SOURCE': role.SOURCE})
    return execute(SLOT, payload(), 180)


if __name__ == '__main__':
    raise SystemExit(main())
