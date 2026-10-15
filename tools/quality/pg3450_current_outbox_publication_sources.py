"""Signed4856 finite publication after independent actual RO, never a business start."""
import json
from pyflakes.api import check

import pg2674_operation_publication_sources as old
import pg3442_current_outbox_ro_sources as ro

TOOLS = 'pg3450-current-outbox-publication-tools-v1'
SAVE = 'pg3456-current-outbox-publication-v1'
CLASS = 'Pg3450OrdinaryPublication'
CURRENT, CURRENT_BOM, BEFORE, BOOT = ro.role.CURRENT, ro.role.CURRENT_BOM, ro.role.BEFORE, ro.role.BOOT
W = ro.W


def production():
    return ro.role.SOURCE


def candidate_bom():
    ro.qualify()
    v = json.loads((W / 'pg3448-current-outbox-ro-independent-post-v1/manifest.safe.json').read_bytes())
    if (type(v.get('actualExit')) is not int or v['actualExit'] != 0
            or v['guest'].get('candidateSource') != production()
            or v['guest'].get('candidateManifestSha256') != ro.role.BOM
            or v['guest'].get('candidateHostReadonlyVerified') is not True):
        raise ValueError('same signed candidate independent actual PID1 host RO required')
    return ro.role.BOM


def bind(raw, bom):
    if bom != ro.role.BOM:
        raise ValueError('exact actual signed candidate BOM, not a pending marker')
    raw = ro.bind(raw)
    for a, b in [(old.TOOLS, TOOLS), (old.SAVE, SAVE), ('pg2674', 'pg3450'),
                 ('Pg2674', 'Pg3450'), ('PG2674', 'PG3450'),
                 ('pg2670-operation-host-ro-v1', ro.SAVE),
                 ('pg2672-operation-ro-post-v1', 'pg3448-current-outbox-ro-independent-post-v1')]:
        raw = raw.replace(a, b)
    return raw


def sources(bom=None):
    actual = candidate_bom()
    if bom is None:
        bom = actual
    if bom != actual:
        raise ValueError('one source/BOM fixed before generation')
    values = {bind(n, bom): bind(raw, bom) for n, raw in old.sources(bom).items()}
    normal = ro.sources()
    for suffix in ['parent_receipt.py', 'warning_parent_projection.py']:
        values['pg3450_' + suffix] = normal['pg3442_' + suffix]
    for name, raw in values.items():
        if any(v in raw for v in [ro.role.old.BOOT, ro.role.old.CURRENT,
                                  ro.role.old.SOURCE, ro.role.old.BEFORE,
                                  'NORMAL_DAEMON_RELOAD', 'REGULAR_MORNING_UNIT_EXCHANGE']):
            raise ValueError('old role or duplicate action remains: ' + name)
        if name.endswith('.py'):
            prefix = "BUNDLE_HASH='pending-real-bundle'\n" if name == 'pg3450_native_refs.py' else ''
            if check(prefix + raw, '<whole current/candidate finite publication graph>'):
                raise ValueError('all finite publication exports required')
            compile(raw, '<new current/candidate publication>', 'exec')
    return values


if __name__ == '__main__':
    raise SystemExit('source factory only')
