"""BUG3190/YKT2658: immutable legacy rows and explicit, unqualified later registrations.

Pure metadata validation. No artifact contents, classfiles, processes or acceptance
decisions are read or created here. An observed filename is not execution permission.
"""
import hashlib
import json
import re
from pathlib import PurePosixPath


def value_digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def _rows(values):
    require(type(values) is list, 'registry array required')
    result = {}
    for row in values:
        name = row['path']
        p = PurePosixPath(name)
        require(type(name) is str and not p.is_absolute() and '..' not in p.parts
                and '\\' not in name and str(p) == name
                and name.startswith(('src/', 'program/characterization/src/main/java/'))
                and '/src/test/' not in name, 'registered public artifact name required')
        require(name not in result, 'duplicate registry path')
        result[name] = row
    return result


def verify(legacy, current, binding, tasks, git_names, separation_proofs):
    """Prove registry preservation without treating later hashes as legacy/runtime proof."""
    require(binding['schema'] == 'WBS_PREPARATION_REGISTRY_SEPARATION_V1', 'binding schema')
    require(binding['runtimeQualified'] is False and binding['wholeAcceptance'] is False
            and binding['sourceBytesRecomputed'] is False
            and type(binding['newAcceptance']) is int and binding['newAcceptance'] == 0
            and binding['effortRate'] is None, 'registry cannot transfer runtime/acceptance')
    require(value_digest(legacy) == binding['legacySemanticSha256'], 'frozen legacy changed')
    require(value_digest(current) == binding['registrySemanticSha256'], 'unrecorded registry change')
    old, now = _rows(legacy), _rows(current)
    require(set(old) <= set(now), 'legacy registration removed')
    additions = sorted(set(now) - set(old))
    require(binding['registeredAdditions'] == additions, 'explicit exact additions required')
    task_map = {t['id']: t for t in tasks}
    require(len(task_map) == len(tasks), 'duplicate canonical task')
    changes = {}
    separate = set()
    for name, row in now.items():
        require(row['owner'] in task_map and row['costOwner'] in task_map
                and task_map[row['costOwner']]['executionRole'] != 'REFERENCE_ONLY',
                'registered logical owner and one actual cost owner required')
        require(row['acceptance'] in ('UNASSESSED', 'NOT_RUN', 'NOT_RUN_HOLD'),
                'preparatory row must not import acceptance')
        require(type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                'explicit unqualified registry hash required')
        if name in old:
            before = old[name]
            require(all(row[k] == before[k] for k in ('owner', 'costOwner', 'kind')),
                    'legacy owner/cost/kind changed')
            delta = {k: {'legacy': v, 'registered': row.get(k)} for k, v in before.items()
                     if k not in row or row[k] != v}
            require(set(delta) <= {'sha256', 'basis'}, 'legacy semantic field changed')
            if delta:
                changes[name] = delta
        elif row['owner'] != row['costOwner']:
            separate.add(name)
            require(name in separation_proofs, 'separate cost owner lacks pinned existing proof')
            proof = separation_proofs[name]
            require(proof['actualExit'] == 0 and type(proof['actualExit']) is int
                    and proof['owner'] == row['owner'] and proof['costOwner'] == row['costOwner']
                    and proof['formalUpdated'] is False and type(proof['newAcceptance']) is int
                    and proof['newAcceptance'] == 0 and type(proof['productTestsExecuted']) is int
                    and proof['productTestsExecuted'] == 0,
                    'separate cost ownership is not a runtime/acceptance waiver')
    require(set(separation_proofs) == separate, 'unused or missing cost-separation proof')
    require(changes == binding['legacyFieldUpdates'], 'exact recorded legacy/current differences required')
    missing = sorted(set(now) - set(git_names))
    require(missing == binding['retainedRetiredHistoricalPaths'], 'unrecorded absent filename')
    require(set(missing) <= set(old) and all(n in git_names for n in additions),
            'new artifact absent from observed Git filenames')
    return dict(legacyRows=len(old), preparationRows=len(now), registeredAdditions=len(additions),
                currentHashOrBasisUpdates=len(changes), logicalCostSeparations=len(separate),
                immutableLegacyPreserved=True, sourceBytesRecomputed=False,
                runtimeQualified=False, wholeAcceptance=False, formalUpdated=False,
                newAcceptance=0, effortRate=None)
