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
