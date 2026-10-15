"""Warm completed-current a9 to signed4856 unused graph; pure factory, never an operator.

Historical factories render code only. New current data/boot/Root witness and
candidate roles are separately authenticated before any generated operation.
"""
import ast
from functools import lru_cache
import json
import re
import uuid

from pyflakes.api import check
import pg2658_operation_candidate_sources as old
import pg3150_browser_business_owned_sources as owner
from pg1446_current_cold_stage import W

CURRENT = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
CURRENT_BOM = '37bfe01a075449d36cc8b73408dd81fc6d6efc158910a437cbde21b6a0b7f863'
SOURCE = '4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
BOM = 'dc535a48a8d8d46ae5c33a442143e376c59b882a1e098ea7579e3f070fe92d72'
BEFORE = '0e8758639b44fa0a451c1ee342948af6e0caa978dcdf5dc2fc788f36d1039d84'
BOOT = '79a3260a-e16d-42bf-942a-b914ed144c28'
TOOLS = 'pg3434-current-outbox-unused-tools-v1'
SAVE = 'pg3438-current-outbox-unused-placement-v1'
ARCHIVE = 'pg3438-current-outbox-release-v1.tar'
REMOTE = '/home/ubuntu/pg3438-current-outbox-input-v1'


def production():
    return SOURCE


def binding(raw):
    tree = ast.parse(raw)
    return ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
                                 and any(isinstance(t, ast.Name) and t.id == 'BINDING' for t in n.targets)))


def qualify():
    proof = json.loads((W / 'pg3430-current-a9-readonly-before-v1/manifest.safe.json').read_bytes())
    view = json.loads((W / 'pg3432-current-a9-before-view-v2/manifest.safe.json').read_bytes())
    signed = json.loads((W / 'pg3420-candidate-build-v1.safe.json').read_bytes())
    if (proof['actualExit'] != 0 or proof['productionSource'] != CURRENT
            or any(proof.get(k) is not True for k in ['all24UnchangedTwice', 'allTenUnitsKernelEmpty',
                       'allActorGone', 'allClientAdvisoryFlock0', 'whole187SignedArtifactBytesVerified', 'exactRuntimeEntryRetired'])
            or view['actualExit'] != 0 or view['productionSource'] != CURRENT
            or view['privateBeforeSha256'] != BEFORE or view['dataOnlyNotRuntimeAuthority'] is not True
            or view['nativeCandidateCredit'] is not False or view['canonicalBeforeFields'] != 10
            or signed['actualExit'] != 0 or signed['candidateSource'] != SOURCE
            or signed['manifestSha256'] != BOM or not signed['signatureVerified'] or not signed['candidateNotDeployed']):
        raise ValueError('separate genuine current data and signed candidate roles required')


@lru_cache(maxsize=1)
def _binding_context():
    # Cache immutable completed-Root template data only, never live authority.
    # Every sources()/operation still performs its own fresh qualification.
    values = old.sources(BOM)
    latest = owner.sources(); current_binding = binding(latest['pg3150_parent_receipt.py'])
    previous_binding = binding(values['pg2658_parent_receipt.py'])
    _, _, summary, ended = owner.context()
    live = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())
    if (live['actualExit'] != 0 or live['productionSource'] != CURRENT or live['binding'] != current_binding
            or current_binding['boot'] != BOOT.replace('-', '')
            or re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z', ended) is None):
        raise ValueError('actual same-boot completed Root tuple required, never reused as new authority')
    pairs = [(old.SOURCE, SOURCE), (old.CURRENT, CURRENT), (old.CURRENT_BOM, CURRENT_BOM),
             (old.BEFORE, BEFORE), (old.BOOT, BOOT), (old.BOOT.replace('-', ''), BOOT.replace('-', '')),
             ('PG2654', 'PG3420'), ('pg2654', 'pg3420'), ('PG2512', 'PG2802'), ('pg2512', 'pg2802'),
             ('pg2656-current-a79-before-v1', 'pg3432-current-a9-before-view-v2'),
             (old.TOOLS, TOOLS), (old.SAVE, SAVE), (old.ARCHIVE, ARCHIVE), (old.REMOTE, REMOTE),
             ('pg2658', 'pg3434'), ('Pg2658', 'Pg3434'), ('PG2658', 'PG3434'),
             ('pg2659', 'pg3436'), ('PG2659', 'PG3436'),
             ('pg2660', 'pg3438'), ('PG2660', 'PG3438'), ('pg2662', 'pg3438'), ('PG2662', 'PG3438'),
             ('2026-10-14T01:04:03.525607Z', ended)]
    for key in ['activation', 'run', 'cutoff', 'invocation']:
        pairs.append((str(previous_binding[key]), str(current_binding[key])))
    def bind(raw):
        for a, b in pairs:
            raw = raw.replace(a, b)
        for a, b in [(str(previous_binding['job']), str(current_binding['job'])),
                     ('41101204300', str(current_binding['start'])),
                     ('42816406603', str(summary['endMonotonicUs'])), ('287080', str(live['rootPid']))]:
            raw = re.sub(r'\b' + a + r'\b', b, raw)
        return raw
    return bind, latest, current_binding, values


def bind(raw):
    return _binding_context()[0](raw)


def sources(bom=BOM, before=BEFORE):
    qualify()
    if bom != BOM or before != BEFORE:
        raise ValueError('one actual signed candidate and authenticated current data view')
    binder, latest, current_binding, values = _binding_context()
    result = {binder(name): binder(raw) for name, raw in values.items()}
    # Latest current Root proof is historical data only; the new actor is acquired
    # independently by M/A/backend/peer checks in the operation protocol.
    result['pg3434_parent_receipt.py'] = latest['pg3150_parent_receipt.py']
    result['pg3434_warning_parent_projection.py'] = latest['pg3150_warning_parent_projection.py']
    forbidden = [old.CURRENT, old.SOURCE, old.CURRENT_BOM, old.BEFORE, old.BOOT,
                 'pg2656-current-a79-before-v1', '2026-10-14T01:04:03.525607Z']
    for name, raw in result.items():
        if any(value in raw for value in forbidden):
            raise ValueError('unbound historical role in ' + name)
        if name.endswith('.py'):
            prelude = "BUNDLE_HASH='pending-real-bundle'\n" if name in ['pg3434_native_refs.py', 'pg3434_input_preflight.py'] else ''
            if check(prelude + raw, '<new current/candidate ' + name + '>'):
                raise ValueError('complete generated namespace')
            compile(raw, '<current a9 to unused4856 role graph>', 'exec')
    if binding(result['pg3434_parent_receipt.py']) != current_binding or uuid.UUID(current_binding['run']).int == 0:
        raise ValueError('exact authenticated current Root data witness')
    return result


if __name__ == '__main__':
    raise SystemExit('factory only; no VM operation')
