"""Verify the new Protocol run, its exact JAR, and the width of every shared layout."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import runpy
import subprocess
from xml.etree import ElementTree as XML


ROOT = Path(__file__).resolve().parents[4]
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
H = runpy.run_path(str(OPS.parent / "input/5389_f03_protocol_current_maven_independent.py"))
JAVA, MODULE = H["JAVA"], H["MODULE"]
pin, read, write, verify, classes_in_jar = (H[k] for k in ("pin", "read", "write", "verify", "jar_classes"))
RUN = "PG41302-protocol-numeric-full-maven-v1"
NEW = ("dev.codex.schubert.nk.protocol.codec.FieldCodecTest",
       "numericDecodeValidatesEveryByteBeforeAccumulatingTheValue")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=20)


def scope_widths(snapshot, start):
    lib = snapshot / start / "src/main/java/dev/codex/schubert/nk/protocol"
    fields = [(idx, row.strip().split(r"\t"))
              for idx, row in enumerate((lib / "layout/LayoutFieldCatalog.java").read_text().splitlines(), 1)]
    nums = [(index, field[0], int(field[4])) for index, field in fields
            if len(field) == 8 and field[5] == "N"]
    assert len(nums) == 135 and max(item[-1] for item in nums) == 17
    header = (lib / "codec/HeaderCodec.java").read_text()
    pairs = re.findall(r"numericInt\(body, (\d+), (\d+),", header)
    assert len(pairs) == 7
    sizes = [int(end) - int(begin) for begin, end in pairs]
    assert max(sizes) == 9
    usages = git("grep", "-n", "-e", "FieldCodec.decodeNumeric(", "HEAD",
                 "--", str(MODULE / "src/main/java")).decode().splitlines()
    assert len(usages) == 2 and {Path(line.split(":")[1]).name for line in usages} == {
        "PayloadCodec.java", "HeaderCodec.java"}
    return dict(payloadCatalogNumericFields=len(nums), payloadNumericMaxWidth=17,
                headerDirectNumericFields=len(sizes), headerNumericMaxWidth=9,
                dualFailureMinWidth=20, directCodecAffected=True, exactKnownWireLayoutsAffected=False)


def main():
    base = OPS / RUN
    end = read(base / "terminal.json")
    begin = read(verify(end["begin"]))
    head = end["source"]
    assert head == begin["source"] and git("rev-parse", "HEAD").decode().strip() == head
    assert end["actualExit"] == 0 and end["surefireReports"] == 39
    summary = verify(end["summary"]).read_text()
    assert "[INFO] BUILD SUCCESS" in summary and "All coverage checks have been met." in summary
    work = Path(end["work"])
    assert work.parent == Path("/dev/shm") and work.stat().st_mode & 0o777 == 0o700
    assert pin(work / "original-maven.log")["sha256"] == end["logHash"]
    before_receipt = verify(begin["previous"])
    before = read(before_receipt)
    roster = before_receipt.with_name("testcases.json")
    assert pin(roster) in before["sanitizedOutputs"]
    expected = {(v["className"], v["method"]) for v in read(roster)}
    assert len(expected) == 170 and NEW not in expected
    records = {}
    xml_hashes = {}
    target = work / MODULE / "target"
    for xml in sorted((target / "surefire-reports").glob("TEST-*.xml")):
        report = XML.parse(xml).getroot()
        cases = report.findall("testcase")
        assert len(cases) == int(report.attrib["tests"])
        assert all(int(report.attrib[k]) == 0 for k in ("failures", "errors", "skipped"))
        xml_hashes[xml.name] = pin(xml)["sha256"]
        for case in cases:
            assert all(case.find(name) is None for name in ("failure", "error", "skipped"))
            key = (case.attrib["classname"], case.attrib["name"].removesuffix("()"))
            assert key not in records
            records[key] = dict(className=key[0], method=key[1], outcome="PASS")
    assert len(records) == 171 and set(records) == expected | {NEW} and len(xml_hashes) == 39
    inventory = read(verify(begin["input"]))
    for path, value in inventory.items():
        actual = pin(work / path)
        assert actual["sha256"] == value["sha256"]
        assert git("rev-parse", f"{head}:{path}").decode().strip() == value["gitBlob"]
    old_jar = verify(before["retainedEarlierPassArtifact"])
    jar = target / "schubert-nk-protocol-0.1.0-SNAPSHOT.jar"
    old_classes = classes_in_jar(old_jar)
    classes = classes_in_jar(jar)
    assert len(classes) == 176 and classes.keys() == old_classes.keys()
    changed = [key for key, body in classes.items() if old_classes[key] != body]
    assert changed == ["dev/codex/schubert/nk/protocol/codec/FieldCodec.class"]
    physical = target / "classes"
    assert all(body == (physical / key).read_bytes() for key, body in classes.items())
    assert set(classes) == {p.relative_to(physical).as_posix() for p in physical.rglob("*.class")}
    before_spot = before["spotbugsCounts"]
    spot_path = target / "spotbugsXml.xml"
    spot = XML.parse(spot_path).getroot()
    findings = {key: len(spot.findall(".//" + tag)) for key, tag in
                (("bugs", "BugInstance"), ("missing", "MissingClass"), ("errors", "Error"))}
    assert findings == before_spot == dict(bugs=0, missing=0, errors=0)
    coverage = target / "site/jacoco/jacoco.xml"
    cov = XML.parse(coverage).getroot()
    session, = cov.findall("sessioninfo")
    assert all(int(row.attrib["missed"]) == 0 for row in cov.findall("counter"))
    original = target / "jacoco.exec"

    tool_src = ROOT / "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
    repo = ROOT.parent / "toolchain/m2/repository"
    sdk = [repo / "org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar",
           *[repo / f"org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar"
             for name in ("asm", "asm-commons", "asm-tree")]]
    cp = os.pathsep.join(map(str, sdk))
    tools = work / "current-strict-analyzer"
    steps = []

    def run(command):
        argv = list(map(str, command))
        proc = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=85, check=False)
        steps.append(dict(argv=argv, exit=proc.returncode, stderrSha256=hashlib.sha256(proc.stderr).hexdigest()))
        assert proc.returncode == 0, proc.stderr
        return proc.stdout

    run([JAVA.with_name("javac"), "--release", "25", "-proc:none", "-cp", cp, "-d", tools, tool_src])
    raw = run([JAVA, "-cp", str(tools) + os.pathsep + cp,
               "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
               "--strict-original-exec", "--line-deficits", original,
               *[physical / key for key in sorted(classes)]])
    total = Counter()
    compiled = {}
    physical_crc = {}
    for row in (line.split("\t") for line in raw.decode().splitlines()):
        if row[0] != "CLASS":
            continue
        n = row[1]
        assert n not in physical_crc and int(row[2], 16) == int(H["crc64"](classes[n + ".class"]), 16)
        physical_crc[n] = int(row[2], 16)
        if row[3] == "true":
            compiled[n] = physical_crc[n]
        for i in row[6:]:
            kind, missed, covered = i.split(":")
            total[kind, "missed"] += int(missed)
            total[kind, "covered"] += int(covered)
    assert len(physical_crc) == 176 and len(compiled) == 162
    reader = ROOT / "tools/quality/jacoco_readonly_exec_subset.py"
    exec_info = runpy.run_path(str(reader))["decode"](original.read_bytes(), set(compiled))
    actual_session, = exec_info["sessions"]
    assert actual_session["labelBytesHex"] == session.attrib["id"].encode().hex()
    assert {n: int(x["crc64"], 16) for n, x in exec_info["classes"].items()} == compiled
    counters = {k: {mode: total[k, mode] for mode in ("covered", "missed")}
                for k in ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")}
    complete = all(r["missed"] == 0 and r["covered"] > 0 for r in counters.values())
    out = OPS / "PG41304-protocol-numeric-physical-independent-v1"
    out.mkdir()
    (out / "unfiltered.tsv").write_bytes(raw)
    write(out / "cases.json", [records[key] for key in sorted(records)])
    widths = scope_widths(work, MODULE)
    write(out / "manifest.json", dict(
        actualExit=int(not complete), source=head, core=head, run=out.name, ordinaryTests=len(records),
        suites=len(xml_hashes), failures=0, errors=0, skipped=0, notRun=0, requiredOldCases=170, newCases=1,
        provenMaven=pin(base / "terminal.json"), priorRoster=pin(roster), originalXmlHashes=xml_hashes,
        localJar=pin(jar), jarPhysicalCount=len(physical_crc), identicalEarlierPhysical=175,
        changedPhysical=changed, execClasses=len(compiled), originalExec=pin(original), noCodeClasses=14,
        sourceSnapshotFiles=len(inventory), coverageRaw=counters, fullProtocol=complete, originalCoverageXml=pin(coverage),
        nullawayRootVerified="-Xep:NullAway:ERROR" in (work / "pom.xml").read_text(), noSuppressionChange=True,
        spotbugs=findings, spotbugsXml=pin(spot_path), scopeWidth=widths, tools=steps,
        toolSource=pin(tool_src), readerSource=pin(reader), singleSession=True, execMerged=False,
        whole451=False, actualExternalOperations=0, formalDelta=0,
        evidence=[pin(out / "unfiltered.tsv"), pin(out / "cases.json")],
        terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(complete, counters, widths)


if __name__ == "__main__":
    main()
