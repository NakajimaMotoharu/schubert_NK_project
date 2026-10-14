"""Current cdbc role and fresh strict-reference candidate; source factory only."""
import json
import re
from pyflakes.api import check
import pg2432_current_boot_question_sources as prior
from pg2458_question_current_owned_sources import sources as current_owners
from pg2510_strict_reference_full_six import SOURCE
from pg1446_current_cold_stage import W

CURRENT = 'cdbc07cdf77370d521e64de8b327da7f6752139b'
CURRENT_BOM = '6e069bc89f53b513c719c27fbe71167afbd07b48caa0a31c61bda3e2222f11cf'
BEFORE = 'df3bdffdd093d77302cc11766d44d2efd06f7a7f14c831e76d28b014e14bc4c6'
BOOT = prior.BOOT
TOOLS = 'pg2516-current-strict-candidate-tools-v1'
SAVE = 'pg2520-current-strict-placement-v1'
ARCHIVE = 'pg2518-current-strict-release-v1.tar'
REMOTE = '/home/ubuntu/pg2518-current-strict-input-v1'


def production():
    return SOURCE


def bind(raw):
    # Candidate currently overlaps the new current Source. Protect roles first.
    raw = raw.replace(prior.production(), '__STRICT_CANDIDATE_SOURCE__').replace(
        prior.CURRENT, CURRENT).replace('__STRICT_CANDIDATE_SOURCE__', SOURCE)
    raw = raw.replace('PG2428', '__STRICT_RELEASE__').replace('pg2428', '__STRICT_RELEASE_LOWER__').replace(
        'PG2126', 'PG2428').replace('pg2126', 'pg2428').replace('__STRICT_RELEASE__', 'PG2512').replace(
        '__STRICT_RELEASE_LOWER__', 'pg2512')
    pairs = [(prior.CURRENT_BOM, CURRENT_BOM), (prior.BEFORE, BEFORE),
        ('pg2410-retired-current-before-v1', 'pg2514-current-cdbc-before-v2'),
        ('91f5484b-9702-4c7c-97f3-dd5110a853f9', '06236d14-a6f8-4d05-a6ff-49c713cc2647'),
        ('e1429ac8-f3dd-4e8c-83d2-1926c4ba8440', 'c347b14a-2e59-41e6-993c-a07e537cbd00'),
        ('2026-10-13T15:01:53.237266Z', '2026-10-13T21:16:10.125382Z'),
        ('2026-10-13T19:18:53.785844Z', '2026-10-13T21:44:13.530366Z'),
        ('4011498eef014f25986f4e5ac5c92b1d', '9024d0364d07478d9237b6941d725208'),
        (prior.ARCHIVE, ARCHIVE), (prior.TOOLS, TOOLS), (prior.SAVE, SAVE), (prior.REMOTE, REMOTE),
        ('pg2432', 'pg2516'), ('Pg2432', 'Pg2516'), ('PG2432', 'PG2516'),
        ('pg2434', 'pg2518'), ('PG2434', 'PG2518'), ('pg2436', 'pg2520'), ('PG2436', 'PG2520')]
    for before, after in pairs:
        raw = raw.replace(before, after)
    for before, after in [('20469616839', '29104365495'), ('22107644017', '30827355356'), ('104841', '194154')]:
        raw = re.sub(r'\b' + before + r'\b', after, raw)
    return raw


def sources(bom, before=BEFORE):
    proof = json.loads((W / 'pg2514-current-cdbc-before-v2/manifest.safe.json').read_bytes())
    expected = {'actualExit':0, 'productionSource':CURRENT, 'privateBeforeSha256':BEFORE,
                'runtimeAlreadyRetired':True, 'all24UnchangedTwice':True, 'allTenUnitsKernelEmpty':True,
                'allClientAdvisoryFlock0':True, 'whole187SignedArtifactBytesVerified':True}
    if before != BEFORE or any(type(proof.get(k)) is not type(v) or proof[k] != v for k,v in expected.items()):
        raise ValueError('actual current cdbc original/resource proof required')
    owners = current_owners()
    result = {bind(n):bind(raw) for n,raw in prior.sources(bom).items()}
    for suffix in ['parent_receipt.py', 'warning_parent_projection.py']:
        result['pg2516_' + suffix] = owners['pg2458_' + suffix]
    for name, raw in result.items():
        if name.endswith('.py'):
            context = "BUNDLE_HASH='pending-real-bundle'\n" if name in {'pg2516_native_refs.py', 'pg2516_input_preflight.py'} else ''
            if check(context + raw, '<current cdbc/candidate complete graph>'):
                raise ValueError('all generated namespace exports required')
            compile(raw, '<current strict-candidate graph>', 'exec')
        if '__STRICT_' in raw:
            raise ValueError('unbound overlapping role refused')
    return result


if __name__ == '__main__':
    raise SystemExit('source factory only; no VM operation')
