"""Validate the owned real FileStore and complete offline suite as one evidence run."""

from collections import Counter
import os
from pathlib import Path
import runpy
import subprocess
import xml.etree.ElementTree as ET


INPUT = Path(__file__).parent
UPPER = runpy.run_path(str(INPUT / "5326_f02_group_lookup_upper.py"))
STORE, COMMON = (UPPER[k] for k in ("EVIDENCE", "COMMON"))


def main():
    read = UPPER["read"]
    pin, dump, sha = (COMMON[k] for k in ("pin", "dump", "sha"))
    run = next(STORE.glob("PG40396-*"))
    begin, terminal, attestation = (run / name for name in ("begin.json", "manifest.json", "capsule-independent.json"))
    b, t, apt = map(read, (begin, terminal, attestation))
    previous_run = next(STORE.glob("PG40208-*"))
    old = read(previous_run / "manifest.json")
    old_post = read(next(STORE.glob("PG40212-*/manifest.json")))
    assert t["sshExit"] == t["actualExit"] == t["terminal"]["actualExit"] == 0
    assert t["outcome"] == "TERMINAL_RETURNED" and t["authPrompts"] == 1 and t["capsuleSent"] is True
    assert t["terminal"]["boot"] == t["admission"]["boot"]
    assert t["terminal"]["ownerUid"] == t["admission"]["uid"] == 1000
    assert t["admission"]["workspaceMode"] == "0700" and t["admission"]["runAbsent"] is True
    assert t["admission"]["activeOwnedWorkspaceJobs"] == 0 and t["admission"]["freeBytes"] >= 21_474_836_480
    assert apt["preparedBytesSha256"] == b["spec"]["capsuleSha256"]
    assert t["terminal"]["totals"] == dict(tests=209, failures=0, errors=0, skipped=0)
    assert t["terminal"]["steps"]["unit"]["actualExit"] == 0
    for item in t["artifacts"].values():
        assert pin(Path(item["path"])) == item
    old_xml = previous_run / "xml/TEST-junit-jupiter.xml"
    assert pin(old_xml)["sha256"] == old["xmlHashes"][old_xml.name]
    prior = {(row.get("classname"), row.get("name"))
             for row in ET.parse(old_xml).getroot().iter("testcase")}
    assert len(prior) == 208 and len({c for c, _ in prior}) == 20
    data = read(run / "cases.json")
    actual = {(row["classname"], row["name"]) for row in data}
    fresh = ("dev.codex.schubert.characterization.GateOwnedFileStoreContract",
             "admitsOnlyTheOwnedRealFileStoreThroughThePublicCli(Path)")
    assert actual == prior | {fresh} and len(actual) == len(data) == 209
    assert all(row["outcome"] == "pass" for row in data)

    runtime = run / "combined.exec"
    code_dir = Path(old["classesDir"])
    expected = b["spec"]["physical"]
    no_code = set(old_post["raw"]["noCode"])
    assert expected == old["mainPhysical"] and len(expected) == 17 and len(no_code) == 5
    names = {name.removesuffix(".class") for name in expected}
    code = names - no_code
    assert len(code) == 12
    crc64 = runpy.run_path(str(INPUT / "5257_p01810_broker_evidence_value_post.py"))["crc64"]
    decode = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    observed = decode(runtime.read_bytes(), code)
    assert [v["labelBytesHex"] for v in observed["sessions"]] == [b["spec"]["session"].encode().hex()]
    crc = {}
    for name, digest in expected.items():
        p = code_dir / name
        content = p.read_bytes()
        assert sha(content) == digest
        key = name.removesuffix(".class")
        if key in code:
            crc[key] = crc64(content)
    assert {k: int(v["crc64"], 16) for k, v in observed["classes"].items()} == {
        k: int(value, 16) for k, value in crc.items()}
    report = ET.parse(run / "coverage.xml").getroot()
    assert [item.get("id") for item in report.findall("sessioninfo")] == [b["spec"]["session"]]

    picked = old_post["raw"]["command"][:5]
    command = [*picked, str(runtime), *(str(code_dir / name) for name in sorted(expected))]
    result = subprocess.run(command, capture_output=True, check=False, timeout=35,
                            env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
    assert result.returncode == 0
    out = STORE / "PG40398-p020-single-session-filestore-independent-v1"
    out.mkdir()
    raw_path = out / "raw.tsv"
    raw_path.write_bytes(result.stdout)
    misses, seen, totals = [], set(), Counter()
    for line in result.stdout.decode().splitlines():
        row = line.split("\t")
        if row[0] == "CLASS":
            assert row[1] not in seen and row[1] in names
            seen.add(row[1])
            for item in row[6:]:
                metric, miss, hit = item.split(":")
                totals[metric, "missed"] += int(miss)
                totals[metric, "covered"] += int(hit)
        if row[0] == "METHOD":
            parts = [part for part in row[5:] if int(part.split(":")[1]) > 0]
            if parts:
                misses.append(dict(className=row[1], method=row[2], descriptor=row[3], misses=parts))
    assert seen == names
    gate_canary = [row for row in misses if row["className"] == "dev/codex/schubert/characterization/GateCli"
                  and (row["method"], row["descriptor"]) in {
                      ("main", "([Ljava/lang/String;)V"),
                      ("preflight", "(Ljava/nio/file/Path;Ljava/nio/file/Path;)V")}]
    counters = {kind: {key: totals[kind, key] for key in ("covered", "missed")}
                for kind in ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")}
    dump(out / "manifest.json", dict(
        actualExit=0, exactToolSource=b["previousToolSource"], executedWrapperSource=b["source"],
        productionCore=b["productionCore"], tests=209, requiredExistingTests=208, toolCaseBindingsNew=1,
        originalCaseName=fresh[1], failed=0, errors=0, skipped=0, notRun=0, productTests=0,
        physicalClasses=17, positivePhysicalCrc=crc, naturalNoCode=sorted(no_code),
        session=b["spec"]["session"], oldExecMerged=False, manualCoverageExclusions=0,
        livePreflightTwoMissingMethodsRemaining=gate_canary,
        rawMissedMethods=misses, rawCounters=counters, toolFour100=all(totals[k, "missed"] == 0
            for k in ("LINE", "METHOD", "CLASS", "BRANCH")),
        cwdAdmission=t["admission"], actualChr=False, actualBackendActions=0, formalDelta=0,
        whole451Accepted=False, sourceEvidence=list(map(pin, (begin, terminal, attestation, old_xml, runtime,
             raw_path, run / "cases.json", run / "coverage.xml"))),
        command=command, terminalAtUTC=COMMON["timestamp"]()))
    print(pin(out / "manifest.json"), counters, len(gate_canary))


if __name__ == "__main__":
    main()
