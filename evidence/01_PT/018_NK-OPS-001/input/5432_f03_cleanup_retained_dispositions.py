"""Join 24 existing Cleanup diagnostics to prior decisions using byte-stable source lines."""

from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
PLAN = next((ROOT / "documents/400_PGPT/470_PMO").glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
TARGETS = {"read", "readRejected"}


def digest(raw):
    return sha256(raw).hexdigest()


@cache
def verified(path, expected):
    data = Path(path).read_bytes()
    assert digest(data) == expected
    return data


def raw(ref):
    return verified(ref["path"], ref["sha256"])


def snapshot(source, path):
    return subprocess.check_output(["git", "show", f"{source}:{path}"], cwd=ROOT, timeout=15)


def report_items(xml):
    doc = ET.fromstring(raw(xml))
    return [r for r in doc.iter() if r.tag.endswith("}violation")
            and r.get("method") in TARGETS]


def fingerprint(node, first):
    return (node.get("method"), int(first), int(node.get("begincolumn")),
            node.get("rule"), " ".join(node.text.split()))


def main():
    start = json.loads(next(PLAN.glob("1123_F03Cleanup*")).read_bytes())
    v = start["values"]
    refs = v["oracleReferences"]
    for ref in refs:
        raw(ref)
    cleanup, retained, old, lineage = (json.loads(raw(ref)) for ref in refs[1:])
    core = v["productionCoreMain"]
    assert cleanup["core"] == lineage["productionCore"] == core
    assert retained["productionCore"] == old["productionCore"] == lineage["previousCore"]
    path = cleanup["target"]["path"]
    old_bytes = snapshot(old["productionCore"], path)
    current_bytes = snapshot(core, path)
    assert raw(cleanup["target"]) == current_bytes and old_bytes != current_bytes
    old_lines, current_lines = old_bytes.splitlines(), current_bytes.splitlines()
    matching = SequenceMatcher(None, current_lines, old_lines, autojunk=False)
    current_to_old = {a + offset + 1: b + offset + 1
                      for a, b, size in matching.get_matching_blocks() for offset in range(size)}
    old_rows = {}
    for row in json.loads(raw(retained["exact"])):
        if row["path"] != path or row["method"] not in TARGETS:
            continue
        prior = row["prior"]
        ref = prior["reference"]
        ref_cases = json.loads(raw(ref))
        verdict = next(case for case in ref_cases if case["rawFindingIndex"] == prior["index"])
        assert prior["sourceSha256"] == verdict["sourceSha256"] == digest(old_bytes)
        assert verdict["decision"] == prior["decision"] and verdict["decision"].startswith("NOT_APPLICABLE_")
        assert all(verdict[key] == row[key] for key in ("path", "rule", "line", "column"))
        prior_method = verdict.get("method")
        if prior_method is not None:
            assert prior_method.rsplit("#", 1)[-1].split("(", 1)[0] == row["method"]
        key = (row["method"], row["line"], row["column"], row["rule"],
               " ".join(row["message"].split()))
        assert key not in old_rows
        old_rows[key] = {"decision": verdict["decision"], "sourceSha256": verdict["sourceSha256"],
                         "priorIndex": prior["index"], "previousOccurrence": row["occurrence"],
                         "reference": ref}
    xml = next(row for row in cleanup["reports"] if row["path"].endswith("/pmd.xml"))
    cases = report_items(xml)
    assert len(old_rows) == len(cases) == 24
    matched = []
    for case in cases:
        first, last = int(case.get("beginline")), int(case.get("endline"))
        previous_first = current_to_old[first]
        for line in range(first, last + 1):
            assert current_to_old[line] == previous_first + line - first
        key = fingerprint(case, previous_first)
        evidence = old_rows.pop(key)
        matched.append({"method": case.get("method"), "rule": case.get("rule"),
                        "currentLine": first, "oldLine": previous_first,
                        "column": int(case.get("begincolumn")), **evidence})
    assert not old_rows and Counter(row["method"] for row in matched) == {"read": 12, "readRejected": 12}
    result = dict(
        actualExit=0, source=v["source"], productionCore=core, startEvent=start["eventId"],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), inputs=refs, rawPmdCurrent=cleanup["pmdRaw"],
        oldRawAcceptedReceipts=matched, reopened=0, priorReviewedByPG40748=24,
        reusedHistoricalByExactMatch=24, applicableUnclassifiedInThisFile=0,
        unchangedAcceptedBySS332=["typed close priority", "original Throwable", "alias ownership"],
        relatedFile=cleanup["target"], runnerSha256=digest(Path(__file__).read_bytes()),
        dynamicTestExecutions=0, staticAnalyzerExecutions=0, actualHeldOperations=0,
        wholeBatch=False, wholeF03=False, whole451=False, formalDelta=0,
    )
    out = OPS / v["run"]
    out.mkdir()
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print("24/24 matched to original disposition identities on the exact retained source spans")


if __name__ == "__main__":
    main()
