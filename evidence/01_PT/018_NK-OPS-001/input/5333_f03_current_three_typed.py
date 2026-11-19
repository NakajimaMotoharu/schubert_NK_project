"""Check explicitly selected changed binaries under the existing protected-scope filter."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED


INPUT = Path(__file__).parent
PRIOR = runpy.run_path(str(INPUT / "5242_f03_batch_current_static_delta.py"))
UPPER = runpy.run_path(str(INPUT / "5326_f02_group_lookup_upper.py"))
OPS, PLAN, COMMON = (UPPER[name] for name in ("EVIDENCE", "PLAN", "COMMON"))


def main(plan_prefix="779_*"):
    read = UPPER["read"]
    start = read(next(PLAN.glob(plan_prefix)))
    work = start["values"]
    pin = COMMON["pin"]
    assert all(pin(Path(meta["path"])) == meta for meta in work["oracleReferences"])
    jar_manifest, compile_manifest, prior, tools, annotation = (
        read(row["path"]) for row in work["oracleReferences"][1:6])
    core = work["productionCoreMain"]
    assert jar_manifest["sourceCore"] == core
    assert all(x["actualExit"] == 0 for x in
               (jar_manifest, annotation, *(read(row["path"]) for row in work["oracleReferences"][6:])))
    expected = {name for rows in jar_manifest["changedClassesFromOldJars"].values() for name in rows}
    assert len(expected) == work.get("expectedChangedCount", 3)
    assert all(PRIOR["allowed"](name) for name in expected)
    prior_command = prior["command"]
    new_sdk = annotation["onlyAdditionalAux"]
    assert pin(Path(new_sdk["path"])) == new_sdk
    sdk = dict(tools["sdkJars"])
    sdk[new_sdk["path"]] = new_sdk["sha256"]
    assert len(sdk) == prior["externalSdkCount"]
    assert all(pin(Path(path))["sha256"] == value for path, value in sdk.items())
    tool_pins = {p["path"]: p["sha256"] for p in tools["toolAndRulePins"]}
    classpath = prior_command[prior_command.index("-cp") + 1].split(":")
    assert all(pin(Path(path))["sha256"] == tool_pins[path] for path in classpath)
    assert ["-effort:max", "-low", "-xml:withMessages", "-exitcode"] == prior_command[
        prior_command.index("-effort:max"):prior_command.index("-exitcode")+1]
    out = (OPS / work["run"]).resolve()
    out.mkdir()
    xml = out / "spotbugs.xml"
    analyzed, excluded = {}, 0
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-three-") as temp:
        scratch = Path(temp)
        peer = scratch / "allowed-aux.jar"
        with ZipFile(peer, "x", compression=ZIP_DEFLATED) as aux:
            aux_hits = 0
            for name, item in jar_manifest["jars"].items():
                path = Path(item["artifact"]["path"])
                assert pin(path) == item["artifact"]
                with ZipFile(path) as jar:
                    for entry, expected_hash in compile_manifest["classHashes"][name].items():
                        if not PRIOR["allowed"](entry):
                            excluded += 1
                            continue
                        data = jar.read(entry)
                        assert hashlib.sha256(data).hexdigest() == expected_hash
                        if entry in expected:
                            target = scratch / entry
                            target.parent.mkdir(exist_ok=True, parents=True)
                            target.write_bytes(data)
                            analyzed[entry] = expected_hash
                        else:
                            aux.writestr(entry, data)
                            aux_hits += 1
        assert set(analyzed) == expected
        assert excluded == prior["excludedFromTargetsAndAux"]
        assert aux_hits + excluded + len(expected) == 1102
        auxdef = out / "spotbugs-aux.txt"
        auxdef.write_text("\n".join([str(peer), *sorted(sdk)]) + "\n")
        command = [*prior_command[:prior_command.index("-auxclasspathFromFile")+1],
                   auxdef, "-output", xml, *(scratch / path for path in sorted(expected))]
        result = UPPER["run"](out, "spotbugs", command, scratch,
                              {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
    if xml.exists():
        report = ET.parse(xml).getroot()
        observed = {x.get("class").replace(".", "/") + ".class" for x in report.findall(".//ClassStats")}
        findings = [dict(type=node.get("type"), primary=node.find("Class").get("classname"))
                    for node in report.findall("BugInstance")]
        errors = len(report.findall(".//Error"))
        missing = sorted(x.text for x in report.findall(".//MissingClass"))
    else:
        observed, findings, errors, missing = set(), [], None, []
    okay = result["actualExit"] == 0 and observed == expected and errors == 0 and not findings and not missing
    outcome = dict(actualExit=0 if okay else 1, source=work["source"], productionCore=core,
                   startEvent=start["eventId"], terminal=result, observedClassStats=sorted(observed),
                   targetHashes=analyzed, errors=errors, spots=findings, missing=missing,
                   excludedEarlierHoldClasses=excluded, testedAuxInput=aux_hits,
                   report=pin(xml) if xml.exists() else None, productTestsExecuted=0,
                   wholeF03Accepted=False, whole451Accepted=False, newFormalAcceptance=0,
                   terminalAtUTC=datetime.now(timezone.utc).isoformat())
    COMMON["dump"](out / "manifest.json", outcome)
    print(pin(out / "manifest.json"), result["actualExit"], findings, errors, missing)
    return outcome["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
