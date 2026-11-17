"""Resolve a pinned current static view. A structure PASS never qualifies any runtime evidence."""
from pathlib import Path, PurePosixPath
import copy
import hashlib
import json
import re
import subprocess

VIEW_KEY = 'currentSourceArtifactStructureView20261108'
PROJECTION_KEY = 'currentSourceArtifactOwnershipProjection20261108'
PUBLIC_PREFIX = 'evidence/01_PT/018_NK-OPS-001/evidence/'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def value_digest(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def safe_relative(value):
    require(type(value) is str and value and '\\' not in value and '\0' not in value, 'invalid artifact path')
    path = PurePosixPath(value)
    require(not path.is_absolute() and '..' not in path.parts and str(path) == value, 'noncanonical artifact path')
    return value


def pinned_public_json(root, reference):
    name = safe_relative(reference['path'])
    require(name.startswith(PUBLIC_PREFIX) and name.endswith('.json'), 'nonpublic descriptor reference')
    path = root / name
    require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), 'descriptor reference escaped')
    require(type(reference['sha256']) is str and re.fullmatch('[0-9a-f]{64}', reference['sha256']), 'invalid descriptor digest')
    require(digest(path) == reference['sha256'], 'descriptor digest mismatch')
    return read_json(path)


def eligible_names(names):
    # Inventory names only. Test files are excluded before any object identity/content operation.
    return {safe_relative(p) for p in names
            if ('/src/main/java/' in p and p.endswith('.java'))
            or '/src/main/resources/' in p or p.startswith('src/deployment/')}


def resolve_descriptors(view, base, legacy, tasks, git_names):
    source = view['source']
    require(type(source) is str and re.fullmatch('[0-9a-f]{40}', source), 'invalid current source')
    require(view['version'] == 1 and type(view['version']) is int, 'unsupported static view version')
    require(view['runtimeQualified'] is False and view['wholeAcceptance'] is False, 'runtime transfer forbidden')
    require(view['oldRuntimeQualificationTransferred'] is False, 'old runtime qualification transfer')
    require(type(base) is list and len(base) == view['artifactCount'], 'static descriptor count mismatch')
    by_task = {v['id']: v for v in tasks}
    require(len(by_task) == len(tasks), 'duplicate task ID')
    old = {v['path']: v for v in legacy}
    require(len(old) == len(legacy), 'duplicate legacy path')
    actual, names = [], set()
    overrides = view['ownerKindOverrides']
    require(type(overrides) is dict, 'invalid ownership overrides')
    for row in base:
        path = safe_relative(row['path'])
        require(path.startswith(('src/', 'program/characterization/src/main/java/')), 'unexpected source domain')
        require(path not in names, 'duplicate current artifact')
        names.add(path)
        require(row['staticSource'] == source, 'mixed current static source')
        require(row['qualification'] == 'UNQUALIFIED_STATIC_DESCRIPTOR_ONLY'
                and row['runtimeQualificationTransferred'] is False and row['acceptance'] == 'UNASSESSED',
                'descriptor runtime acceptance imported')
        require(type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'invalid static digest')
        resolved = copy.deepcopy(row)
        if path in overrides:
            override = overrides[path]
            require(set(override) == {'owner', 'costOwner', 'kind'}, 'identity field override forbidden')
            resolved.update(override)
        owner = resolved['owner']
        require(owner == resolved['costOwner'] and owner in by_task
                and by_task[owner]['executionRole'] != 'REFERENCE_ONLY', 'invalid current owner/cost owner')
        if path in old:
            require((owner, resolved['costOwner'], resolved['kind'])
                    == (old[path]['owner'], old[path]['costOwner'], old[path]['kind']), 'current canonical owner changed')
        actual.append(resolved)
    require(set(overrides) <= names, 'override for absent artifact')
    require(names == eligible_names(git_names), 'current Git filename scope mismatch')
    require(sorted(names - set(old)) == view['addedComparedToLegacy'], 'new artifact set mismatch')
    require(sorted(set(old) - names) == view['retiredHistoricalPaths'], 'retired artifact set mismatch')
    char = sum(v['path'].startswith('program/characterization/') for v in actual)
    require(view['productionArtifacts'] == len(actual) - char and view['characterizationArtifacts'] == char,
            'static source domain counts')
    return actual


def verify(root, master, snapshot, inventory, git_names=None, inventory_path=None):
    root = Path(root)
    require(VIEW_KEY in inventory, 'current source structure view missing')
    view = inventory[VIEW_KEY]
    current_inventory = Path(inventory_path) if inventory_path is not None else root / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
    require(snapshot['inventorySha256'] == digest(current_inventory),
            'current WBS reference mismatch')
    require(snapshot['source'] == inventory['source'], 'legacy snapshot source drift')
    identity = pinned_public_json(root, view['identityProof'])
    lineage = pinned_public_json(root, view['lineageManifest'])
    base = pinned_public_json(root, view['descriptorBase'])
    require(identity['actualExit'] == lineage['actualExit'] == 0, 'static proof incomplete')
    require(identity['productionMainSource'] == lineage['source'] == view['source'], 'static proof source mismatch')
    require(identity['currentLineage'] == view['lineageManifest'], 'independent lineage reference mismatch')
    require(lineage['files']['artifacts.json'] == view['descriptorBase']['sha256'], 'lineage descriptor binding')
    require(identity['artifacts'] == lineage['artifactCount'] == len(base), 'qualified descriptor denominator')
    require(identity['whole451Accepted'] is False and identity['wholeG13Accepted'] is False, 'static proof used as full gate')
    require(inventory['source'] == view['preservedLegacyInventorySource']
            and inventory['currentPhysicalCandidate']['source'] == view['preservedLegacyCandidateSource'],
            'legacy source history modified')
    legacy = inventory['artifacts']
    registry_result = None
    if 'legacyArtifactRows' in view:
        # BUG3190: preserve the exact original table, not a current registry under its hash.
        # The later registry has its own explicit, unqualified metadata proof and guards.
        legacy = pinned_public_json(root, view['legacyArtifactRows'])
        binding = pinned_public_json(root, inventory['currentPreparationRegistryBinding20261117'])
        require(binding['legacyReference'] == view['legacyArtifactRows'], 'registry legacy reference drift')
        require(binding['legacySemanticSha256'] == view['preservedLegacyArtifactRowsDigest'],
                'registry cannot replace the fixed legacy digest')
        require(binding['retainedRetiredHistoricalPaths'] == view['retiredHistoricalPaths'],
                'registry retired history mismatch')
        observed = binding['observedGitHead']
        require(type(observed) is str and re.fullmatch('[0-9a-f]{40}', observed),
                'explicit registry filename observation source')
        current_names = subprocess.run(['git', 'ls-tree', '-r', '--name-only', '-z', observed, '--',
                                        'src', 'program/characterization/src/main/java'], cwd=root,
                                       check=True, capture_output=True, timeout=15)
        separation_proofs = {name: pinned_public_json(root, reference)
                             for name, reference in binding['costSeparationReferences'].items()}
        import wbs_preparation_registry
        registry_result = wbs_preparation_registry.verify(
            legacy, inventory['artifacts'], binding, master['tasks'],
            current_names.stdout.decode().rstrip('\0').split('\0'), separation_proofs)
    require(value_digest(legacy) == view['preservedLegacyArtifactRowsDigest'],
            'legacy artifact history modified')
    require(value_digest(inventory['currentPhysicalCandidate']) == view['preservedLegacyCandidateDigest'],
            'legacy candidate history modified')
    if git_names is None:
        result = subprocess.run(['git', 'ls-tree', '-r', '--name-only', '-z', view['source'], '--',
                                 'src', 'program/characterization/src/main/java'], cwd=root,
                                check=True, capture_output=True, timeout=15)
        git_names = result.stdout.decode().rstrip('\0').split('\0')
    rows = resolve_descriptors(view, base, legacy, master['tasks'], git_names)
    projection = master[PROJECTION_KEY]
    require(projection['source'] == view['source'] and projection['viewKey'] == VIEW_KEY
            and projection['artifactCount'] == len(rows), 'master current projection binding')
    require(projection['runtimeQualified'] is False and projection['newAcceptance'] == 0
            and type(projection['newAcceptance']) is int and projection['effortRate'] is None,
            'master projection must not import runtime acceptance or cost progress')
    require(projection['descriptorBase'] == view['descriptorBase'], 'master projection descriptor binding')
    counts = owner_counts(v['owner'] for v in rows)
    require(projection['ownerArtifactCounts'] == counts, 'master current owner projection mismatch')
    result = dict(status='PASS_CURRENT_STATIC_SOURCE_STRUCTURE_ONLY', source=view['source'], artifactCount=len(rows),
                productionArtifacts=view['productionArtifacts'], characterizationArtifacts=view['characterizationArtifacts'],
                addedComparedToLegacy=len(view['addedComparedToLegacy']), retiredHistoricalPaths=len(view['retiredHistoricalPaths']),
                ownerKindOverrides=len(view['ownerKindOverrides']), identityRecomputed=False,
                descriptorBase=view['descriptorBase'], runtimeQualified=False, wholeWbsAccepted=False,
                formalUpdated=False, newAcceptance=0, effortRate=None)
    if registry_result is not None:
        result.update(laterPreparationRegistry=registry_result,
                      sourceViewPinnedToExactDeclaredSource=True,
                      laterRegistryDoesNotQualifyLatestProductionSource=True)
    return result


def owner_counts(values):
    result = {}
    for value in values:
        result[value] = result.get(value, 0) + 1
    return result


def preparation_projection(view, base, frozen_legacy, current_registry, tasks,
                           git_names, task_id, registered_additions):
    """Project preparatory ownership only; never reuse the baseline byte or runtime claims.

    Frozen legacy rows are independently pinned by the original view digest. Later public
    registrations remain explicit inputs; they cannot silently replace a retired source.
    """
    require(value_digest(frozen_legacy) == view['preservedLegacyArtifactRowsDigest'],
            'frozen legacy preparation digest mismatch')
    rows = resolve_descriptors(view, base, frozen_legacy, tasks, git_names)
    by_task = {row['id']: row for row in tasks}
    require(task_id in by_task and by_task[task_id]['executionRole'] != 'REFERENCE_ONLY',
            'invalid preparation owner')
    historical = {row['path']: row for row in frozen_legacy}
    current = {row['path']: row for row in current_registry}
    require(len(current) == len(current_registry), 'duplicate current registration')
    require(set(historical) <= set(current), 'historical registration removed')
    require(type(registered_additions) is list and len(registered_additions) == len(set(registered_additions))
            and set(current) - set(historical) == set(registered_additions),
            'unlisted post-baseline registration')
    for name, row in historical.items():
        require(all(current[name][key] == row[key] for key in ('owner', 'costOwner', 'kind')),
                'historical ownership changed')
    resolved = {row['path']: row for row in rows}
    for name in registered_additions:
        safe_relative(name)
        row = current[name]
        require(name.startswith('src/') and ('/src/main/java/' in name or '/src/main/resources/' in name)
                and row['owner'] == row['costOwner'] and row['owner'] in by_task
                and by_task[row['owner']]['executionRole'] != 'REFERENCE_ONLY'
                and row['acceptance'] in ('UNASSESSED', 'NOT_RUN'),
                'unqualified public registration owner required')
        if name in resolved:
            require(all(resolved[name][key] == row[key] for key in ('owner', 'costOwner', 'kind')),
                    'registered baseline ownership changed')
        else:
            resolved[name] = row
    owned = sorted(name for name, row in resolved.items() if row['owner'] == task_id)
    require(owned, 'empty preparation source projection')
    return dict(paths=owned, baselineSource=view['source'], runtimeQualified=False,
                wholeAcceptance=False, baselineByteQualificationTransferred=False,
                registeredAdditions=list(registered_additions), newAcceptance=0)


def full_audit_hold(structure, inventory):
    require(structure['status'] == 'PASS_CURRENT_STATIC_SOURCE_STRUCTURE_ONLY'
            and structure['runtimeQualified'] is False and structure['wholeWbsAccepted'] is False,
            'invalid current structure result')
    return dict(status='HOLD', reason='CURRENT_SOURCE_RUNTIME_AND_FINAL_CHECKS_NOT_QUALIFIED',
                currentSourceStructure=structure, preservedLegacyInventorySource=inventory['source'],
                preservedCandidateSource=inventory['currentPhysicalCandidate']['source'],
                unverifiedChecks=['current source runtime/candidate source/run qualification',
                                  'current source final requirement/layout/method-oracle completeness',
                                  'current source full PT/coverage/static/CHR/secrets gates',
                                  'remaining full-audit graph/cost/individual acceptance/history checks'],
                privateRuntimeEvidenceRead=False, originalRuntimeTestsExecuted=False,
                wholeWbsAccepted=False, formalUpdated=False, newAcceptance=0, effortRate=None)
