"""Qualify the 211-case same-stream FileStore result against the immutable inputs."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import tarfile
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


E = Path("evidence/01_PT/018_NK-OPS-001/evidence")
FILESTORE = ("dev.codex.schubert.characterization.GateOwnedFileStoreContract",
             "admitsOnlyTheOwnedRealFileStoreThroughThePublicCli(Path)")
METRICS = ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")


def read(path):
    return json.loads(Path(path).read_bytes())


def pin(path):
    return dict(path=str(path), sha256=sha256(Path(path).read_bytes()).hexdigest())


def main():
    run = next(E.glob("PG40706-*"))
    begin, result, pre = (read(run / name) for name in ("begin.json", "manifest.json", "boot-format-independent.json"))
    assert begin["capsule"] == pin(begin["capsule"]["path"])
    assert begin["pmoPrecheck"] == pin(begin["pmoPrecheck"]["path"])
    assert pre["historicalSameBootEquality"] and pre["freshAdmissionRequired"]
    host = result["admission"]
    term = result["terminal"]
    expected_boot = read(begin["pmoPrecheck"]["path"])["bootIdSha256"]
    assert host["bootReceiptSha256"] == term["bootReceiptSha256"] == expected_boot
    assert term["ownerUid"] == host["uid"] == 1000
    assert host["host"] == "haruka" and host["workspaceMode"] == "0700"
    assert host["freeBytes"] >= 21_474_836_480 and host["activeOwnedWorkspaceJobs"] == 0 and host["runAbsent"]
    assert term["workspace"] == host["workspace"] + "/" + begin["run"]
    assert result["actualExit"] == result["sshExit"] == term["actualExit"] == 0
    assert result["outcome"] == "TERMINAL_RETURNED" and result["authPrompts"] == 1 and result["capsuleSent"]
    assert term["stage"] == "terminal" and term["allocatedRun"] and term["actualBackendActions"] == 0
    assert all(row["actualExit"] == 0 for row in term["steps"].values())
    assert result["artifacts"].keys() == {"cases.json", "combined.exec", "coverage.xml"}
    assert all(pin(row["path"]) == row for row in result["artifacts"].values())
    assert term["totals"] == {"tests": 211, "failures": 0, "errors": 0, "skipped": 0}

    previous = next(E.glob("PG40658-*/manifest.json"))
    local_xml = previous.with_name("xml") / "TEST-junit-jupiter.xml"
    assert read(previous)["xmlHashes"][local_xml.name] == pin(local_xml)["sha256"]
    local = {(row.get("classname"), row.get("name")) for row in ET.parse(local_xml).iter("testcase")}
    cases = read(run / "cases.json")
    assert len(local) == 210 and FILESTORE not in local and len(cases) == 211
    assert {(row["classname"], row["name"]) for row in cases} == local | {FILESTORE}
    assert all(row["outcome"] == "pass" for row in cases)
    spec = begin["spec"]
    command = term["steps"]["unit"]["command"]
    assert [a.split("=", 1)[1] for a in command if a.startswith("--select-class=")] == spec["selectors"]
    assert len(spec["selectors"]) == len({row["classname"] for row in cases}) == 21
    coverage = ET.parse(run / "coverage.xml").getroot()
    assert term["session"] == spec["session"]
    assert [item.get("id") for item in coverage.findall("sessioninfo")] == [spec["session"]]

    tool_report = read(next(E.glob("PG40662-*/manifest.json")))
    no_code = set(tool_report["raw"]["noCode"])
    assert len(no_code) == 5 and len(spec["physical"]) == 17
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    tool_crcs = runpy.run_path(str(E.parent / "input/5257_p01810_broker_evidence_value_post.py"))
    crc64 = tool_crcs["crc64"]
    runtime = run / "combined.exec"
    names = {name.removesuffix(".class") for name in spec["physical"]}
    observed = decode(runtime.read_bytes(), names - no_code)
    assert [row["labelBytesHex"] for row in observed["sessions"]] == [spec["session"].encode().hex()]

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-p020-known-211-post-") as room:
        folder = Path(room)
        expected_crc = {}
        args = []
        with tarfile.open(begin["capsule"]["path"], "r:gz") as archive:
            for name, digest in sorted(spec["physical"].items()):
                body = archive.extractfile(f"classes/{name}").read()
                assert sha256(body).hexdigest() == digest
                binary = name.removesuffix(".class")
                if binary not in no_code:
                    expected_crc[binary] = int(crc64(body), 16)
                path = folder / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
                args.append(path)
        assert {k: int(row["crc64"], 16) for k, row in observed["classes"].items()} == expected_crc
        raw_command = list(map(str, [*tool_report["raw"]["command"][:5], runtime, *args]))
        raw = subprocess.run(raw_command, capture_output=True, check=False, timeout=40,
                             env={"LANG": "C.UTF-8", "PATH": "/usr/bin:/bin"})
    assert raw.returncode == 0
    seen = set()
    totals = Counter()
    misses = []
    for line in raw.stdout.decode().splitlines():
        row = line.split("\t")
        if row[0] == "CLASS":
            assert row[1] in names and row[1] not in seen
            seen.add(row[1])
            for value in row[6:]:
                kind, deficit, hit = value.split(":")
                totals[kind, "missed"] += int(deficit)
                totals[kind, "covered"] += int(hit)
        if row[0] == "METHOD":
            absent = [value for value in row[5:] if int(value.split(":")[1])]
            if absent:
                misses.append(dict(className=row[1], method=row[2], descriptor=row[3], misses=absent))
    assert seen == names
    counters = {key: {name: totals[key, name] for name in ("covered", "missed")} for key in METRICS}
    out = E / "PG40708-p020-current-211-independent-v1"
    out.mkdir()
    (out / "raw.tsv").write_bytes(raw.stdout)
    manifest = dict(
        actualExit=0, toolSource=begin["previousToolSource"], workspaceSource=begin["source"],
        completedTests=211, failed=0, errors=0, skipped=0, notRun=0, selectors=21,
        physicalClasses=17, executableClasses=12, naturalNoCodeTypes=sorted(no_code),
        oneSession=spec["session"], caseSetMatchesIndependent210PlusOne=True, crcAllExact=True,
        currentAdmittedBootHash=expected_boot, associatedOwnedJobsAtEntry=0,
        runtimeCounters=counters, fourIndicatorsAllCovered=all(counters[k]["missed"] == 0 for k in METRICS[:4]),
        rawMissedMethods=misses, productTests=0, backendActions=0, actualBrowserOrChr=False,
        whole451Accepted=False, formalDelta=0, oldRunsMerged=0, revokedOrRepeatedRuns=0,
        rawCommand=raw_command, rawExit=raw.returncode,
        raw=pin(out / "raw.tsv"), legacyRoster=pin(local_xml),
        receipts=list(map(pin, [run / "begin.json", run / "manifest.json", run / "cases.json",
                                run / "combined.exec", run / "coverage.xml"])),
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(dict(tests=211, raw=counters, missedMethods=len(misses)))


if __name__ == "__main__":
    main()
