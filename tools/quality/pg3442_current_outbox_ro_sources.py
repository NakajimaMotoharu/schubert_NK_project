"""Candidate-only RO graph after genuine unused full post; no publication or startup."""
import json
from pyflakes.api import check

import pg2666_operation_ro_sources as old
import pg3434_current_outbox_candidate_sources as role
from pg1446_current_cold_stage import W

TOOLS = 'pg3442-current-outbox-ro-tools-v1'
SAVE = 'pg3446-current-outbox-ro-completed-v1'
CLASS = 'Pg3442CandidateRo'


def qualify():
    role.qualify()
    v = json.loads((W / 'pg3440-current-outbox-unused-independent-post-v1/manifest.safe.json').read_bytes())
    g = v.get('guest', {})
    if (v['actualExit'] != 0 or g.get('actualExit') != 0 or g.get('candidateSource') != role.SOURCE
            or g.get('candidateManifestSha256') != role.BOM or not g.get('unusedCandidate187Verified')
            or not g.get('signatureVerified') or not g.get('allOriginalBackupAndNativeUnchanged')
            or not g.get('allClientAdvisoryFlock0') or not g.get('currentEpochApprovalUnchanged')):
        raise ValueError('genuine full unused candidate/current resource post required')


def bind(raw):
    raw = role.bind(raw)
    for a, b in [(old.TOOLS, TOOLS), (old.SAVE, SAVE), ('pg2666', 'pg3442'),
                 ('Pg2666', 'Pg3442'), ('PG2666', 'PG3442'), ('pg2670', 'pg3446'), ('PG2670', 'PG3446'),
                 ('pg2664-operation-unused-post-v1', 'pg3440-current-outbox-unused-independent-post-v1')]:
        raw = raw.replace(a, b)
    return raw


def sources(bom=role.BOM, before=role.BEFORE):
    qualify()
    if bom != role.BOM or before != role.BEFORE:
        raise ValueError('fixed same candidate/current before required')
    values = {bind(n): bind(raw) for n, raw in old.sources(bom).items()}
    normal = role.sources()
    for suffix in ['parent_receipt.py', 'warning_parent_projection.py']:
        values['pg3442_' + suffix] = normal['pg3434_' + suffix]
    for name, raw in values.items():
        if any(v in raw for v in [role.old.BOOT, role.old.SOURCE, role.old.CURRENT, role.old.BEFORE]):
            raise ValueError('old role remains in RO graph')
        if name.endswith('.py'):
            prelude = "BUNDLE_HASH='pending-real-bundle'\n" if name == 'pg3442_native_refs.py' else ''
            if check(prelude + raw, '<whole RO source ' + name + '>'):
                raise ValueError('complete RO namespace required')
            compile(raw, '<currenta9/new4856 RO graph>', 'exec')
    return values


if __name__ == '__main__':
    raise SystemExit('factory only; no operation')
