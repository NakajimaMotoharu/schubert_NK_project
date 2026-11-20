"""Independently measure the API memory handler from its one retained execution."""
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


root = Path("evidence/01_PT/018_NK-OPS-001/evidence")
path = next(root.glob("PG40942-*-v2/manifest.json"))
d = json.loads(path.read_bytes())
assert d["actualExit"] == 0 and d["counts"] == dict(tests=23, errors=0, failures=0, skipped=0)
assert d["heldInitializationsObserved"] == 0 and len(d["actualCases"]) == 23
scope = d["coverage"]
exec_file, target, xml = [Path(scope[key]["path"]) for key in ("exec", "target", "xml")]
assert [pin(p) for p in (exec_file, target, xml)] == [scope[key] for key in ("exec", "target", "xml")]
assert [row.attrib["id"] for row in ET.parse(xml).getroot().findall("sessioninfo")] == [scope["session"]]
previous_path = next(root.glob("PG40906-*/manifest.json"))
previous = json.loads(previous_path.read_bytes())
reference = json.loads(Path(previous["before"]["path"]).read_bytes())
measurement = "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
archive = subprocess.check_output(["git", "show", "c5674055a6:" + measurement], timeout=15)
assert hashlib.sha256(archive).hexdigest() == reference["unfilteredToolSha256"]
old_compile = previous["compileCommand"]
libs = old_compile[old_compile.index("-cp") + 1]
with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40942-raw-") as tmp:
    source = Path(tmp) / "UnfilteredCodeMeasurement.java"
    source.write_bytes(archive)
    cc = [*old_compile[:old_compile.index("-d")], "-d", tmp, str(source)]
    subprocess.run(cc, check=True, capture_output=True, timeout=40)
    java, _, _, launcher = previous["rawCommand"][:4]
    cmd = [java, "-cp", f"{tmp}:{libs}", launcher, str(exec_file), str(target)]
    raw = subprocess.run(cmd, check=True, capture_output=True, timeout=40)
row, = (line.split("\t") for line in raw.stdout.decode().splitlines() if line.startswith("CLASS\t"))
assert row[1] == "dev/codex/schubert/nk/api/monitoring/ApiMetricHttpHandler" and row[3] == "true"
table = path.with_name("unfiltered.tsv")
table.write_bytes(raw.stdout)
counters = [dict(name=key, missed=int(missed), covered=int(covered))
            for key, missed, covered in (cell.split(":") for cell in row[6:])]
result = dict(actualExit=0, source=d["source"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              parentUnit=pin(path), target=pin(target), crc64=row[2], session=scope["session"],
              retainedExec=pin(exec_file), compileCommand=cc, rawCommand=cmd, unfiltered=pin(table),
              counters=counters, productReruns=0, whole451=False, formalDelta=0)
path.with_name("raw-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
print(counters)
