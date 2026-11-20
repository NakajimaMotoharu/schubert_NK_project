"""Measure three exact ModePolicy classfiles using only the original observation exec."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def pin(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    cp = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1437_*.json"))
    g = json.loads(cp.read_bytes())
    scope = g["values"]
    refs = scope["oracleReferences"][1:]
    paths = [Path(ref["path"]) for ref in refs]
    assert [pin(path) for path in paths] == refs
    current, unit, prior = [json.loads(path.read_bytes()) for path in paths]
    assert all(row["actualExit"] == 0 for row in (current, unit, prior))
    assert prior["source"] == unit["source"] and prior["singleSession"]
    assert prior["tests"] == 55 and prior["failures"] == prior["errors"] == prior["skipped"] == 0
    assert prior["execSha256"] == unit["execSha256"]
    core = scope["productionCoreMain"]
    source = next(row for row in current["inputSourcePins"] if row["path"].endswith("/MonitoringModePolicy.java"))
    original = subprocess.check_output(["git", "show", f"{unit['source']}:{source['path']}"])
    candidate = subprocess.check_output(["git", "show", f"{core}:{source['path']}"])
    assert original == candidate and hashlib.sha256(candidate).hexdigest() == source["sha256"]

    prefix = "dev/codex/schubert/nk/batch/monitoring/MonitoringModePolicy"
    names = [prefix, prefix + "$DetailService", prefix + "$RetentionConfiguration"]
    current_by_name = {row["path"].removesuffix(".class").split("/classes/", 1)[1]: row
                       for row in current["supportSeparatePhysical"]}
    selected = [current_by_name[name] for name in names]
    for name, declared in zip(names, selected, strict=True):
        assert pin(Path(declared["path"])) == declared
        assert prior["sourcePhysicalInventory"][name]["sha256"] == declared["sha256"]

    old_exec = Path("../pgpt-runs/PG379/pg14928-batch-monitoring-pure-fifty-five-pt-v1/jacoco.exec").resolve()
    assert pin(old_exec)["sha256"] == unit["execSha256"]
    prior_raw = next(item for item in current["steps"] if item["step"] == "raw")
    assert prior_raw["exitCode"] == 0
    raw_command = [*prior_raw["command"][:4], str(old_exec), *(row["path"] for row in selected)]
    started = datetime.now(timezone.utc).isoformat()
    measured = subprocess.run(raw_command, capture_output=True, timeout=30, check=False)
    terminal = datetime.now(timezone.utc).isoformat()
    lines = measured.stdout.decode().splitlines()
    rows = {}
    for line in lines:
        if line.startswith("CLASS\t"):
            cells = line.split("\t")
            assert cells[3] == "true"
            rows[cells[1]] = {
                "crc64": cells[2],
                "counters": {key: dict(missed=int(m), covered=int(c))
                             for key, m, c in (word.split(":") for word in cells[6:])},
            }
    assert measured.returncode == 0 and rows.keys() == set(names)
    out = Path("evidence/01_PT/018_NK-OPS-001/evidence") / scope["run"]
    out.mkdir()
    (out / "unfiltered.tsv").write_bytes(measured.stdout)
    (out / "manifest.json").write_text(json.dumps(dict(
        actualExit=0, run=scope["run"], source=core, historicalSource=unit["source"],
        startEvent=g["eventId"], startedAtUTC=started, terminalAtUTC=terminal,
        rawCommand=raw_command, productionSource=source, physical=selected,
        originalExec=pin(old_exec), originalSession=prior["sessionIdentity"], previousEvidence=refs,
        originalTestCount=55, originalFiltered=prior["fullSourceUnits"][prefix]["totals"],
        actual=rows, rawOutput=pin(out / "unfiltered.tsv"),
        stderrSha256=hashlib.sha256(measured.stderr).hexdigest(),
        productTestsReexecuted=0, execStreamsCombined=0, nativeOperations=0,
        whole451=False, wholeF03=False, formalDelta=0,
    ), ensure_ascii=False, indent=2) + "\n")
    print(rows)


if __name__ == "__main__":
    main()
