"""Explain the mapper's measured raw gaps from its exact two retained binaries."""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


group = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1364_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
raw, status = [json.loads(Path(ref["path"]).read_bytes()) for ref in refs[1:3]]
assert raw["source"] == status["source"] == ctx["productionCoreMain"]
rows = {row["name"].rsplit("/", 1)[-1]: row for row in raw["raw"]}
parts = {}
tool = Path("../toolchain/jdk-25.0.4/bin/javap")
for name in ("WebResultMapper", "WebResultMapper$1"):
    detail, = (entry for entry in raw["targetClasses"] if Path(entry["path"]).stem == name)
    assert pin(Path(detail["path"])) == detail and rows[name]["crcMatched"]
    command = [str(tool), "-p", "-c", detail["path"]]
    result = subprocess.run(command, capture_output=True, text=True, timeout=15, check=True)
    parts[name] = dict(input=detail, command=command, exitCode=result.returncode, javap=result.stdout,
                       historicalRawCounters=rows[name]["counters"])

mapper = parts["WebResultMapper"]["javap"]
assert "tableswitch" in mapper
target, = re.findall(r"default:\s+(\d+)", mapper)
assert re.search(rf"^\s*{target}:\s+new\s+.*java/lang/MatchException", mapper, re.MULTILINE)
assist = parts["WebResultMapper$1"]["javap"].split("Exception table:", maxsplit=1)[1]
handlers = re.findall(r"^\s*\d+\s+\d+\s+(\d+)\s+Class java/lang/NoSuchFieldError$", assist, re.MULTILINE)
assert len(set(handlers)) == len(handlers) == 12
for name, expected in [("WebResultMapper", {"INSTRUCTION": 6, "BRANCH": 1}),
                       ("WebResultMapper$1", {"INSTRUCTION": 12})]:
    actual = {counter["kind"]: counter["missed"] for counter in parts[name]["historicalRawCounters"]}
    assert all(actual[key] == value for key, value in expected.items())
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
result = dict(actualExit=0, source=ctx["productionCoreMain"], startEvent=group["eventId"],
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), originals=refs[1:],
              inspected=list(parts.values()), switchDefaultOffset=int(target), enumMissingFieldHandlerCount=12,
              rawCoverageWaived=False, testScopeChanged=False, productSourceChanged=False,
              otherRunCombined=False, unitReruns=0, actualExternalActions=0, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
