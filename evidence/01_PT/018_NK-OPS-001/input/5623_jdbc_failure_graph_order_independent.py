"""Measure two JDBC graph methods from one unchanged original exec."""

from datetime import datetime, timezone
import json
from pathlib import Path
import os
import runpy
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


g = runpy.run_path(str(Path(__file__).with_name("5622_jdbc_failure_graph_order.py")))
BIN, OPS, TARGET, TEST_BINARY, check, pin, read = (
    g[key] for key in ("BIN", "OPS", "TARGET", "TEST_BINARY", "check", "pin", "read")
)


def main(fixed):
    unit = OPS/g["FIXED" if fixed else "RUN"]/"manifest.json"
    result = read(unit)
    assert result["actualExit"] == 0 and result["tests"] == 3 and result["oldTestsReplayed"] == 0
    for item in (*result["originalArtifacts"], *result["sealedPhysical"], *result["inputSources"]):
        assert pin(Path(item["path"])) == item
    raw_exec = unit.parent/"unit.exec"
    raw_xml = unit.parent/"jupiter.xml"
    assert pin(raw_exec)["sha256"] == result["originalArtifacts"][1]["sha256"]
    assert pin(raw_xml)["sha256"] == result["originalArtifacts"][2]["sha256"]
    repo = Path("../toolchain/m2/repository").resolve()
    deps = [repo/"org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"] + [
        repo/f"org/ow2/asm/{name}/9.10.1/{name}-9.10.1.jar"
        for name in ("asm", "asm-commons", "asm-tree")
    ]
    cp = os.pathsep.join(map(str, deps))
    measurement = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
    classes = [Path(value["path"]) for value in result["sealedPhysical"]]
    run = "PG41216-f02-ssc461-jdbc-order-fixed-independent-v1" if fixed else "PG41212-f02-ssc461-jdbc-order-independent-v1"
    out = OPS/run
    out.mkdir()
    report = out/"spotbugs.xml"
    static, = OPS.glob("PG41162-*/manifest.json")
    stages = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-jdbc-order-proof-") as temp:
        scratch = Path(temp)
        stages["compileMeasure"], built = check([BIN/"javac", "--release", "25", "-proc:none",
                                                  "-cp", cp, "-d", scratch, measurement])
        assert built.returncode == 0, built.stderr
        stages["unfiltered"], scanned = check([BIN/"java", "-cp", f"{scratch}:{cp}",
            "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
            "--strict-original-exec", raw_exec, *classes])
        (out/"coverage.tsv").write_bytes(scanned.stdout)
        assert scanned.returncode == 0, scanned.stderr
        targets = []
        for owner in TARGET:
            binary, = [path for path in classes if path.stem == Path(owner).name]
            dest = scratch/(owner+".class")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(binary.read_bytes())
            targets.append(dest)
        aux = ":".join(row["path"] for row in result["dependencies"])
        test = result["inputSources"][-1]["path"]
        stages["testTypeCompile"], compiled = check([BIN/"javac", "--release", "25", "-g",
            "-Xlint:all", "-Werror", "-proc:none", "-cp", f"{scratch}:{aux}", "-d", scratch, test])
        assert compiled.returncode == 0, compiled.stderr
        for suffix in ("", "$CountingSql"):
            targets.append(scratch/(TEST_BINARY+suffix+".class"))
        cmd = read(static)["stagedStatic"]["spotbugs"]["command"][:13]
        assert cmd[4] == "edu.umd.cs.findbugs.FindBugs2" and cmd[9:12:2] == ["-auxclasspath", "-output"]
        cmd[10] = f"{scratch}:{aux}"
        cmd[12] = report
        stages["spotbugs"], checked = check([*cmd, *targets])
        assert checked.returncode in (0, 1), checked.stderr
    methods = []
    for line in scanned.stdout.decode().splitlines():
        row = line.split("\t")
        if row[0] == "METHOD" and (row[1] == TARGET[0] or
            (row[1] == TARGET[1] and row[2] == "preserveFatal" and "Function" in row[3])):
            counters = {k: dict(missed=int(miss), covered=int(hit))
                        for k, miss, hit in (field.split(":") for field in row[5:])}
            methods.append(dict(owner=row[1], name=row[2], descriptor=row[3], counters=counters))
    assert len(methods) == 3 and all(
        not entry["counters"][k]["missed"]
        for entry in methods for k in ("LINE", "METHOD", "BRANCH", "INSTRUCTION")
    )
    whole = [line for line in scanned.stdout.decode().splitlines() if line.startswith("CLASS\t")]
    assert len(whole) == 3
    tree = ET.parse(report).getroot()
    findings = [
        dict(rule=item.get("type"), owner=item.find("Class").get("classname"))
        for item in tree.findall("BugInstance")
    ]
    errors, missing = (len(tree.findall(k)) for k in (".//Error", ".//MissingClass"))
    record = dict(run=out.name, actualExit=checked.returncode, source=result["source"],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat(), testsExecuted=0,
                  prior=pin(unit), original=pin(raw_exec), xml=pin(raw_xml), admittedPhysical=len(targets),
                  measurementTool=pin(measurement), measurementDeps=list(map(pin, deps)),
                  methodScope=methods, entireClassCounters=whole, findings=findings,
                  errors=errors, missing=missing, output=list(map(pin, (out/"coverage.tsv", report))),
                  stages=stages, manualExclusions=0, wholeF02=False, whole451=False, formalDelta=0)
    with (out/"manifest.json").open("x") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(out/"manifest.json"), len(methods), findings, errors, missing)
    return record["actualExit"] or bool(findings or missing or errors)


if __name__ == "__main__":
    assert sys.argv[1:] in ([], ["--fixed"])
    raise SystemExit(main(bool(sys.argv[1:])))
