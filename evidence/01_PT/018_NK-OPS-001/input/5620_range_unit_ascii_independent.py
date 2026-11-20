"""Independently bind the original Range parser exec, physical classes and typed findings."""

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
import json
import os
import runpy


old = runpy.run_path(str(Path(__file__).with_name("5619_range_unit_ascii.py")))
BIN, OPS, DIR, MAIN = (old[key] for key in ("BIN", "OPS", "DIR", "MAIN"))
check, pin, read = (old[key] for key in ("check", "pin", "read"))
crc = runpy.run_path(str(Path(__file__).with_name("5593_p01808_original_name_binding.py")))["class_id"]


def main():
    red, = OPS.glob("PG41202-*/manifest.json")
    green, = OPS.glob("PG41204-*/manifest.json")
    b, g = read(red), read(green)
    assert (b["actualExit"], b["failures"], g["actualExit"], g["tests"]) == (1, 1, 0, 8)
    for original in g["originals"] + g["physical"] + g["testsInput"] + [g["main"], g["junit"]]:
        assert pin(Path(original["path"])) == original
    assert b["main"]["sha256"] != g["main"]["sha256"]
    for file, suffix in (("unit.exec", "unit.exec"), ("jupiter.xml", "TEST-junit-jupiter.xml")):
        original, = [entry for entry in g["originals"] if entry["path"].endswith(suffix)]
        assert pin(green.parent / file)["sha256"] == original["sha256"]
    physical = [Path(entry["path"]) for entry in g["physical"]]
    core = Path("../toolchain/m2/repository").resolve()
    jacoco = core / "org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"
    asm = [core / f"org/ow2/asm/{artifact}/9.10.1/{artifact}-9.10.1.jar"
           for artifact in ("asm", "asm-commons", "asm-tree")]
    classpath = os.pathsep.join(map(str, [jacoco, *asm]))
    measure = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
    out = OPS / "PG41206-range-unit-ascii-independent-v1"
    out.mkdir()
    report = out / "spotbugs.xml"
    stages = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-range-receipt-") as temp:
        scratch = Path(temp)
        stages["compileMeasure"], made = check([BIN/"javac", "--release", "25", "-proc:none",
                                                 "-cp", classpath, "-d", scratch, measure])
        assert made.returncode == 0, made.stderr
        stages["unfiltered"], analysis = check([BIN/"java", "-cp", f"{scratch}{os.pathsep}{classpath}",
            "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
            "--strict-original-exec", green.parent/"unit.exec", *physical])
        (out/"coverage.stdout").write_bytes(analysis.stdout)
        (out/"coverage.stderr").write_bytes(analysis.stderr)
        assert analysis.returncode == 0, analysis.stderr
        measured = {}
        for line in analysis.stdout.decode().splitlines():
            fields = line.split("\t")
            if fields[0] == "CLASS":
                assert fields[1] not in measured
                file, = [p for p in physical if p.stem == Path(fields[1]).name]
                ident = crc(file.read_bytes())
                assert fields[2] == f"{ident:016x}"
                parts = (field.split(":") for field in fields[6:])
                measured[fields[1]] = dict(id=fields[2], present=fields[3] == "true",
                    counters={key: dict(missed=int(miss), covered=int(hit)) for key, miss, hit in parts})
        assert len(measured) == len(physical)
        for file in physical:
            dst = scratch / DIR / file.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(file.read_bytes())
        junit = g["junit"]["path"]
        test_source = g["testsInput"][0]["path"]
        stages["compileNewTest"], compiled = check([BIN/"javac", "--release", "25", "-g",
            "-Xlint:all", "-Werror", "-proc:none", "-cp", f"{scratch}{os.pathsep}{junit}",
            "-d", scratch, test_source])
        assert compiled.returncode == 0, compiled.stderr
        test_class = scratch/DIR/"HttpByteRangeUnitTokenTest.class"
        old_static, = OPS.glob("PG41162-*/manifest.json")
        command = read(old_static)["stagedStatic"]["spotbugs"]["command"][:13]
        assert command[4] == "edu.umd.cs.findbugs.FindBugs2" and command[9:12:2] == ["-auxclasspath", "-output"]
        command[10] = f"{scratch}{os.pathsep}{junit}"
        command[12] = report
        targets = [scratch/DIR/p.name for p in physical] + [test_class]
        class_hashes = {target.name: pin(target)["sha256"] for target in targets}
        stages["spotbugs"], spot = check([*command, *targets])
        assert spot.returncode in (0, 1), spot.stderr
    summary = {
        key: {category: sum(rows["counters"][key][category] for rows in measured.values())
              for category in ("missed", "covered")}
        for key in ("LINE", "METHOD", "CLASS", "BRANCH", "INSTRUCTION")
    }
    tree = ElementTree.parse(report).getroot()
    findings = [{"type": bug.get("type"), "owner": bug.find("Class").get("classname")}
                for bug in tree.findall("BugInstance")]
    missing = len(tree.findall(".//MissingClass"))
    errors = len(tree.findall(".//Error"))
    data = dict(run=out.name, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                actualExit=0 if not findings and missing == errors == spot.returncode == 0 else 1,
                source=g["source"], prior=pin(red), unit=pin(green), newProductTestInvocations=0,
                checkedProofs=list(map(pin, (measure, jacoco, *asm, old_static))),
                sourceEntrypoint=pin(MAIN), stages=stages, typedPhysicalHashes=class_hashes,
                findings=findings, missing=missing, errors=errors, counters=summary, classes=measured,
                noCounters=[name for name, row in measured.items()
                            if not any(sum(counts.values()) for counts in row["counters"].values())],
                manualExclusions=0, output=list(map(pin, (report, out/"coverage.stdout", out/"coverage.stderr"))),
                whole451=False, formalDelta=0)
    path = out/"manifest.json"
    with path.open("x") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(path), summary, findings, missing, errors)
    return data["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
