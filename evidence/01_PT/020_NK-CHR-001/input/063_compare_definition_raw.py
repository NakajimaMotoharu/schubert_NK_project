"""Check the two exact comparator classes from a single original exec."""

import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("061_compare_definition_contract.py")))
ROOT, TOOLS, WORK, EVIDENCE = (H[name] for name in ("ROOT", "TOOLS", "WORK", "EVIDENCE"))
dump, pin, utc = (H[name] for name in ("dump", "pin", "utc"))


def main():
    by_run = lambda name: EVIDENCE / name / "manifest.json"
    raw_path = by_run("PG41274-p020-comparison-definitions-qualified-v1")
    green_path = by_run("PG41270-p020-comparison-definitions-green-v1")
    static_path = by_run("PG41272-p020-comparison-definitions-independent-v1")
    raw, green, static = [json.loads(path.read_bytes()) for path in (raw_path, green_path, static_path)]
    assert raw["source"] == green["source"] == static["source"]
    assert static["greenManifestSha256"] == pin(green_path)
    assert raw["testExit"] == 0 and raw["tests"] == dict(tests=75, failures=0, errors=0, skipped=0)
    assert {name: raw["physical"][name] for name in green["physical"]} == green["physical"]
    assert len(raw["physical"]) == len(green["physical"]) + 1
    work = WORK / raw["run"]
    original = work / "jacoco.exec"
    assert pin(original) == raw["rawExecSha256"]
    assert pin(work / "reports/TEST-junit-jupiter.xml") == raw["rawXmlSha256"]
    class_names = static["comparedPhysical"]
    assert len(class_names) == 2
    classes = [work / "classes" / name for name in class_names]
    assert [pin(path) for path in classes] == [raw["physical"][name] for name in class_names]

    crc_tool = (ROOT / "evidence/01_PT/018_NK-OPS-001/input/5593_p01808_original_name_binding.py")
    crc = runpy.run_path(str(crc_tool))["class_id"]
    reader = ROOT / "tools/quality/jacoco_readonly_exec_subset.py"
    decode = runpy.run_path(str(reader))["decode"]
    probes = decode(original.read_bytes(), {name.removesuffix(".class") for name in class_names})
    for name, bytecode in zip(class_names, classes, strict=True):
        assert crc(bytecode.read_bytes()) == int(probes["classes"][name.removesuffix(".class")]["crc64"], 16)

    java = TOOLS / "jdk-25.0.4/bin"
    repo = TOOLS / "m2/repository"
    deps = [repo / "org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"]
    deps += [repo / "org/ow2/asm" / module / "9.10.1" / (module + "-9.10.1.jar")
             for module in ("asm", "asm-commons", "asm-tree")]
    tool = ROOT / "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
    classpath = os.pathsep.join(map(str, deps))
    steps = []

    def run(argv):
        args = list(map(str, argv))
        result = subprocess.run(args, cwd=ROOT, capture_output=True, check=False, timeout=90)
        steps.append(dict(argv=args, exitCode=result.returncode,
                          stderrSha256=hashlib.sha256(result.stderr).hexdigest()))
        assert result.returncode == 0, result.stderr
        return result.stdout

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-comparison-") as temp:
        run([java / "javac", "--release", "25", "-proc:none", "-cp", classpath, "-d", temp, tool])
        report = run([java / "java", "-cp", temp + os.pathsep + classpath,
                      "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                      "--strict-original-exec", "--line-deficits", original, *classes])
    totals = {}
    missing = {}
    records = [line.split("\t") for line in report.decode().splitlines() if line.startswith("CLASS\t")]
    assert len(records) == 2 and {line[1] + ".class" for line in records} == set(class_names)
    for row in records:
        for counter in row[6:]:
            name, misses, hits = counter.split(":")
            totals[name] = totals.get(name, 0) + int(hits)
            missing[name] = missing.get(name, 0) + int(misses)
    out = EVIDENCE / "PG41276-p020-comparison-definitions-qualified-raw-v1"
    out.mkdir()
    (out / "unfiltered.tsv").write_bytes(report)
    dump(out / "manifest.json", dict(
        run=out.name, source=raw["source"], qualifiedManifestSha256=pin(raw_path),
        staticManifestSha256=pin(static_path), originalExecSha256=pin(original),
        scopesCompared=class_names, crcCount=len(classes), originalSessionCount=len(probes["sessions"]),
        originalClassRecords=probes["totalClassRecords"], wholeTypeInstrumentedTotals=totals,
        wholeTypeInstrumentedMisses=missing, countsAreFull=not any(missing.values()),
        staticPhysicalUnchanged=True, tsvSha256=pin(out / "unfiltered.tsv"), toolSha256=pin(tool),
        readerSha256=pin(reader), steps=steps, terminalAtUTC=utc(), exclusions=0,
        execMerged=False, whole451=False, actualChr=False, formalDelta=0))
    print({"covered": totals, "missed": missing})


if __name__ == "__main__":
    main()
