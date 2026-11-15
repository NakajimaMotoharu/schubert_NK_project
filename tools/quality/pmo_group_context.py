"""Explicit activity context, independent of event identity and all accounting fields.

BUG2418/YKT2163: never inherit another group's labels or oracle description.
This pure validator does no file access and grants no execution/acceptance authority.
Actual evidence hashes must still be independently bound by the activity's verifier.
"""
import copy
import re
from pathlib import PurePosixPath

CATEGORIES = frozenset({"IMPLEMENTATION", "CONTRACT_AUDIT", "SELECTED_TEST",
                        "FULL_REGRESSION", "NATIVE_CONNECTION", "RECOVERY",
                        "REVIEW", "ADMIN"})
KINDS = frozenset({"ORIGINAL_PLAN", "ADDITIONAL_FINDING", "REWORK",
                   "SOURCE_REQUALIFICATION", "TOOL_FIX", "MIXED_UNALLOCATED"})


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def build_context(*, group_id, category, kind, scope, oracle_refs):
    """Require current context; derive detail from group ID rather than a default."""
    _require(isinstance(group_id, str) and
             re.fullmatch(r"PGPT-[A-Z0-9]+(?:-[A-Z0-9]+)*", group_id), "group ID")
    _require(category in CATEGORIES and kind in KINDS, "registered category/kind")
    _require(isinstance(scope, str) and scope.strip() and len(scope) <= 4096,
             "explicit bounded scope")
    _require(isinstance(oracle_refs, list) and oracle_refs, "explicit oracle refs")
    seen = set()
    for ref in oracle_refs:
        _require(isinstance(ref, dict) and set(ref) in
                 ({"path", "sha256"}, {"path", "sha256", "source"}), "ref schema")
        path = ref["path"]
        _require(isinstance(path, str) and path and "\\" not in path, "relative path")
        pure = PurePosixPath(path)
        _require(not pure.is_absolute() and ".." not in pure.parts and
                 str(pure) == path and pure.suffix in {".md", ".json"} and
                 path.startswith(("documents/", "evidence/")) and
                 not any(word in path.lower() for word in
                         ("private", "rootfailedstart", "snapshotkeyclosewitness",
                          "pg9892_snapshot_key_close_witness")), "public reference")
        _require(isinstance(ref["sha256"], str) and
                 re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]), "sha256")
        source = ref.get("source")
        _require("source" not in ref or isinstance(source, str) and
                 re.fullmatch(r"[0-9a-f]{40}", source), "source identity")
        identity = (path, source)
        _require(identity not in seen, "duplicate ref identity")
        seen.add(identity)
    return dict(contextSchema="PGPT_EXPLICIT_GROUP_CONTEXT_V1", contextGroupId=group_id,
                workCategory=category, workDetailCategory=group_id,
                workAttributionKind=kind, workScope=scope,
                oracleReferences=copy.deepcopy(oracle_refs))


def validate_context(group_id, fields):
    """Reject a reused context before a caller passes it to the event writer."""
    expected = build_context(group_id=group_id, category=fields["workCategory"],
                             kind=fields["workAttributionKind"], scope=fields["workScope"],
                             oracle_refs=fields["oracleReferences"])
    _require(all(fields.get(key) == value for key, value in expected.items()),
             "group/context mismatch")


def collect_canonical_nodes(plans):
    """Read only 481/484 structural arrays, never historical estimates with reused IDs."""
    nodes = {}
    for plan in plans:
        _require(isinstance(plan, dict), 'canonical plan object')
        arrays = [plan[key] for key in ('tasks', 'children', 'sharedBudgets') if key in plan]
        _require(arrays and all(isinstance(array, list) for array in arrays),
                 'canonical structural arrays')
        for array in arrays:
            for node in array:
                _require(isinstance(node, dict), 'canonical structural node')
                node_id = node.get('id')
                _require(isinstance(node_id, str) and node_id.startswith('WBS-') and
                         ':' not in node_id, 'canonical structural WBS identity')
                _require(node_id not in nodes, 'duplicate canonical structural identity')
                children = node.get('children', [])
                _require(isinstance(children, list) and
                         all(isinstance(child, str) for child in children),
                         'canonical structural child IDs')
                nodes[node_id] = node
    return nodes


def validate_implementation_artifacts(config, artifact_rows, canonical_nodes=None):
    """BUG2745: bind production implementation labels before an event is appended.

    Pure metadata only. Existing historical events/configurations are never rewritten.
    Selected quality runs retain their explicit F03 cost boundary; TOOL_FIX changes
    do not claim to implement a production artifact.
    """
    if config.get('category') != 'IMPLEMENTATION' or config.get('kind') == 'TOOL_FIX':
        return
    paths = config.get('implementationArtifactPaths')
    _require(isinstance(paths, list) and paths and len(paths) == len(set(paths)),
             'explicit implementation artifact paths')
    rows = {r['path']: r for r in artifact_rows}
    owners = set()
    for name in paths:
        _require(isinstance(name, str) and name.startswith('src/') and
                 '..' not in PurePosixPath(name).parts and name in rows,
                 'registered production artifact')
        owner = rows[name].get('costOwner', rows[name].get('owner'))
        _require(isinstance(owner, str) and owner.startswith('WBS-'),
                 'registered production cost owner')
        owners.add(owner)
    bindings = config.get('implementationOwnerLeafBindings')
    if bindings is not None:
        # BUG2758: 485 ownership can be a subdivided parent; 487 costs require leaves.
        _require(isinstance(canonical_nodes, dict) and canonical_nodes,
                 'authoritative canonical nodes required')
        _require(isinstance(bindings, dict) and set(bindings) == owners,
                 'exact implementation owner bindings')
        selected = []
        for owner, leaves in bindings.items():
            _require(isinstance(leaves, list) and leaves and
                     all(isinstance(leaf, str) for leaf in leaves) and
                     len(leaves) == len(set(leaves)), 'explicit unique owner leaves')
            reachable, pending = set(), [owner]
            while pending:
                node_id = pending.pop()
                _require(isinstance(node_id, str) and node_id in canonical_nodes,
                         'registered owner descendant')
                if node_id in reachable:
                    continue
                reachable.add(node_id)
                children = canonical_nodes[node_id].get('children', [])
                _require(isinstance(children, list), 'canonical children list')
                pending.extend(children)
            for leaf in leaves:
                _require(isinstance(leaf, str) and ':' not in leaf and
                         leaf in reachable and not canonical_nodes[leaf].get('children'),
                         'actual owner descendant leaf only')
            selected.extend(leaves)
        _require(len(selected) == len(set(selected)) and
                 isinstance(config.get('wbsLeafIds'), list) and
                 len(config['wbsLeafIds']) == len(selected) and
                 set(config['wbsLeafIds']) == set(selected),
                 'exact canonical implementation leaf set')
        return
    _require(isinstance(config.get('wbsLeafIds'), list) and
             len(config['wbsLeafIds']) == len(owners) and
             set(config['wbsLeafIds']) == owners, 'implementation WBS artifact mismatch')
