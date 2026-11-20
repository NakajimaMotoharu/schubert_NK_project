"""Reconcile one local CHR tool session with the admitted packaging and raw counters."""

from collections import Counter
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("065_current_216_local.py")))
ROOT, TOOLS, MODULE, OPS, RUN = (H[key] for key in ("ROOT", "TOOLS", "MODULE", "OPS", "RUN"))
dump, pin, utc, read, reference = (H[key] for key in ("dump", "pin", "utc", "read", "reference"))


def main():
    manifest = OPS / RUN / "manifest.json"
    unit = read(manifest)
    assert unit["exit"] == 0 and not unit["priorExecMerged"]
    assert unit["counts"] == dict(tests=216, failures=0, errors=0, skipped=0)
    for key in ("rawXml", "originalExec", "actual", "roster", "jar", "sourcePreparation"):
        assert reference(Path(unit[key]["path"])) == unit[key]
    pack = read(Path(unit["sourcePreparation"]["path"]))
    assert pack["toolSource"] == unit["packagedSource"]
    assert pack["physical"] == unit["actualPhysical"] and unit["exactPackagedClasses"] == 17
    classes = Path(unit["snapshot"]) / MODULE / "target/classes"
    physical = {p.relative_to(classes).as_posix().removesuffix(".class"): p
                for p in classes.rglob("*.class")}
    assert {name + ".class": pin(path) for name, path in physical.items()} == unit["actualPhysical"]
    old = read(next(OPS.glob("PG41128-*/manifest.json")))
    no_code = set(old["naturalNoCodeTypes"])
    recorded = set(physical) - no_code
    assert len(recorded) == 12 and len(no_code) == 5
    library = ROOT / "tools/quality/jacoco_readonly_exec_subset.py"
    decode = runpy.run_path(str(library))["decode"]
    crc = runpy.run_path(str(OPS.parent / "input/5593_p01808_original_name_binding.py"))["class_id"]
    original = Path(unit["originalExec"]["path"])
    session = decode(original.read_bytes(), recorded)
    assert [r["labelBytesHex"] for r in session["sessions"]] == [unit["session"].encode().hex()]
    assert {name: int(row["crc64"], 16) for name, row in session["classes"].items()} == {
        name: crc(physical[name].read_bytes()) for name in recorded}

    repository = TOOLS / "m2/repository"
    deps = [repository / "org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"]
    deps += [repository / f"org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar"
             for name in ("asm", "asm-commons", "asm-tree")]
    classpath = os.pathsep.join(map(str, deps))
    jdk = TOOLS / "jdk-25.0.4/bin"
    tool = ROOT / "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
    steps = []

    def execute(argv):
        args = list(map(str, argv))
        process = subprocess.run(args, cwd=ROOT, capture_output=True, check=False, timeout=90)
        steps.append(dict(argv=args, exitCode=process.returncode))
        assert process.returncode == 0, process.stderr
        return process.stdout

    with TemporaryDirectory(dir="/dev/shm", prefix="chr-216-raw-") as temp:
        execute([jdk / "javac", "--release", "25", "-proc:none", "-cp", classpath, "-d", temp, tool])
        report = execute([jdk / "java", "-cp", temp + os.pathsep + classpath,
                          "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                          "--strict-original-exec", "--line-deficits", original,
                          *[physical[name] for name in sorted(physical)]])
    counters = Counter()
    covered = set()
    for line in report.decode().splitlines():
        row = line.split("\t")
        if row[0] == "CLASS":
            assert (row[3] == "true") == (row[1] in recorded)
            assert row[1] not in covered
            covered.add(row[1])
            for field in row[6:]:
                kind, missed, hit = field.split(":")
                counters[kind, "missed"] += int(missed)
                counters[kind, "covered"] += int(hit)
    assert covered == set(physical)
    results = {kind: {n: counters[kind, n] for n in ("covered", "missed")}
               for kind in ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")}
    raw_all = all(row["missed"] == 0 and row["covered"] > 0 for row in results.values())
    out = OPS / "PG41282-p020-current-216-raw-independent-v1"
    out.mkdir()
    (out / "unfiltered.tsv").write_bytes(report)
    dump(out / "manifest.json", dict(
        run=out.name, testedSource=unit["testedSource"], packageSource=pack["toolSource"],
        productionCore=pack["productionCore"], unit=reference(manifest),
        terminalAtUTC=utc(), testCounts=unit["counts"], suites=len(unit["selectors"]),
        notRunOutsideSelectedScope=1, rawCounters=results, rawAll=raw_all,
        crcVerified=len(recorded), physicallyVerified=len(physical),
        naturalNoCodeTypes=sorted(no_code), sessionCount=len(session["sessions"]),
        reader=reference(library), tool=reference(tool), steps=steps,
        rawOutput=reference(out / "unfiltered.tsv"), exclusions=0, oldExecMerged=False,
        actualFileStore=False, actualChr=False, whole451=False, formalDelta=0))
    print(raw_all, results)


if __name__ == "__main__":
    main()
