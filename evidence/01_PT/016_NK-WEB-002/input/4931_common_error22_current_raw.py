"""Measure the exact Web error class bytes from the retained current 22-test execution."""
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


root = Path("evidence/01_PT")
base = next((root / "016_NK-WEB-002/evidence").glob("PG40932-*/manifest.json"))
before = json.loads(base.read_bytes())
assert before["actualExit"] == before["unitExit"] == before["coverageExit"] == 0
assert before["counts"] == dict(tests=22, failures=0, errors=0, skipped=0)
assert before["classInitHeldHits"] == 0
exec_file = Path(before["execData"]["path"])
assert pin(exec_file) == before["execData"]
default_xml = Path(before["coverageXml"]["path"])
assert pin(default_xml) == before["coverageXml"]
assert ET.parse(default_xml).getroot().find("sessioninfo").attrib["id"] == before["session"]
ops = root / "018_NK-OPS-001/evidence"
old_prepare = json.loads(next(ops.glob("PG28014-*/manifest.json")).read_bytes())
inputs = before["coverageCommand"]
classes = [Path(inputs[index + 1]) for index, value in enumerate(inputs) if value == "--classfiles"]
classes.append(exec_file.parent / "products/dev/codex/schubert/nk/web/error/WebResultMapper$1.class")
expected = {}
for cls in classes:
    index = cls.parts.index("dev")
    relative = "/".join(cls.parts[index:])
    assert pin(cls)["sha256"] == old_prepare["physicalClassHashes"][relative]
    expected[relative.removesuffix(".class")] = pin(cls)
assert len(expected) == 7
baseline = next(ops.glob("PG40906-*/manifest.json"))
raw_reference = json.loads(baseline.read_bytes())
raw_path = "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
tool = subprocess.check_output(["git", "show", "c5674055a6:" + raw_path], timeout=15)
previous = json.loads(Path(raw_reference["before"]["path"]).read_bytes())
assert sha(tool) == previous["unfilteredToolSha256"]
compiler = raw_reference["compileCommand"]
libs = compiler[compiler.index("-cp") + 1]
with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40932-raw-") as temp:
    place = Path(temp)
    code = place / "UnfilteredCodeMeasurement.java"
    code.write_bytes(tool)
    compile_cmd = [*compiler[:compiler.index("-d")], "-d", temp, str(code)]
    compile_result = subprocess.run(compile_cmd, capture_output=True, check=True, timeout=30)
    reference = raw_reference["rawCommand"]
    command = [reference[0], "-cp", f"{temp}:{libs}", reference[3], str(exec_file),
               *map(str, classes)]
    run = subprocess.run(command, capture_output=True, check=True, timeout=45)
    rows = []
    for text in run.stdout.decode().splitlines():
        line = text.split("\t")
        if line[0] != "CLASS":
            continue
        counters = []
        for cell in line[6:]:
            kind, missed, covered = cell.split(":")
            counters.append(dict(kind=kind, missed=int(missed), covered=int(covered)))
        rows.append(dict(name=line[1], crc64=line[2], crcMatched=line[3] == "true",
                         counters=counters))
assert {row["name"] for row in rows} == expected.keys() and len(rows) == 7
assert all(row["crcMatched"] for row in rows)
table = base.with_name("unfiltered.tsv")
assert not table.exists()
table.write_bytes(run.stdout)
measured = base.with_name("raw-manifest.json")
assert not measured.exists()
result = dict(actualExit=0, source=before["source"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              retainedExec=before["execData"], session=before["session"], unit=pin(base),
              measurementTool=dict(path=raw_path, revision="c5674055a6", sha256=sha(tool)),
              targetClasses=list(expected.values()), raw=rows, compileCommand=compile_cmd,
              compileExit=compile_result.returncode, rawCommand=command, rawExit=run.returncode,
              allMeasuredCounters100=all(counter["missed"] == 0
                                         for row in rows for counter in row["counters"]),
              coverageTable=pin(table), productReruns=0, newProductTests=0, whole451=False, formalDelta=0)
measured.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
print(result["allMeasuredCounters100"], len(rows), result["actualExit"])
