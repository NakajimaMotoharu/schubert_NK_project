#!/usr/bin/env python3
"""PT-QUALITY-005: isolated regeneration equality and mismatch-detection canary.

This is a reproducibility check, not the functional oracle for wire/semantic PT.
Never modifies production, SS, Current baseline, or golden fixtures.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


FORMATTER_SHA256 = "25b400f003089d23cc5320cdaf1a16cabee19b8aa3434d0ff021b3d9f42154b4"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(generated, production):
    return [str(path.relative_to(generated))
            for path in sorted(generated.rglob("*.java"))
            if not (production / path.relative_to(generated)).is_file()
            or digest(path) != digest(production / path.relative_to(generated))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formatter", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    generator = repo / "src/schubert-nk-protocol/build-tools/001_generate_payload_records.py"
    production = repo / "src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout"
    fixture = repo / "src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv"
    design = repo / "documents/300_SS/320_メッセージング/323_全電文layout・Java・DB対応表.md"
    java = Path(os.environ["JAVA_HOME"]) / "bin/java"
    if digest(args.formatter) != FORMATTER_SHA256:
        raise SystemExit("pinned Google Java Format 1.36.1 SHA-256 mismatch")
    started = datetime.now(timezone.utc).isoformat()
    protected = [generator, fixture, design, *sorted(production.rglob("*.java"))]
    before = {str(path.relative_to(repo)): digest(path) for path in protected}
    commands = []
    with tempfile.TemporaryDirectory(prefix="pgpt-generation-", dir=args.work_dir) as temporary:
        generated = Path(temporary)
        command = [sys.executable, str(generator), "--output-root", str(generated)]
        subprocess.run(command, cwd=repo, check=True, capture_output=True, timeout=60)
        commands.append(command)
        files = sorted(generated.rglob("*.java"))
        command = [str(java), "-jar", str(args.formatter.resolve()),
                   "--skip-reflowing-long-strings", "--replace",
                   *[str(path) for path in files]]
        subprocess.run(command, cwd=repo, check=True, capture_output=True, timeout=60)
        commands.append(command[:5] + ["<70 isolated generated Java paths>"])
        differences = compare(generated, production)
        hashes = {str(path.relative_to(generated)): digest(path) for path in files}
        # Mutate only disposable output: the comparator must reject one exact changed file.
        canary = generated / "PayloadTypeCatalog.java"
        canary.write_bytes(canary.read_bytes() + b"// deliberate reproducibility canary\n")
        changed = compare(generated, production)
        negative_pass = not differences and changed == ["PayloadTypeCatalog.java"]
    unchanged = before == {str(path.relative_to(repo)): digest(path) for path in protected}
    passed = len(files) == 70 and not differences and negative_pass and unchanged
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    result = {
        "testId": "PT-QUALITY-005", "relatedBugs": ["BUG-017", "BUG-019"],
        "relatedYkt": ["YKT-014", "YKT-016"], "targetCommit": commit,
        "startedAt": started, "completedAt": datetime.now(timezone.utc).isoformat(),
        "commands": commands, "formatterVersion": "1.36.1",
        "formatterSha256": FORMATTER_SHA256, "expectedFileCount": 70,
        "actualFileCount": len(files), "differences": differences,
        "negativeCanary": "PASS" if negative_pass else "FAIL",
        "protectedSourcesUnchanged": unchanged, "sourceSha256": before,
        "generatedSha256": hashes, "status": "PASS" if passed else "FAIL",
        "oracle": "69 SS323 named records + one 64-layout catalog; byte equality after pinned formatting. Functional expectations remain independent SS-offset golden vectors.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "generatedFiles": len(files),
                      "differences": differences, "evidence": str(args.output)}))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
