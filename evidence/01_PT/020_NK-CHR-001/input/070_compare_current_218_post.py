"""Check the original local 218-tool execution and its Maven package without rerunning tests."""

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


H = runpy.run_path(str(Path(__file__).with_name("069_compare_current_218_local.py")))
ROOT, TOOLS, OPS, WORK, MODULE, EVIDENCE = (H[k] for k in ("ROOT", "TOOLS", "OPS", "WORK", "MODULE", "EVIDENCE"))
load, pin, report = (H[k] for k in ("load", "pin", "report"))


def main():
    unit_path = EVIDENCE / H["RUN"] / "manifest.json"
    unit = load(unit_path)
    assert unit["actualExit"] == 0 and unit["testedTests"] == {
        "tests": 218, "failures": 0, "errors": 0, "skipped": 0
    }
    for name in ("originalExec", "originalXml", "package"):
        assert pin(Path(unit[name]["path"])) == unit[name]
    root = Path(unit["package"]["path"]).parent / "classes"
    classes = {p.relative_to(root).as_posix(): p for p in root.rglob("*.class")}
    assert len(classes) == 17 and {k: pin(v)["sha256"] for k, v in classes.items()} == unit["physical"]
    old_qualified, = OPS.glob("PG41282-*/manifest.json")
    old = load(old_qualified)
    original = Path(unit["originalExec"]["path"])
    natural = set(old["naturalNoCodeTypes"])
    recorded = {name.removesuffix(".class") for name in classes} - natural
    decoder = ROOT / "tools/quality/jacoco_readonly_exec_subset.py"
    decode = runpy.run_path(str(decoder))["decode"]
    crc = runpy.run_path(str(OPS.parent / "input/5593_p01808_original_name_binding.py"))["class_id"]
    session = decode(original.read_bytes(), recorded)
    assert [row["labelBytesHex"] for row in session["sessions"]] == [unit["run"].encode().hex()]
    assert len(recorded) == 12
    assert all(crc(classes[key + ".class"].read_bytes()) == int(val["crc64"], 16)
               for key, val in session["classes"].items())
    repository = TOOLS / "m2/repository"
    jars = [repository / "org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"]
    jars += [repository / f"org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar"
             for name in ("asm", "asm-commons", "asm-tree")]
    jdk = TOOLS / "jdk-25.0.4/bin"
    cp = os.pathsep.join(map(str, jars))
    tool = ROOT / "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
    trace = []

    def execute(argv):
        command = list(map(str, argv))
        run = subprocess.run(command, cwd=ROOT, capture_output=True, check=False, timeout=90)
        trace.append({"argv": command, "exit": run.returncode})
        assert run.returncode == 0, run.stderr[-400:]
        return run.stdout

    previous, = OPS.glob("PG41280-*/manifest.json")
    old_jar = Path(load(previous)["jar"]["path"])
    old_dir = old_jar.parent / "classes"
    diffs = {}
    for rel in unit["changedFromEarlierPackage"]:
        changed = execute([jdk / "javap", "-p", "-s", "-c", classes[rel]])
        old_class = execute([jdk / "javap", "-p", "-s", "-c", old_dir / rel])
        diffs[rel] = changed != old_class
    assert sum(diffs.values()) == 2 and all(flag == ("$" not in name) for name, flag in diffs.items())

    with TemporaryDirectory(dir="/dev/shm", prefix="p020-local-218-") as scratch:
        execute([jdk / "javac", "--release", "25", "-proc:none", "-cp", cp, "-d", scratch, tool])
        raw = execute([jdk / "java", "-cp", scratch + os.pathsep + cp,
                       "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                       "--strict-original-exec", "--line-deficits", original, *classes.values()])
    type_rows = {}
    counters = Counter()
    impairments = {}
    for line in raw.decode().splitlines():
        row = line.split("\t")
        if row[0] == "CLASS":
            assert (row[3] == "true") == (row[1] in recorded)
            assert row[1] not in type_rows
            values = {field.split(":")[0]: list(map(int, field.split(":")[1:])) for field in row[6:]}
            type_rows[row[1]] = values
            if any(v[0] for v in values.values()):
                impairments[row[1]] = values
            for metric, (miss, hit) in values.items():
                counters[(metric, "missed")] += miss
                counters[(metric, "hit")] += hit
    assert set(type_rows) == {name.removesuffix(".class") for name in classes}
    comparator = {n: v for n, v in type_rows.items() if "ArtifactComparator" in n}
    assert len(comparator) == 2 and all(c[0] == 0 for row in comparator.values() for c in row.values())
    totals = {k: {"covered": counters[(k, "hit")], "missed": counters[(k, "missed")]}
              for k in ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")}
    out = EVIDENCE / "PG41346-p020-current-218-independent-v1"
    out.mkdir()
    result = out / "unfiltered.tsv"
    result.write_bytes(raw)
    report(out / "manifest.json", {
        "run": out.name, "actualExit": 0, "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
        "source": unit["source"], "productionCore": unit["productionCore"], "unit": pin(unit_path),
        "raw": pin(result), "strictReader": pin(tool), "independentDecoder": pin(decoder),
        "exactPhysical": len(classes), "actualCrcRecords": len(recorded), "originalSessions": 1,
        "bytecodeDiffByChangedType": diffs, "classCounters": {k: v for k, v in type_rows.items() if k in comparator},
        "remainingTypeCounters": impairments, "wholeLocalToolCounters": totals, "commands": trace,
        "heldFileStore": 1, "actualChr": False, "testReruns": 0, "execUnions": 0, "whole451": False,
        "formalDelta": 0,
    })
    print(totals)


if __name__ == "__main__":
    main()
