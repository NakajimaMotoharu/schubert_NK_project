"""Synchronize an existing same-Core preservation boundary with a verified scope end.

Pure metadata only. The caller verifies the evidence bytes before calling this function.
An activity end neither certifies the whole phase nor establishes process/VM ownership.
"""
from copy import deepcopy
import re

_PRODUCT_CATEGORIES = frozenset({
    'IMPLEMENTATION', 'SELECTED_TEST', 'FULL_REGRESSION', 'NATIVE_CONNECTION',
})


def synchronize_boundary(document, config, manifest, event_id, mode):
    """Return a copy; leave absent, foreign-Core, start and administrative boundaries alone."""
    result = deepcopy(document)
    old = result.get('currentManufacturingBoundary')
    if mode != 'end' or config.get('category') not in _PRODUCT_CATEGORIES or not isinstance(old, dict):
        return result
    core = config.get('sourceAfter')
    if not isinstance(core, str) or not re.fullmatch(r'[0-9a-f]{40}', core):
        raise ValueError('explicit end Core required')
    if manifest.get('productionCoreMain') != core or type(manifest.get('actualExit')) is not int or manifest.get('actualExit') != 0:
        raise ValueError('verified successful activity identity required, not whole-quality acceptance')
    if old.get('productionCoreMain') != core:
        return result
    if not isinstance(event_id, str) or not re.fullmatch(r'PGPT-[A-Za-z0-9-]+', event_id):
        raise ValueError('explicit completed event required')
    if old.get('completedEvent') == event_id:
        return result
    path, digest = config.get('manifestPath'), config.get('manifestSha256')
    if not isinstance(path, str) or not path.startswith('evidence/') or '..' in path.split('/'):
        raise ValueError('public activity evidence path required')
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('verified evidence hash required')
    history = result.setdefault('manufacturingBoundaryHistory', [])
    if not isinstance(history, list):
        raise ValueError('preserve existing boundary history schema')
    history.append(deepcopy(old))
    result['currentManufacturingBoundary'] = dict(
        stage='ACTIVITY_ENDED_SCOPE_ONLY',
        source=core,
        productionCoreMain=core,
        completedEvent=event_id,
        completedAtUTC=config.get('terminalAtUTC'),
        scopeOutcome=config.get('outcome'),
        activityEvidence=dict(path=path, sha256=digest),
        actualUnitSource=manifest.get('actualUnitSource'),
        scopeEvidenceOnly=True,
        whole451Accepted=False,
        formalUpdated=False,
        newAcceptance=0,
        effortRate=None,
        ownProcessAndVmState='NOT_INFERRED_FROM_ACTIVITY_END',
    )
    return result
