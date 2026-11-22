#!/usr/bin/env python3
"""BUG-100/YKT-089: fail-fast collection and same-run/source verification of every active scope."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from pgpt_evidence_destination import CANDIDATE_ROOT_ENV, check_candidate_root

BASE = (
    ("006_collect_scenario_evidence.py", "008_NK-SCN-001"),
    ("003_collect_auth_evidence.py", "007_NK-AUT-001"),
    ("007_collect_large_result_regression.py", "003_NK-PRO-003"),
    ("008_collect_inbox_regression.py", "006_NK-MSG-002"),
    ("009_collect_media_evidence.py", "009_NK-MED-001"),
    ("010_collect_admin_evidence.py", "010_NK-ADM-001"),
    ("015_collect_web_evidence.py", "015_NK-WEB-001"),
    ("020_collect_batch_evidence.py", "017_NK-BAT-001"),
    ("027_collect_question_receipt_evidence.py", "011_NK-QST-001"),
    ("028_collect_stub_evidence.py", "012_NK-ASY-001"),
    ("029_collect_scenario_screen_evidence.py", "016_NK-WEB-002"),
)
NESTED = (
    ("", "inbox-inspection"), ("--authentication", "authentication-inspection"),
    ("--sql", "inspection-sql"), ("--deletion-sql", "deletion-sql"),
    ("--cleanup", "authentication-cleanup"), ("--non-authentication", "non-authentication-inspection"),
    ("--full-sql", "full-inbox-sql"), ("--full-cleanup", "full-inbox-cleanup"),
    ("--outbox-only", "outbox-only-cleanup"), ("--progress-sql", "inbox-progress-sql"),
    ("--progress-service", "inbox-progress-service"), ("--cleanup-safety", "cleanup-safety"),
    ("--run-executor", "inbox-run-executor"), ("--aes-credential", "inbox-aes-credential"),
    ("--credential-access", "credential-access"), ("--inode-security", "inode-security"),
    ("--credential-loader", "credential-loader"),
    ("--inspector-process", "inspector-process"),
    ("--log-progress", "log-cleanup-progress"),
    ("--question-query", "question-query"),
    ("--result-binding", "result-binding"),
    ("--question-mutation", "question-mutation"),
)
SCOPES = tuple(p + "/evidence" for _, p in BASE) + tuple(
    "004_NK-DAT-001/evidence/" + p for _, p in NESTED) + (
        "004_NK-DAT-001/evidence/inspector-database",
        "004_NK-DAT-001/evidence/inspector-application",
        "004_NK-DAT-001/evidence/inspector-launch", "018_NK-OPS-001/evidence",
        "004_NK-DAT-001/evidence/backup-rerun", "004_NK-DAT-001/evidence/run-references",
        "004_NK-DAT-001/evidence/parent-summary", "004_NK-DAT-001/evidence/atomic-cleanup",
        "004_NK-DAT-001/evidence/expiry-audit",)
SCOPES += ("005_NK-MSG-001/evidence/sync-consumers",
           "005_NK-MSG-001/evidence/web-reply-consumer",
           "006_NK-MSG-002/003_WebLogReplayWorker/evidence",
           "005_NK-MSG-001/evidence/api-web-log-consumer",
           "005_NK-MSG-001/evidence/api-messaging-parent",
           "005_NK-MSG-001/evidence/log-path-router",
           "005_NK-MSG-001/evidence/api-log-path-runtime",
           "005_NK-MSG-001/evidence/request-sender-resource",
           "005_NK-MSG-001/evidence/jms-resource-compounds",
           "006_NK-MSG-002/004_JmsResourceCompounds/evidence",
           "006_NK-MSG-002/005_LogReplayVertical/evidence")
ROOT_MANIFEST = "008_NK-SCN-001/evidence/manifest.json"
SCOPE_METADATA = {"manifest.json", "checksums.sha256"}
PROVISIONAL_RUN_DIRECTORY = re.compile(r"PG[1-9][0-9]*-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(root, relative):
    path = root / relative
    if (not relative or Path(relative).is_absolute()
            or ".." in Path(relative).parts or not path.is_file()
            or not path.resolve().is_relative_to(root.resolve())):
        raise ValueError("invalid local evidence path")
    return path


def load_success_manifest(path):
    def unique_object(pairs):
        values = dict(pairs)
        if len(values) != len(pairs):
            raise ValueError("duplicate evidence manifest field")
        return values

    def invalid_constant(_):
        raise ValueError("invalid evidence manifest numeric constant")

    manifest = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=invalid_constant,
    )
    if (not isinstance(manifest, dict)
            or type(manifest.get("exitCode")) is not int
            or manifest["exitCode"] != 0):
        raise ValueError("mixed or failed evidence run/source/branch")
    return manifest


def scope_payloads(directory):
    """List owned payloads, keeping reserved sibling namespaces out of the formal scope."""
    pending = list(directory.iterdir())
    actual = set()
    while pending:
        path = pending.pop()
        relative = path.relative_to(directory)
        if path.is_symlink():
            raise ValueError("symbolic link in the formal evidence scope")
        if path.is_dir():
            if len(relative.parts) == 1 and (
                path.name == "provisional" or PROVISIONAL_RUN_DIRECTORY.fullmatch(path.name)
            ):
                continue
            pending.extend(path.iterdir())
        elif path.is_file():
            if path.name not in SCOPE_METADATA:
                actual.add(str(relative))
        else:
            raise ValueError("non-regular formal evidence entry")
    return actual


def validate_scope(root, scope, run, commit, branch):
    directory = root / scope
    if directory.resolve() != root.resolve() / scope:
        raise ValueError("invalid formal evidence scope directory")
    actual = scope_payloads(directory)
    manifest_path = directory / "manifest.json"
    manifest = load_success_manifest(manifest_path)
    if (manifest["runId"], manifest["targetCommit"], manifest["branch"]) != (run, commit, branch):
        raise ValueError("mixed or failed evidence run/source/branch")
    entries = manifest["files"]
    paths = [entry["path"] for entry in entries]
    if len(paths) != len(set(paths)) or set(paths) != actual:
        raise ValueError("incomplete or duplicate evidence file inventory")
    for entry in entries:
        if digest(local_file(directory, entry["path"])) != entry["sha256"]:
            raise ValueError("evidence file hash mismatch")
    checksums = {}
    for line in (directory / "checksums.sha256").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None or match[2] in checksums:
            raise ValueError("invalid checksum inventory")
        checksums[match[2]] = match[1]
    if set(checksums) != actual | {"manifest.json"}:
        raise ValueError("incomplete checksum inventory")
    for path, expected in checksums.items():
        if digest(local_file(directory, path)) != expected:
            raise ValueError("checksum mismatch")
    if scope.startswith(("004_NK-DAT-001/", "005_NK-MSG-001/", "006_NK-MSG-002/003_", "006_NK-MSG-002/004_", "006_NK-MSG-002/005_", "011_NK-QST-001/", "012_NK-ASY-001/", "016_NK-WEB-002/", "017_NK-BAT-001/", "018_NK-OPS-001/")):
        linked = directory / manifest["fullReactorManifest"]
        if (linked.resolve() != (root / ROOT_MANIFEST).resolve()
                or digest(linked) != manifest["fullReactorManifestSha256"]):
            raise ValueError("invalid full reactor reference")
    return {"scope": scope, "manifestSha256": digest(manifest_path)}


def validate_all(root, run, commit, branch):
    # Fixed mandatory inventory: globbing only extant manifests would silently accept missing scopes.
    return [validate_scope(root, scope, run, commit, branch) for scope in SCOPES]


def collect(repo, run, execute=subprocess.run, *, candidate_root=None):
    commands = [[sys.executable, "-B", str(repo / "tools/quality" / tool), run]
                for tool, _ in BASE]
    commands.extend([sys.executable, "-B",
                     str(repo / "tools/quality/016_collect_inbox_inspection_evidence.py"), run]
                    + ([flag] if flag else []) for flag, _ in NESTED)
    commands.append([sys.executable, "-B", str(repo / "tools/quality/021_collect_inspector_database_evidence.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/021_collect_inspector_database_evidence.py"), run, "--application"])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/022_collect_inspector_launch_evidence.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/022_collect_inspector_launch_evidence.py"), run, "--deployment"])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/023_collect_backup_rerun_evidence.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/024_collect_run_reference_evidence.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/025_collect_parent_summary_evidence.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/026_collect_atomic_cleanup_evidence.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/037_collect_expiry_audit_database.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/030_collect_sync_consumers.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/031_collect_web_reply_consumers.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/032_collect_web_log_worker.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/033_collect_api_web_log_consumers.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/034_collect_api_messaging_runtime.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/035_collect_log_path_router.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/036_collect_api_log_path_runtime.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/038_collect_request_sender_resource.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/039_collect_jms_resource_compounds.py"), run])
    commands.append([sys.executable, "-B", str(repo / "tools/quality/040_collect_log_replay_vertical.py"), run])
    # Batch has a fixed certified inventory. Reject incompatible input before any writer runs.
    preflight = [sys.executable, "-B", str(repo / "tools/quality/020_collect_batch_evidence.py"),
                 run, "--preflight"]
    options = {"cwd": repo, "check": True}
    if candidate_root is not None:
        options["env"] = dict(os.environ, **{CANDIDATE_ROOT_ENV: str(candidate_root)})
    execute(preflight, **options)
    for command in commands:
        execute(command, **options)


def reserve_candidate(repo, run, requested=None):
    if requested is None:
        area = check_candidate_root(repo, repo.parent / "pgpt-formal-candidates")
        area.mkdir(mode=0o700, exist_ok=True)
        requested = area / run
    candidate = check_candidate_root(repo, requested)
    candidate.mkdir(mode=0o700)
    return candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--candidate-root", type=Path, help="collect or validate evidence outside the checkout")
    args = parser.parse_args()
    if not re.fullmatch(r"PT-(WEB|ADM|MED|SCN)-[A-Za-z0-9-]+", args.run_id):
        raise SystemExit("invalid run ID")
    repo = Path(__file__).resolve().parents[2]
    temporary_commit = Path("/tmp") / (args.run_id + ".commit")
    root = repo / "evidence/01_PT"
    if args.candidate_root is not None:
        root = check_candidate_root(repo, args.candidate_root)
    if args.validate_only:
        # A persisted manifest can validate an old run after /tmp is cleared. It is not
        # evidence of a new execution, and every mandatory scope is checked below.
        manifest = load_success_manifest(root / ROOT_MANIFEST)
        if manifest["runId"] != args.run_id:
            raise ValueError("invalid persisted reactor run")
        commit = manifest["targetCommit"]
        if temporary_commit.is_file() and temporary_commit.read_text().strip() != commit:
            raise ValueError("temporary and persisted source commits disagree")
    else:
        commit = temporary_commit.read_text().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("invalid evidence source commit")
    subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"], cwd=repo, check=True)
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip()
    paths = ["src", "pom.xml", "program/characterization"]
    if not args.validate_only:
        paths.extend(("tools/quality", ".mvn", "mvnw", "mvnw.cmd"))
    subprocess.run(["git", "diff", "--exit-code", commit, "--", *paths], cwd=repo, check=True)
    if not args.validate_only:
        root = reserve_candidate(repo, args.run_id, args.candidate_root)
        collect(repo, args.run_id, candidate_root=root)
    results = validate_all(root, args.run_id, commit, branch)
    print(json.dumps({"runId": args.run_id, "targetCommit": commit, "scopes": results,
                      "evidenceRoot": str(root),
                      "result": "PASS_PERSISTED_EVIDENCE_ONLY" if args.validate_only
                      else "PASS_EVIDENCE_SET_ONLY", "phaseComplete": False}))


if __name__ == "__main__":
    main()
