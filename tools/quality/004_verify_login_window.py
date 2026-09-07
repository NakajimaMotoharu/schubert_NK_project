#!/usr/bin/env python3
"""Read-only Current/NK fixed-clock boundary comparison (BUG-021/SSC-009/PT-AUT-003-05)."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--nk-classes", type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    nk = args.nk_classes or repo / "src/schubert-nk-api/target/classes"
    current = args.current_root / "program/app/target/classes"
    jdk = Path(os.environ["JAVA_HOME"])
    files = [args.current_root / "program/app/src/main/java/dev/codex/schubert/security/LoginAttemptService.java"]
    files += sorted((current / "dev/codex/schubert/security").glob("LoginAttemptService*.class"))
    files += [nk / "dev/codex/schubert/nk/api/security/LoginAttemptState.class",
              nk / "dev/codex/schubert/nk/api/security/LoginAttemptKind.class"]
    if len(files) != 6 or any(not path.is_file() for path in files):
        raise SystemExit("required Current/NK inputs are missing")
    hash_inputs = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    before = hash_inputs()
    started = datetime.now(timezone.utc).isoformat()
    classpath = os.pathsep.join((str(current), str(nk)))
    probe = repo / "tools/quality/login-boundary-probe/dev/codex/schubert/security/CurrentWindowBoundaryProbe.java"
    with tempfile.TemporaryDirectory(prefix="login-window-", dir=args.work_dir) as temporary:
        compile_command = [str(jdk / "bin/javac"), "-cp", classpath, "-d", temporary, str(probe)]
        compiled = subprocess.run(compile_command, capture_output=True, text=True)
        if compiled.returncode or compiled.stderr or compiled.stdout:
            raise SystemExit("independent probe compilation did not complete cleanly")
        run_command = [str(jdk / "bin/java"), "-cp", temporary + os.pathsep + classpath,
                       "dev.codex.schubert.security.CurrentWindowBoundaryProbe"]
        observed = subprocess.run(run_command, capture_output=True, text=True)
    if observed.stderr or observed.returncode not in (0, 2):
        raise SystemExit("independent probe execution failed")
    rows = []
    lines = observed.stdout.splitlines()
    for line in lines[:-1]:
        match = re.fullmatch(r"kind=(USER|IP) boundaryOffsetNanos=(-1|0|1) currentLocked=(true|false) nkLocked=(true|false)", line)
        if not match:
            raise SystemExit("probe output is outside the safe contract")
        kind, offset, old, new = match.groups()
        rows.append({"kind": kind, "offsetNanos": int(offset), "currentLocked": old == "true", "nkLocked": new == "true"})
    expected = [(kind, offset) for kind in ("USER", "IP") for offset in (-1, 0, 1)]
    if [(row["kind"], row["offsetNanos"]) for row in rows] != expected:
        raise SystemExit("probe case set is incomplete")
    mismatches = sum(row["currentLocked"] != row["nkLocked"] for row in rows)
    if lines[-1] != f"cases=6 mismatches={mismatches}" or observed.returncode != (2 if mismatches else 0):
        raise SystemExit("probe result and exit code disagree")
    if before != hash_inputs():
        raise SystemExit("comparison modified a protected input")
    report = {"testId": "PT-AUT-003-05", "bug": "BUG-021", "ssc": "SSC-009", "ykt": "YKT-018",
              "startedAt": started, "completedAt": datetime.now(timezone.utc).isoformat(),
              "status": "FAIL" if mismatches else "PASS", "exitCode": observed.returncode,
              "compileCommand": compile_command, "runCommand": run_command,
              "jdk": subprocess.check_output([str(jdk / "bin/java"), "--version"], text=True).splitlines()[0],
              "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip(),
              "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
              "sourceDirty": bool(subprocess.check_output(["git", "status", "--porcelain", "--", "src", "tools/quality"], cwd=repo, text=True)),
              "inputSha256": before, "probeSha256": hashlib.sha256(probe.read_bytes()).hexdigest(),
              "inputsUnchanged": True, "cases": rows, "mismatches": mismatches,
              "baselineWritten": False, "sensitiveValuesRecorded": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "cases": 6, "mismatches": mismatches, "inputsUnchanged": True}))
    raise SystemExit(observed.returncode)


if __name__ == "__main__":
    main()
