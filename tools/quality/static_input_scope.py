"""Compare an analyzer plan to pinned scope and inventory metadata (BUG-3412)."""

import argparse
import hashlib
import json
import re
from pathlib import Path


class ScopeError(ValueError):
    """A plan or receipt is missing, invalid, or outside the recorded scope."""


def unique_object(pairs):
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ScopeError("DUPLICATE_FIELD")
    return fields


def read_metadata(path, expected_sha256=None):
    contents = path.read_bytes()
    if expected_sha256 is not None and hashlib.sha256(contents).hexdigest() != expected_sha256:
        raise ScopeError("RECEIPT_DIGEST_MISMATCH")
    document = json.loads(contents, object_pairs_hook=unique_object)
    if not isinstance(document, dict):
        raise ScopeError("INVALID_RECEIPT")
    return document


def unique_strings(document, key, *, require_any=False):
    values = document.get(key)
    if not isinstance(values, list) or (require_any and not values):
        raise ScopeError("MISSING_OR_EMPTY_" + key.upper())
    if any(not isinstance(value, str) or not value or value != value.strip() for value in values):
        raise ScopeError("INVALID_" + key.upper())
    if len(set(values)) != len(values):
        raise ScopeError("DUPLICATE_" + key.upper())
    return set(values)


def compare_scope(plan, scope, inventory):
    """Check both input roles without reading artifacts or starting an analyzer."""
    source = plan.get("source")
    if not isinstance(source, str) or not re.fullmatch(r"[0-9a-f]{40}", source):
        raise ScopeError("INVALID_SOURCE")
    if scope.get("source") != source or inventory.get("source") != source:
        raise ScopeError("SOURCE_MISMATCH")
    targets = unique_strings(plan, "targets", require_any=True)
    auxiliaries = unique_strings(plan, "auxiliaries")
    if targets & auxiliaries:
        raise ScopeError("INPUT_ROLE_OVERLAP")
    admitted = unique_strings(scope, "admitted", require_any=True)
    held = unique_strings(scope, "held")
    if admitted & held:
        raise ScopeError("CONTRADICTORY_SCOPE")
    artifacts = inventory.get("membersByArtifactSha256")
    if not isinstance(artifacts, dict):
        raise ScopeError("MISSING_INVENTORY")

    seen = set()
    for digest in sorted(targets | auxiliaries):
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ScopeError("INVALID_ARTIFACT_DIGEST")
        if digest not in artifacts:
            raise ScopeError("UNCATALOGUED_INPUT")
        members = unique_strings(artifacts, digest, require_any=True)
        if members & held:
            raise ScopeError("HELD_MEMBER")
        if members - admitted:
            raise ScopeError("UNASSESSED_MEMBER")
        if members & seen:
            raise ScopeError("AMBIGUOUS_MEMBER")
        seen.update(members)
    return {"targets": len(targets), "auxiliaries": len(auxiliaries), "members": len(seen)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--scope-sha256", required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--inventory-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        outcome = compare_scope(
            read_metadata(args.plan),
            read_metadata(args.scope, args.scope_sha256),
            read_metadata(args.inventory, args.inventory_sha256),
        )
    except ScopeError as exc:
        print(json.dumps({"scopeMatch": False, "reason": str(exc)}))
        return 1
    except (OSError, UnicodeError, json.JSONDecodeError):
        print(json.dumps({"scopeMatch": False, "reason": "UNREADABLE_METADATA"}))
        return 1
    print(json.dumps({"scopeMatch": True, **outcome}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
