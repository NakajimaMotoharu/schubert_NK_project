"""Measure the two schema history fixtures in one process against the exact candidate."""

from pathlib import Path
import runpy
import subprocess
from hashlib import sha256
from xml.etree import ElementTree as ET


PRIOR = runpy.run_path(str(Path(__file__).with_name("5791_f03_schema_history_fixture_local.py")))
ROOT, RUNS, OPS, RECORDS = (PRIOR[k] for k in ("ROOT", "RUNS", "OPS", "RECORDS"))
get, pin, git, now, put = (PRIOR[k] for k in ("get", "pin", "git", "now", "put"))
ADMISSION = PRIOR["FIXTURE"]
ROW = ADMISSION.with_name("SchemaHistoryRowValueTest.java")
METHOD_PREFIX = "opsSchema011"
OLD = "PG43176-f03-schema-history-fixture-exact13-v1"
RUN = "PG43178-p0190102-schema-history-single-exec-v1"


def copy_exact(src, dest, expected):
    assert pin(src)["sha256"] == expected
    dest.parent.mkdir(exist_ok=True, parents=True)
    with dest.open("xb") as handle:
        handle.write(src.read_bytes())
    assert pin(dest)["sha256"] == expected


def main():
    point, = RECORDS.glob("3450_*")
    work = get(point)["values"]
    assert work["run"] == RUN
    core = work["productionCoreMain"]
    current = git("rev-parse", "HEAD").decode().strip()
    assert work["source"] == current
    approved, public = PRIOR["public_receipt"]("PG43176")
    assert public["productCore"] == core and public["actualExit"] == 0
    assert public["actualLocalTests"] == 13 and public["coverage"]["method"]["missed"] == 3
    previous_archive = RUNS / OLD
    receipt = previous_archive / "begin.json"
    assert receipt.resolve() == Path(public["commandManifest"]["path"]).resolve()
    assert pin(receipt)["sha256"] == public["commandManifest"]["sha256"]
    available = get(receipt)
    assert pin(ADMISSION) == available["fixture"]
    historical, historical_proof = PRIOR["public_receipt"]("PG40494")
    assert historical_proof["actualExit"] == 0
    old_row = git("show", f'{historical_proof["testSource"]}:{ROW}')
    assert sha256(old_row).hexdigest() == historical_proof["testInputs"][str(ROW)]
    original_literal = b'checksum=19, success=true]"'
    split_literal = b'checksum=19,"\n            + " success=true]"'
    assert old_row.count(original_literal) == 1
    assert old_row.replace(original_literal, split_literal) == ROW.read_bytes()
    assert all(file.read_bytes() == git("show", f"{current}:{file}") for file in (ADMISSION, ROW))
    assert all(pin(x["path"]) == x for x in available["exactInputs"])
    out = RUNS / RUN
    out.mkdir(mode=0o700)
    for leaf in ("target/classes", "test", "xml", "meter"):
        (out / leaf).mkdir(parents=True)
    for row in available["bytes"]:
        member = Path("target/classes") / row["className"]
        copy_exact(previous_archive / member, out / member, row["sha256"])
    steps = {name: [x.replace(OLD, RUN) for x in available["commands"][name]]
             for name in ("format", "fixture", "junit", "rawCompile", "unfiltered")}
    steps["format"].append(str(ROW))
    steps["fixture"].append(str(ROW))
    steps["junit"].extend(("--select-class", "dev.codex.schubert.nk.api.maintenance.SchemaHistoryRowValueTest"))
    put(out / "begin.json", dict(run=RUN, source=current, productCore=core, startedAtUTC=now(),
                               approved=pin(approved), olderRowFixtureReceipt=pin(historical),
                               fixtures=list(map(pin, (ADMISSION, ROW))), physicalInputs=available["bytes"],
                               dependencies=available["exactInputs"], commands=steps,
                               earlierPreflights=[
                                   dict(exit=1, cause="relative and absolute receipt path spellings", ptStarted=0),
                                   dict(exit=1, cause="historical Row fixture predates its literal wrapping", ptStarted=0),
                               ]))
    statuses = {}
    for name, argv in steps.items():
        executed = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=120, check=False)
        statuses[name] = executed.returncode
        (out / f"{name}.stdout").write_bytes(executed.stdout)
        (out / f"{name}.stderr").write_bytes(executed.stderr)
        put(out / f"{name}.exit.json", dict(exit=executed.returncode, observedAtUTC=now()))
        print(name, executed.returncode, flush=True)
        if executed.returncode:
            return executed.returncode
    xml = out / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(xml).getroot()
    assert suite.get("tests") == "14" and all(suite.get(k) == "0" for k in ("failures", "errors", "skipped"))
    executed_cases = sorted((case.get("classname"), case.get("name")) for case in suite.findall("testcase"))
    new = [method for cls, method in executed_cases if cls.rsplit(".", 1)[-1] == ROW.stem]
    assert len(new) == 1 and new[0].startswith(METHOD_PREFIX)
    retained_cases = get(Path(public["sanitized"][0]["path"]))["cases"]
    assert sorted(x["method"] for x in retained_cases) == sorted(
        method for cls, method in executed_cases if cls.rsplit(".", 1)[-1] == ADMISSION.stem)
    result = dict(run=RUN, source=current, productCore=core, terminalAtUTC=now(), actualExit=0,
                  stageExits=statuses, cases=executed_cases, rawCounterFile=pin(out / "unfiltered.stdout"),
                  xml=pin(xml), execData=pin(out / "unit.exec"), actualDatabaseConnections=0,
                  externalActions=0, remeasuredInSingleNewExec=True)
    put(out / "terminal.json", result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
