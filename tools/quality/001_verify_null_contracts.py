#!/usr/bin/env python3
"""PT-QUALITY-001: execute positive/negative compile canaries and collect safe evidence."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--maven-repository", required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    command = [str(repo / "mvnw"), "-o", "--no-transfer-progress",
               "-Dmaven.repo.local=" + args.maven_repository,
               "-f", "tools/quality/null-contracts/pom.xml"]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    source_paths = [repo / "pom.xml", repo / "tools/quality/null-contracts/pom.xml",
                    *sorted((repo / "tools/quality/null-contracts/fixtures").rglob("*.java"))]
    before = {str(path.relative_to(repo)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in source_paths}
    started = datetime.now(timezone.utc).isoformat()
    results = []
    for fixture, expected_exit in (("valid", 0), ("invalid", 1)):
        full_command = command + ["-Dcanary.source=fixtures/" + fixture, "clean", "compile"]
        run = subprocess.run(full_command, cwd=repo, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=120, check=False)
        diagnostics = sorted(set(line.split("error: [NullAway] ", 1)[1]
                                 for line in run.stdout.splitlines()
                                 if "error: [NullAway] " in line))
        matched = []
        if fixture == "invalid":
            for expected in ("dereferenced expression 'value' is @Nullable",
                             "returning @Nullable expression from method with @NonNull return type",
                             "dereferenced expression 'values.getFirst()' is @Nullable",
                             "passing @Nullable parameter 'null' where @NonNull is required"):
                matched.append(expected in diagnostics)
        passed = (run.returncode == expected_exit
                  and ((fixture == "valid" and "BUILD SUCCESS" in run.stdout)
                       or (fixture == "invalid" and len(matched) == 4 and all(matched))))
        results.append({"fixture": fixture, "command": full_command,
                        "exitCode": run.returncode, "expectedExitCode": expected_exit,
                        "nullAwayDiagnostics": diagnostics, "expectedDiagnosticMatches": matched,
                        "status": "PASS" if passed else "FAIL",
                        "rawLogSha256": hashlib.sha256(run.stdout.encode()).hexdigest()})
    after = {str(path.relative_to(repo)): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in source_paths}
    passed = before == after and all(result["status"] == "PASS" for result in results)
    manifest = {"testId": "PT-QUALITY-001", "targetCommit": commit,
                "startedAt": started, "completedAt": datetime.now(timezone.utc).isoformat(),
                "javaHome": os.environ.get("JAVA_HOME", "NOT_SET"),
                "sourceSha256": before, "sourceUnchanged": before == after,
                "expectedOracle": "453_Null解析gate検証仕様.md QLT-NULL-01..05",
                "results": results, "status": "PASS" if passed else "FAIL",
                "redaction": "Only fixed canary diagnostics and execution metadata are retained."}
    artifact = output / "null-canary-results.json"
    artifact.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "artifact": str(artifact)}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
