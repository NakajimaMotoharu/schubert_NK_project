"""Measure PMD on the exact old and new lookup scope without replaying any product PT."""

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET


HERE = Path(__file__)
RUNNER = runpy.run_path(str(HERE.with_name("5326_f02_group_lookup_upper.py")))
COMMON, STORE, PLAN = (RUNNER[name] for name in ("COMMON", "EVIDENCE", "PLAN"))


def report(path):
    root = ET.parse(path).getroot()
    counts = Counter()
    for node in root:
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "file":
            for finding in node:
                counts[(Path(node.get("name")).name, finding.get("rule"),
                        finding.get("method", ""), (finding.text or "").strip())] += 1
        else:
            raise ValueError("unexpected PMD report processing element " + tag)
    return counts


def main():
    read = RUNNER["read"]
    start = read(next(PLAN.glob("767_*")))
    work = start["values"]
    fixed = read(next(STORE.glob("PG39980-*/manifest.json")))
    rules = read(next(STORE.glob("PG40210-*/begin.json")))
    git, pin = (COMMON[x] for x in ("git", "pin"))
    artifacts = [entry["artifact"] for entry in fixed["jars"].values()]
    assert all(pin(Path(p["path"])) == p for p in artifacts)
    assert all(pin(Path(p["path"])) == p for p in rules["toolAndRulePins"])
    old_unit = read(next(STORE.glob("PG40128-*/begin.json")))
    tool_dependencies = [item for label, item in old_unit["tools"].items()
                         if label.startswith(("jspecify-", "junit-platform-console-standalone-"))]
    assert len(tool_dependencies) == 2
    assert all(pin(Path(p["path"])) == p for p in tool_dependencies)
    new_source = git("rev-parse", "HEAD").decode().strip()
    assert new_source == "cfdedf39165ce5b2a50aaf1ebc884b084309ad9a"
    old_source = work["source"]
    scope = work["oracleReferences"][-2:]
    out = STORE / "PG40310-f02-group-lookup-pmd-delta-v1"
    out.mkdir()
    stages, counts = {}, {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-lookup-pmd-") as temp:
        folder = Path(temp)
        for label, commit in (("before", old_source), ("after", new_source)):
            workdir = folder / label
            workdir.mkdir()
            sources = []
            for row in scope:
                name = row["path"]
                contents = git("show", f"{commit}:{name}")
                if label == "before":
                    assert COMMON["sha"](contents) == row["sha256"]
                path = workdir / Path(name).name
                path.write_bytes(contents)
                sources.append(path)
            files = workdir / "sources.txt"
            files.write_text("".join(str(p) + "\n" for p in sources))
            command = rules["commands"]["pmd"][:]
            java = Path(command[0])
            paths = [p["path"] for p in [*artifacts, *tool_dependencies]]
            paths.append(str(java.parents[1] / "lib/jrt-fs.jar"))
            command[command.index("--file-list") + 1] = files
            command[command.index("--aux-classpath") + 1] = os.pathsep.join(paths)
            destination = (out / (label + ".xml")).resolve()
            command[command.index("--report-file") + 1] = destination
            stages[label] = RUNNER["run"](out.resolve(), label, command, workdir,
                                           {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
            counts[label] = report(destination)
    delta = counts["after"] - counts["before"]
    result = dict(source=new_source, originalSource=old_source, stages=stages,
                  oldFindings=sum(counts["before"].values()), newRawFindings=sum(counts["after"].values()),
                  newlyObserved=[dict(file=k[0], rule=k[1], method=k[2], count=v) for k, v in delta.items()],
                  actualExit=0 if not delta else 1, platformOperations=0,
                  productTestsExecuted=0, wholeF03Accepted=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), result["actualExit"], result["newlyObserved"])
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
