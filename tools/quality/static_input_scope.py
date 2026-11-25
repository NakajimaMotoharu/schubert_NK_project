"""Compare a quality tool's inputs to pinned scope and inventory metadata."""

import argparse
import csv
import hashlib
import io
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


def invalid_constant(_):
    raise ScopeError("INVALID_JSON_CONSTANT")


def read_metadata(path, expected_sha256=None):
    contents = path.read_bytes()
    if expected_sha256 is not None and hashlib.sha256(contents).hexdigest() != expected_sha256:
        raise ScopeError("RECEIPT_DIGEST_MISMATCH")
    document = json.loads(
        contents, object_pairs_hook=unique_object, parse_constant=invalid_constant
    )
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


def check_source(plan, scope, inventory):
    source = plan.get("source")
    if not isinstance(source, str) or not re.fullmatch(r"[0-9a-f]{40}", source):
        raise ScopeError("INVALID_SOURCE")
    if scope.get("source") != source or inventory.get("source") != source:
        raise ScopeError("SOURCE_MISMATCH")


def compare_scope(plan, scope, inventory):
    """Check both input roles without reading artifacts or starting an analyzer."""
    check_source(plan, scope, inventory)
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


def compare_source_scope(plan, scope, inventory):
    """Match a source-only plan to explicit, tool-specific scope and Git blobs."""
    if set(plan) != {"source", "tool", "toolSha256", "filesByPath"}:
        raise ScopeError("INVALID_SOURCE_PLAN_FIELDS")
    check_source(plan, scope, inventory)
    tool = plan.get("tool")
    tool_sha256 = plan.get("toolSha256")
    if not isinstance(tool, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", tool):
        raise ScopeError("INVALID_TOOL")
    if not isinstance(tool_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", tool_sha256):
        raise ScopeError("INVALID_TOOL_DIGEST")
    if scope.get("tool") != tool or scope.get("toolSha256") != tool_sha256:
        raise ScopeError("TOOL_MISMATCH")
    admitted = unique_strings(scope, "admitted", require_any=True)
    held = unique_strings(scope, "held")
    if admitted & held:
        raise ScopeError("CONTRADICTORY_SCOPE")
    proposed = plan.get("filesByPath")
    if not isinstance(proposed, dict) or not proposed:
        raise ScopeError("MISSING_OR_EMPTY_FILE_PLAN")
    files = inventory.get("filesByPath")
    if not isinstance(files, dict):
        raise ScopeError("MISSING_INVENTORY")
    for path, blob in proposed.items():
        segments = path.split("/") if isinstance(path, str) else []
        if not segments or any(not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.$-]*", s)
                               for s in segments):
            raise ScopeError("INVALID_SOURCE_PATH")
        if path in held:
            raise ScopeError("HELD_SOURCE_PATH")
        if path not in admitted:
            raise ScopeError("UNASSESSED_SOURCE_PATH")
        if not isinstance(blob, str) or not re.fullmatch(r"[0-9a-f]{40}", blob):
            raise ScopeError("INVALID_SOURCE_BLOB")
        if path not in files:
            raise ScopeError("UNCATALOGUED_SOURCE_PATH")
        if files[path] != blob:
            raise ScopeError("SOURCE_BLOB_MISMATCH")
    return {"tool": tool, "files": len(proposed)}


def read_source_roster(path, expected_sha256):
    contents = path.read_bytes()
    if hashlib.sha256(contents).hexdigest() != expected_sha256:
        raise ScopeError("ROSTER_DIGEST_MISMATCH")
    reader = csv.DictReader(io.StringIO(contents.decode("utf-8")), delimiter="\t", strict=True)
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not {"path", "sha256"} <= set(fields):
        raise ScopeError("INVALID_SOURCE_ROSTER")
    sources = {}
    for row in reader:
        name, digest = row["path"], row["sha256"]
        if (None in row or not name or name != name.strip() or name in sources
                or not digest or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ScopeError("INVALID_SOURCE_ROSTER")
        sources[name] = digest
    if not sources:
        raise ScopeError("INVALID_SOURCE_ROSTER")
    return sources


def source_reuse_delta(plan, inventory, roster):
    """Classify already validated targets against a roster for the same tool configuration."""
    hashes = inventory.get("sha256ByPath")
    if not isinstance(hashes, dict):
        raise ScopeError("MISSING_SOURCE_DIGEST_INVENTORY")
    unchanged, unmeasured = [], []
    for path in sorted(plan["filesByPath"]):
        digest = hashes.get(path)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ScopeError("INVALID_SOURCE_DIGEST")
        (unchanged if roster.get(path) == digest else unmeasured).append(path)
    if not unmeasured:
        raise ScopeError("NO_UNMEASURED_SOURCE")
    return {"unchangedInRoster": unchanged, "unmeasuredInRoster": unmeasured}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--scope", type=Path, required=True)
    parser.add_argument("--scope-sha256", required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--inventory-sha256", required=True)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--prior-source-roster", type=Path,
                        help="check target sources against an existing same-configuration roster")
    parser.add_argument("--prior-source-roster-sha256")
    args = parser.parse_args(argv)
    try:
        if (bool(args.prior_source_roster) != bool(args.prior_source_roster_sha256)
                or (args.prior_source_roster and not args.source_only)):
            raise ScopeError("SOURCE_ROSTER_ARGUMENTS")
        compare = compare_source_scope if args.source_only else compare_scope
        plan = read_metadata(args.plan)
        scope = read_metadata(args.scope, args.scope_sha256)
        inventory = read_metadata(args.inventory, args.inventory_sha256)
        outcome = compare(plan, scope, inventory)
        if args.prior_source_roster:
            roster = read_source_roster(args.prior_source_roster, args.prior_source_roster_sha256)
            outcome.update(source_reuse_delta(plan, inventory, roster))
    except ScopeError as exc:
        print(json.dumps({"scopeMatch": False, "reason": str(exc)}))
        return 1
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error):
        print(json.dumps({"scopeMatch": False, "reason": "UNREADABLE_METADATA"}))
        return 1
    print(json.dumps({"scopeMatch": True, **outcome}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
