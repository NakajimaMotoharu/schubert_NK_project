"""Verify the independent Protocol fixture source chain for SS322 and SS354."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


FIELD_FIXTURE = "fields-ui234-236.tsv"
GOLDEN_FIXTURE = "payload-golden-ui234-236.tsv"
FIXTURE_DIR = "src/schubert-nk-protocol/src/test/resources/protocol"
UI_DIR = "documents/200_UI/230_インターフェース"
UI_DOCUMENTS = (
    f"{UI_DIR}/234_認証・検索・シナリオ電文仕様.md",
    f"{UI_DIR}/235_メディア・ログ電文仕様.md",
    f"{UI_DIR}/236_管理・質問・通知電文仕様.md",
)
SOURCE_HEADER = "# source-sha256 "
FIELD_HEADER = f"# {FIELD_FIXTURE}-sha256="


def sha256(contents):
    return hashlib.sha256(contents).hexdigest()


def verify_provenance(fields, golden, designs):
    checks = []
    sources = [line for line in fields.decode("utf-8").splitlines() if line.startswith(SOURCE_HEADER)]
    for path in UI_DOCUMENTS:
        prefix = f"{SOURCE_HEADER}{path}="
        declared = [line.removeprefix(prefix) for line in sources if line.startswith(prefix)]
        checks.append(check(FIELD_FIXTURE, path, declared, sha256(designs[path])))
    for line in sources:
        if not any(line.startswith(f"{SOURCE_HEADER}{path}=") for path in UI_DOCUMENTS):
            checks.append({"fixture": FIELD_FIXTURE, "status": "unexpected-source-declaration"})
    declared = [
        line.removeprefix(FIELD_HEADER)
        for line in golden.decode("utf-8").splitlines()
        if line.startswith(FIELD_HEADER)
    ]
    checks.append(check(GOLDEN_FIXTURE, FIELD_FIXTURE, declared, sha256(fields)))
    return checks


def check(fixture, source, declared, expected):
    return {
        "fixture": fixture,
        "source": source,
        "declarations": len(declared),
        "sha256": expected,
        "status": "match" if declared == [expected] else "missing-duplicate-or-stale",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Git revision of the Protocol fixtures")
    parser.add_argument("design", help="Git revision of the approved UI design")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]

    def git(*arguments):
        return subprocess.check_output(["git", "-C", str(root), *arguments])

    source = git("rev-parse", "--verify", "--end-of-options", args.source + "^{commit}").decode().strip()
    design = git("rev-parse", "--verify", "--end-of-options", args.design + "^{commit}").decode().strip()
    checks = verify_provenance(
        git("show", f"{source}:{FIXTURE_DIR}/{FIELD_FIXTURE}"),
        git("show", f"{source}:{FIXTURE_DIR}/{GOLDEN_FIXTURE}"),
        {path: git("show", f"{design}:{path}") for path in UI_DOCUMENTS},
    )
    print(json.dumps({"source": source, "design": design, "checks": checks}, ensure_ascii=False, indent=2))
    return int(any(row["status"] != "match" for row in checks))


if __name__ == "__main__":
    raise SystemExit(main())
