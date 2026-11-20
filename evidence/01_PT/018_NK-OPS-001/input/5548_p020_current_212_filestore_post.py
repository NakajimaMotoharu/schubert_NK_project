"""Independently match the single returned FileStore run and all executable bytecode."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import xml.etree.ElementTree as ET


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
RUN = "PG41004-p020-current-212-owned-filestore-v1"
REQUIRED = ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")
FILESTORE = ("dev.codex.schubert.characterization.GateOwnedFileStoreContract",
             "admitsOnlyTheOwnedRealFileStoreThroughThePublicCli(Path)")


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


def main():
    entry = OPS / RUN
    paths = [entry / name for name in (
        "begin.json", "manifest.json", "admission.json", "owner-execution-start.json")]
    begin, result, admission, activation = [read(path) for path in paths]
    assert begin["run"] == result["run"] == activation["run"] == RUN
    assert begin["toolSource"] == result["source"] == activation["source"]
    assert result["actualExit"] == result["sshExit"] == 0 and result["state"] == "TERMINAL_RETURNED"
    assert result["authPrompts"] == 1 and result["capsuleTransferred"] is True
    term = result["terminal"]
    assert term["actualExit"] == 0 and term["stage"] == "terminal" and term["allocatedRun"]
    assert term["session"] == begin["session"] and term["actualBackendActions"] == 0
    assert term["bootReceiptSha256"] == admission["bootReceiptSha256"] == activation["bootReceiptSha256"]
    assert admission["uid"] == term["ownerUid"] == 1000 and admission["host"] == "haruka"
    assert admission["runAbsent"] and admission["activeOwnedWorkspaceJobs"] == 0
    assert term["workspace"] == admission["workspace"] + "/" + RUN
    assert all(step["actualExit"] == 0 for step in term["steps"].values())

    returned = {name: Path(row["path"]) for name, row in result["returnedEvidence"].items()}
    assert set(returned) == {"cases.json", "combined.exec", "coverage.xml"}
    assert all(pin(path) == result["returnedEvidence"][name] for name, path in returned.items())
    previous = Path(begin["localEvidence"]["path"])
    assert pin(previous) == begin["localEvidence"]
    local = read(previous)
    assert term["totals"] == dict(tests=212, failures=0, errors=0, skipped=0)
    local_xml = Path(local["xml"]["path"])
    assert pin(local_xml) == local["xml"]
    expected = Counter((row.attrib["classname"], row.attrib["name"]) for row in ET.parse(local_xml).iter("testcase"))
    actual = read(returned["cases.json"])
    observed = Counter((row["classname"], row["name"]) for row in actual)
    assert expected[FILESTORE] == 0 and observed == expected + Counter({FILESTORE: 1})
    assert len(actual) == 212 and all(row["outcome"] == "pass" for row in actual)
    assert len(begin["selectors"]) == 21 and len(set(begin["selectors"])) == 21
    command = term["steps"]["unit"]["command"]
    assert [arg.split("=", 1)[1] for arg in command if arg.startswith("--select-class=")] == begin["selectors"]
    report = ET.parse(returned["coverage.xml"]).getroot()
    assert [row.attrib["id"] for row in report.findall("sessioninfo")] == [begin["session"]]

    prior = next(OPS.glob("PG40708*/manifest.json"))
    old = read(prior)
    no_code = set(old["naturalNoCodeTypes"])
    root = Path("../pgpt-runs/PG379").resolve() / local["run"] / "snapshot/program/characterization/target/classes"
    physical = {str(p.relative_to(root)).removesuffix(".class"): p for p in root.rglob("*.class")}
    assert len(physical) == 17 and all(pin(path)["sha256"] == local["physical"][name + ".class"]
                                       for name, path in physical.items())
    names = set(physical) - no_code
    assert len(names) == 12 and len(no_code) == 5
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    crc64 = runpy.run_path(str(OPS.parent / "input/5257_p01810_broker_evidence_value_post.py"))["crc64"]
    observed_exec = decode(returned["combined.exec"].read_bytes(), names)
    assert [row["labelBytesHex"] for row in observed_exec["sessions"]] == [begin["session"].encode().hex()]
    assert {name: int(row["crc64"], 16) for name, row in observed_exec["classes"].items()} == {
        name: int(crc64(physical[name].read_bytes()), 16) for name in names}
    measure = next(row["command"] for row in local["steps"] if row["step"] == "unfiltered")
    raw_cmd = [*measure[:4], str(returned["combined.exec"]), *map(str, sorted(physical.values()))]
    raw = subprocess.run(raw_cmd, capture_output=True, timeout=45, check=False)
    assert raw.returncode == 0
    totals = Counter()
    observed = set()
    for line in raw.stdout.decode().splitlines():
        row = line.split("\t")
        if row[0] == "CLASS":
            assert row[1] in physical and row[1] not in observed
            observed.add(row[1])
            assert (row[3] == "true") == (row[1] not in no_code)
            for value in row[6:]:
                kind, missed, covered = value.split(":")
                totals[kind, "missed"] += int(missed)
                totals[kind, "covered"] += int(covered)
    assert observed == set(physical)
    out = OPS / "PG41006-p020-current-212-independent-v1"
    out.mkdir()
    (out / "unfiltered.tsv").write_bytes(raw.stdout)
    (out / "case-results.json").write_text(json.dumps(actual, ensure_ascii=False, indent=2) + "\n")
    counters = {name: {"missed": totals[name, "missed"], "covered": totals[name, "covered"]} for name in REQUIRED}
    passed = all(row["missed"] == 0 and row["covered"] > 0 for row in counters.values())
    manifest = dict(
        actualExit=0 if passed else 1, toolSource=begin["toolSource"], productionCore=begin["productionCore"],
        run=RUN, session=begin["session"], completedTests=212, errors=0, failures=0, skipped=0, notRun=0,
        localOracle=pin(local_xml), exactRosterEqualsLocal211PlusExistingFileStore=True, selectors=21,
        physicallyVerified=17, executableCrcsVerified=12, naturalNoCodeTypes=sorted(no_code),
        runtimeCounters=counters, sameSourceRawAll=passed, terminalEvidence=[pin(path) for path in paths],
        returnedEvidence=result["returnedEvidence"], normalizedCases=pin(out / "case-results.json"),
        rawCommand=raw_cmd, rawExit=raw.returncode, rawOutput=pin(out / "unfiltered.tsv"), oldExecMerged=False,
        actualProductTests=0, actualChr=0, actualBackendActions=0, whole451=False, formalDelta=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat())
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(passed, counters)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
