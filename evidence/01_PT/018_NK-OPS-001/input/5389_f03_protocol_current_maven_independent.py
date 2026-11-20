"""Independently qualify the current Protocol Maven run and unfiltered coverage."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree
from zipfile import ZipFile


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
MODULE = Path("src/schubert-nk-protocol")
ROOT = Path.cwd()
JAVA = ROOT.parent / "toolchain/jdk-25.0.4/bin/java"


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def verify(reference):
    path = Path(reference["path"])
    assert pin(path) == reference
    return path


def read(path):
    return json.loads(path.read_bytes())


def write(path, content):
    with path.open("x") as fp:
        json.dump(content, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def crc64(binary):
    assert binary[:4] == bytes.fromhex("cafebabe") and int.from_bytes(binary[6:8], "big") == 69
    value = 0
    for byte in binary:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0xD800000000000000 if value & 1 else 0)
    return f"{value:016x}"


def jar_classes(jar):
    with ZipFile(jar) as zip_file:
        names = [entry.filename for entry in zip_file.infolist() if entry.filename.endswith(".class")]
        assert len(set(names)) == len(names)
        assert all(name.startswith("dev/codex/schubert/nk/protocol/") for name in names)
        return {name: zip_file.read(name) for name in names}


def main():
    end = next(OPS.glob("PG40600-*/terminal.json"))
    terminal = read(end)
    begin = read(verify(terminal["begin"]))
    maven_steps = verify(terminal["filteredMavenSteps"]).read_text()
    source = terminal["source"]
    assert terminal["actualExit"] == 0 and "[INFO] BUILD SUCCESS" in maven_steps
    assert "Compiling 169 source files" in maven_steps
    local = Path(terminal["retainedPrivateDirectory"])
    assert local.parent == Path("/dev/shm") and local.name.startswith("pgpt-current-protocol-full-")
    assert (local.stat().st_mode & 0o777) == 0o700
    assert pin(local / "original-maven.log")["sha256"] == terminal["mavenLogDigest"]
    tracked = read(verify(begin["sourceInventory"]))
    for path, hashes in tracked.items():
        generated = local / path
        assert pin(generated)["sha256"] == hashes["sha256"]
        assert subprocess.check_output(["git", "rev-parse", f"{source}:{path}"], text=True).strip() == hashes["gitBlob"]
    assert "-Xep:NullAway:ERROR" in (local / "pom.xml").read_text()
    historical_path = next(OPS.glob("PG37652-*/manifest.json"))
    previous = read(historical_path)
    original = {(case["classname"], case["name"].removesuffix("()")) for case in previous["cases"]}
    assert len(original) == previous["tests"] == 156 and previous["actualExit"] == 0
    extra = set()
    for path in begin["sourceDelta"]:
        assert path in tracked and path.startswith(str(MODULE / "src/test"))
        java = (local / path).read_text()
        package = re.search(r"(?m)^package ([\w.]+);$", java)[1]
        methods = re.findall(r"(?m)^\s*@Test\s+(?:public\s+)?void ([\w]+)\s*\(", java)
        assert methods
        extra.update((package + "." + Path(path).stem, method) for method in methods)
    assert len(extra) == 14 and not extra & original
    target = local / MODULE / "target"
    cases = {}
    surefire = {}
    parents = Counter()
    for path in sorted((target / "surefire-reports").glob("TEST-*.xml")):
        suite = ElementTree.parse(path).getroot()
        surefire[path.name] = pin(path)["sha256"]
        testcases = suite.findall("testcase")
        assert int(suite.get("tests")) == len(testcases)
        for label in ("errors", "failures", "skipped"):
            parents[label] += int(suite.get(label))
        for case in testcases:
            key = (case.get("classname"), case.get("name").removesuffix("()"))
            assert key not in cases and all(case.find(k) is None for k in ("failure", "error", "skipped"))
            cases[key] = dict(className=key[0], method=key[1], elapsedSeconds=case.get("time"), outcome="PASS")
    assert len(surefire) == terminal["surefireXmlCount"] == 39
    assert set(cases) == original | extra and len(cases) == 170 and not any(parents.values())

    jar = target / "schubert-nk-protocol-0.1.0-SNAPSHOT.jar"
    refs = next(OPS.glob("PG40498-*/manifest.json"))
    earlier_artifact = read(refs)["packagedBuild"]["protocol"]["artifact"]
    retained = jar_classes(verify(earlier_artifact))
    physical = jar_classes(jar)
    assert physical == retained and len(physical) == 176
    directory = target / "classes"
    assert {p.relative_to(directory).as_posix() for p in directory.rglob("*.class")} == set(physical)
    assert all((directory / name).read_bytes() == data for name, data in physical.items())
    class_crc = {name.removesuffix(".class"): crc64(data) for name, data in physical.items()}
    coverage = target / "site/jacoco/jacoco.xml"
    coverage_exec = target / "jacoco.exec"
    junit_coverage = ElementTree.parse(coverage).getroot()
    assert len(junit_coverage.findall("sessioninfo")) == 1
    assert not set(node.get("name") for node in junit_coverage.findall("package/class")) - set(class_crc)
    spotbugs_path = target / "spotbugsXml.xml"
    spotbugs = ElementTree.parse(spotbugs_path).getroot()
    assert spotbugs.tag == "BugCollection" and not (
        spotbugs.findall(".//BugInstance") or spotbugs.findall(".//MissingClass") or spotbugs.findall(".//Error")
    )

    compiled = read(next(OPS.glob("PG31432-*/compile.json")))
    selftests = next(OPS.glob("PG31434-*/manifest.json"))
    assert compiled["actualExit"] == read(selftests)["actualExit"] == 0 and read(selftests)["toolTests"] == 12
    for ref in compiled["dependencies"]:
        verify(ref)
    analyzer_revision = "c5674055a6"
    archived = subprocess.check_output(["git", "show", f"{analyzer_revision}:{compiled['source']['path']}"])
    assert hashlib.sha256(archived).hexdigest() == compiled["source"]["sha256"]
    analyzer_source = local / "UnfilteredCodeMeasurement.java"
    with analyzer_source.open("xb") as fp:
        fp.write(archived)
    retained_bin = Path(compiled["command"][compiled["command"].index("-d") + 1])
    output_bin = local / "verified-analyzer"
    cp = ":".join(dep["path"] for dep in compiled["dependencies"])
    tool_compile = subprocess.run(
        [str(JAVA.with_name("javac")), "-Xlint:all", "-Werror", "--release", "25", "-cp", cp,
         "-d", output_bin, analyzer_source],
        capture_output=True, timeout=60,
    )
    assert tool_compile.returncode == 0 and not tool_compile.stdout and not tool_compile.stderr
    classes = [p.relative_to(output_bin) for p in output_bin.rglob("*.class")]
    assert set(classes) == {p.relative_to(retained_bin) for p in retained_bin.rglob("*.class")}
    assert all((output_bin / path).read_bytes() == (retained_bin / path).read_bytes() for path in classes)
    tool = "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement"
    tool_pin = pin(output_bin / (tool.replace(".", "/") + ".class"))
    cmd = [str(JAVA), "-cp", f"{output_bin}:{cp}",
           tool, str(coverage_exec), *[str(directory / name) for name in sorted(physical)]]
    raw = subprocess.run(cmd, capture_output=True, timeout=60)
    assert raw.returncode == 0 and not raw.stderr
    raw_class = {}
    methods = 0
    code_classes = 0
    counters = {}
    for line in raw.stdout.decode().splitlines():
        row = line.split("\t")
        if row[0] == "METHOD":
            methods += 1
            continue
        assert row[0] == "CLASS" and len(row) == 12 and row[1] not in raw_class
        assert row[2] == class_crc[row[1]]
        raw_class[row[1]] = row[2]
        scope_counters = {}
        for value in row[6:]:
            kind, miss, hit = value.split(":")
            group = counters.setdefault(kind, {"missed": 0, "covered": 0})
            group["missed"] += int(miss)
            group["covered"] += int(hit)
            scope_counters[kind] = int(miss) + int(hit)
        code_classes += int(scope_counters["METHOD"] > 0)
    assert raw_class == class_crc and methods == sum(counters["METHOD"].values())
    assert code_classes == 162 and len(physical) - code_classes == 14
    raw_all = not any(counter["missed"] for counter in counters.values())
    assert all(int(c.get("missed")) == 0 for c in junit_coverage.findall("counter"))

    output = OPS / "PG40602-f03-current-protocol-maven-independent-v1"
    output.mkdir()
    (output / "unfiltered-counters.tsv").write_bytes(raw.stdout)
    write(output / "testcases.json", list(cases.values()))
    write(output / "jvm-crc.json", dict(classes=class_crc, jvmCodeClasses=code_classes, classFiles=len(physical)))
    report = dict(
        actualExit=int(not raw_all), source=source, productionCore=terminal["productionCore"],
        mavenVerify=pin(end), expectedOldCasesBasis=pin(historical_path), addedTestSourceDeclared=len(extra),
        tests=len(cases), suites=len(surefire), failed=0, errors=0, skipped=0, notRun=0, sourceCasesMatch=True,
        surefireOriginalHashes=surefire, currentMavenJar=pin(jar), retainedEarlierPassArtifact=earlier_artifact,
        exactClassBytes=len(physical), naturalNoCode=len(physical)-code_classes, actualJvmMethods=methods,
        originalCoverageXml=pin(coverage), coverageExec=pin(coverage_exec), execSessionCount=1,
        spotbugsXml=pin(spotbugs_path), spotbugsCounts={"bugs": 0, "missing": 0, "errors": 0},
        rawAnalyzer=tool_pin, rawAnalyzerSource=dict(revision=analyzer_revision, **compiled["source"]),
        rawAnalyzerVerifiedBinaryCount=len(classes), rawAnalyzerSelftestsReferenced=pin(selftests),
        rawAnalysisExit=raw.returncode,
        physicalRawCounters=counters, unfilteredCurrentRawFour100=raw_all, safetyHeldClassesRead=0,
        externalSystemOperations=0, oldExecMerged=False, manualExclusions=0, wholeF03Accepted=False,
        whole451Accepted=False, sanitizedOutputs=[pin(p) for p in sorted(output.iterdir())],
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    write(output / "manifest.json", report)
    print(pin(output / "manifest.json"), len(cases), len(surefire), counters)
    return report["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
