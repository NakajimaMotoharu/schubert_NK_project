"""Join the original JUnit XML, single exec, typed static and hand-reviewed monitor obligations."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
DECODER_SOURCE = "dba164629c"
DECODER = "tools/quality/jacoco_readonly_exec_subset.py"
OWNER = "dev/codex/schubert/nk/batch/monitoring/AlertLifecycle"
EXPECTED_ACTIONS = (
    ("snapshot()", "全体はactive Optionalの同一monitor読取一つ。同期範囲の縮小余地がない。"),
    ("interrupt(Duration elapsed)", "時刻の検査・確定と復旧窓の中断、active返却を一遷移で実施。"),
    ("violation(Severity observed, Instant at, Duration elapsed)",
     "時刻、解除の中断、先行イベント、件数・重症度、active置換が一つの更新。"),
    ("normal(CauseClearance clearance, Duration elapsed)",
     "時刻、保護・復旧窓、所定期限、activeの閉鎖を一遷移で実施。"),
)


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=40)


def report(path, raw):
    with path.open("x") as file:
        json.dump(raw, file, ensure_ascii=False, indent=2)
        file.write("\n")


def main():
    unit, = OPS.glob("PG41070-*/manifest.json")
    result = json.loads(unit.read_bytes())
    assert result["source"] == "559f5b5945e82374e0843dcfae11a8d07faef1ea"
    assert result["actualExit"] == 0 and result["launchCount"] == 1
    for ref in [*result["inputs"], result["originalJunitXml"], result["originalCoverageXml"],
                result["rawTsv"], result["execData"], result["spotbugs"]["report"],
                result["pmd"]["report"]]:
        assert pin(Path(ref["path"])) == ref
    xml = ET.parse(result["originalJunitXml"]["path"]).getroot()
    assert {k: int(xml.attrib[k]) for k in ("tests", "failures", "errors", "skipped")} == {
        "tests": 84, "failures": 0, "errors": 0, "skipped": 0,
    }
    results = [case for case in xml.findall("testcase")]
    assert len(results) == len({(c.attrib["classname"], c.attrib["name"]) for c in results}) == 84
    assert all(not any(element.tag in ("failure", "error", "skipped") for element in c)
               for c in results)
    prior84 = result["rejectedStaticRound"]
    assert pin(Path(prior84["path"])) == prior84
    assert json.loads(Path(prior84["path"]).read_bytes())["source"] != result["source"]

    target = {OWNER + suffix for suffix in (
        "", "$Event", "$Condition", "$Service", "$Severity", "$CauseClearance", "$State")}
    pinned = git("show", f"{DECODER_SOURCE}:{DECODER}")
    namespace = {}
    exec(compile(pinned, DECODER, "exec"), namespace)
    exec_data = Path(result["execData"]["path"]).read_bytes()
    stream = namespace["decode"](exec_data, target)
    assert len(stream["sessions"]) == 1 and stream["sessions"][0]["labelBytesHex"] == b"PG41070".hex()
    assert set(stream["classes"]) == target
    expected_raw = {"LINE": 111, "METHOD": 41, "CLASS": 7, "BRANCH": 34, "INSTRUCTION": 667}
    selected = {r["className"]: r for r in result["rawAll"] if r["className"] in target}
    for name, row in selected.items():
        assert row["matched"] and int(row["crc64"], 16) == int(stream["classes"][name]["crc64"], 16)
        assert all(row["counters"][key]["missed"] == 0 for key in expected_raw)
    assert set(selected) == target
    assert {key: sum(r["counters"][key]["covered"] for r in selected.values()) for key in expected_raw} == expected_raw

    source_entry = next(i for i in result["inputs"] if i["path"].endswith("/AlertLifecycle.java"))
    source = Path(source_entry["path"]).read_text().splitlines()
    assert git("show", f"{result['source']}:{source_entry['path']}") == Path(source_entry["path"]).read_bytes()
    findings = ET.parse(result["pmd"]["report"]["path"]).getroot()
    rule_namespace = {"p": findings.tag.partition("}")[0].removeprefix("{")}
    classified, carried = [], []
    for file in findings.findall("p:file", rule_namespace):
        name = Path(file.attrib["name"]).name
        for item in file.findall("p:violation", rule_namespace):
            line = int(item.attrib["beginline"])
            rule = item.attrib["rule"]
            if name == "AlertLifecycle.java":
                assert rule == "AvoidSynchronizedAtMethodLevel"
                expected, reason = next((method, why) for method, why in EXPECTED_ACTIONS
                                        if method.split("(", 1)[0] + "(" in source[line - 1])
                classified.append(dict(line=line, rule=rule, method=expected,
                                       disposition="FULL_PRIVATE_ATOMIC_METHOD", reason=reason))
            else:
                carried.append((name, str(line), rule, (item.text or "").strip()))
    prior_static, = OPS.glob("PG40800-*/manifest.json")
    prior = json.loads(prior_static.read_bytes())
    original_others = [(r["source"], r["line"], r["rule"], r["message"])
                       for r in prior["pmdFindings"] if r["source"] != "AlertLifecycle.java"]
    assert Counter(carried) == Counter(original_others) and len(carried) == 10
    prior_sources = {Path(r["path"]).name: r for r in prior["sources"]}
    assert all(pin(Path(prior_sources[name]["path"])) == prior_sources[name] for name, *_ in carried)
    assert {row["method"] for row in classified} == {pair[0] for pair in EXPECTED_ACTIONS}
    assert result["spotbugs"]["findings"] == 0 and result["spotbugs"]["errors"] == 0

    out = OPS / "PG41072-f03-alert-owner-state-independent-v1"
    out.mkdir()
    manifest = out / "manifest.json"
    report(manifest, dict(
        actualExit=0, productionCore=result["source"], run=pin(unit),
        jvmSession="PG41070", sessionOriginalSha256=result["execData"]["sha256"], ownClassCrcCount=7,
        independentDecoderSource=git("rev-parse", DECODER_SOURCE).decode().strip(),
        independentDecoderSha256=sha256(pinned).hexdigest(), suiteCount=11,
        passed=84, failed=0, errors=0, skipped=0, notRun=0, rawAlertCounters=expected_raw,
        rawMissed={key: 0 for key in expected_raw}, manualExclusions=0,
        extraScopeUnfilteredDataRetained=True, scopedSpotBugsIssues=0,
        pmdRaw=14, pmdRawExit=4, pmdSuppressed=0, newSyncDisposition=classified,
        otherExistingPmdOccurrences=10, previousStatic=pin(prior_static),
        selectedOriginalResultReplayed=0, productBackendOperations=0, allF03=False,
        whole451=False, formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    ))
    print(pin(manifest))


if __name__ == "__main__":
    main()
