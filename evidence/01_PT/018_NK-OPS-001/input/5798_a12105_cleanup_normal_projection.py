"""Verify the current successful cleanup projection and its local exception controls."""

from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET


PRIOR = runpy.run_path(str(Path(__file__).with_name("5797_a12105_cleanup_terminal_read_proxy.py")))
ROOT, RUNS, RECORDS, FIXTURE = (PRIOR[k] for k in ("ROOT", "RUNS", "RECORDS", "FIXTURE"))
get, pin, git, now, put, manifest = (PRIOR[k] for k in ("get", "pin", "git", "now", "put", "manifest"))
OLD = PRIOR["RUN"]
RUN = "PG43208-a12105-cleanup-terminal-ordinary-projection-v1"
CASE = "ordinaryTerminalReadProjectsTheSevenSuccessfulRowsInFixedOrder()"


def main():
    point, = RECORDS.glob("3476_*")
    start = get(point)["values"]
    core = start["productionCoreMain"]
    current = git("rev-parse", "HEAD").decode().strip()
    assert start["run"] == RUN
    prior_path, prior = manifest("PG43206")
    assert prior["productCore"] == core and prior["selectedCases"] == 4
    assert FIXTURE.read_bytes() == git("show", f"{current}:{FIXTURE}")
    assert FIXTURE.read_bytes() != git("show", f'{start["source"]}:{FIXTURE}')
    before = RUNS / OLD
    before_command = before / "begin.json"
    basis = prior["commandReceipt"]
    assert before_command.resolve() == Path(basis["path"]).resolve()
    assert pin(before_command)["sha256"] == basis["sha256"]
    original = get(before_command)
    old_result = get(before / "terminal.json")
    assert len(old_result["testCases"]) == 4
    out = RUNS / RUN
    out.mkdir(mode=0o700)
    for leaf in ("target/classes", "test", "xml", "meter"):
        (out / leaf).mkdir(parents=True)
    for entry in original["physical"]:
        rel = Path("target/classes") / entry["member"]
        src, dest = before / rel, out / rel
        assert pin(src)["sha256"] == entry["sha256"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
        assert pin(dest)["sha256"] == entry["sha256"]
    commands = {k: [v.replace(OLD, RUN) for v in cmd] for k, cmd in original["commands"].items()}
    (out / "current-static-sources.txt").write_text(str(FIXTURE) + "\n")
    put(out / "begin.json", dict(run=RUN, source=current, productCore=core, startedAtUTC=now(),
        currentFixture=pin(FIXTURE), prior=pin(prior_path), physical=original["physical"], commands=commands))
    exits = {}
    for step, command in commands.items():
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120, check=False)
        (out / f"{step}.stdout").write_bytes(result.stdout)
        (out / f"{step}.stderr").write_bytes(result.stderr)
        exits[step] = result.returncode
        put(out / f"{step}.exit.json", dict(exit=result.returncode, observedAtUTC=now()))
        print(step, result.returncode, flush=True)
        assert result.returncode in {"spotbugs": {0, 1}, "pmd": {0, 4}}.get(step, {0}), step
    junit = out / "xml/TEST-junit-jupiter.xml"
    test = ET.parse(junit).getroot()
    assert test.get("tests") == "5" and all(test.get(k) == "0" for k in ("failures", "skipped", "errors"))
    cases = {x.get("name") for x in test.findall("testcase") if x.get("classname") == PRIOR["SELECTED"]}
    assert cases == set(old_result["testCases"]).union({CASE})
    spot = ET.parse(out / "spotbugs.xml").getroot()
    assert not spot.findall("./Errors/Error") and not spot.findall("./Errors/MissingClass")
    put(out / "terminal.json", dict(run=RUN, source=current, productCore=core, terminalAtUTC=now(),
        actualExit=0, actualTestCases=sorted(cases), stages=exits,
        spotbugs=[x.get("type") for x in spot.findall("BugInstance")],
        pmd=[x.get("rule") for x in ET.parse(out / "pmd.xml").findall(".//{*}violation")],
        receipts=list(map(pin, (junit, out / "unit.exec", out / "unfiltered.stdout"))),
        independentlyConstructedOrdinaryRows=7, actualDbConnections=0,
        gatedFailedProfileExecuted=False))
    print(len(cases), exits)


if __name__ == "__main__":
    main()
