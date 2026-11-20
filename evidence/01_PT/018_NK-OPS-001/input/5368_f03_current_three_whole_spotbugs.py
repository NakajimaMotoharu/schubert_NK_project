"""Run static analysis of three whole, currently packaged product modules."""

import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile, ZIP_DEFLATED


B = runpy.run_path(str(Path(__file__).with_name("5364_f02_utc42_four_current_jars.py")))
OPS, PLAN, COMMON, UPPER = (B[key] for key in ("OPS", "PLAN", "COMMON", "UPPER"))
MODULES = {"protocol": 176, "storage": 79, "bootstrap": 201}


def main():
    pin, digest, dump, timestamp = (COMMON[n] for n in ("pin", "sha", "dump", "timestamp"))
    read = UPPER["read"]
    start = read(next(PLAN.glob("884_*")))
    work = start["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in work["oracleReferences"])
    build, post, old, known_metrics, pins, annotations = (
        read(ref["path"]) for ref in work["oracleReferences"][1:])
    core = work["productionCoreMain"]
    assert core == build["sourceCore"] == post["productionCore"]
    assert old["actualExit"] == 1 and old["terminal"]["actualExit"] == 2
    assert old["excludedEarlierHoldClasses"] == 53 and len(old["missing"]) == 10
    sdk_jars = dict(pins["sdkJars"])
    for extra in (annotations["onlyAdditionalAux"], known_metrics["explicitMetricsSdk"]):
        sdk_jars[extra["path"]] = extra["sha256"]
    assert all(pin(Path(name))["sha256"] == value for name, value in sdk_jars.items())
    command = old["terminal"]["command"]
    source_pins = {p["path"]:p["sha256"] for p in pins["toolAndRulePins"]}
    assert all(pin(Path(name))["sha256"] == source_pins[name]
               for name in command[command.index("-cp")+1].split(":"))
    assert ["-effort:max", "-low", "-xml:withMessages", "-exitcode"] == command[
        command.index("-effort:max"):command.index("-exitcode")+1]
    out = (OPS / work["run"]).resolve()
    out.mkdir()
    target_xml = out / "spotbugs.xml"
    candidate = {}
    detail = {}
    physically_changed = []
    aux_path = out / "spotbugs-aux.txt"
    aux_path.write_text("\n".join(sorted(sdk_jars)) + "\n")
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-three-module-whole-") as name:
        temporary = Path(name)
        targets = temporary / "current-three-modules.jar"
        with ZipFile(targets, "x", compression=ZIP_DEFLATED) as collection:
            for module, extent in MODULES.items():
                ref = build["packagedJars"][module]["artifact"]
                assert ref == post["qualifiedLocalArtifacts"][module]["artifact"]
                archive = Path(ref["path"])
                assert pin(archive) == ref
                local = {}
                with ZipFile(archive) as current:
                    members = sorted(n for n in current.namelist() if n.endswith(".class"))
                    assert len(members) == extent and len(set(members)) == extent
                    assert set(members) <= old["targetHashes"].keys()
                    for entry in members:
                        content = current.read(entry)
                        assert entry not in candidate
                        value = digest(content)
                        if value != old["targetHashes"][entry]:
                            physically_changed.append(entry)
                        local[entry] = candidate[entry] = value
                        collection.writestr(entry, content)
                detail[module] = dict(classes=extent, jar=ref,
                                      classMapSha256=digest(json.dumps(local, sort_keys=True).encode()))
        assert len(candidate) == 456 and set(physically_changed) == set(post["requalificationRequired"])
        expected = [*command[:command.index("-auxclasspathFromFile")+1],
                    aux_path, "-output", target_xml, targets]
        execution = UPPER["run"](out, "spotbugs", expected, temporary,
                                 {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
    if target_xml.is_file():
        tree = ElementTree.parse(target_xml).getroot()
        observed = {row.get("class").replace(".", "/")+".class" for row in tree.findall(".//ClassStats")}
        findings = [dict(rule=row.get("type"), target=row.find("Class").get("classname"))
                    for row in tree.findall("BugInstance")]
        errors = len(tree.findall(".//Error"))
        missing = [row.text for row in tree.findall(".//MissingClass")]
    else:
        observed, findings, errors, missing = set(), [], None, []
    okay = execution["actualExit"] == 0 and observed == set(candidate) and not findings and errors == 0 and not missing
    status = dict(actualExit=0 if okay else 1, source=work["source"], productionCore=core,
                  phase="F03 exact current three full product modules",
                  inputs=detail, artifactShaValid=True, allIncludedOrdinaryPreviously=True, observed=len(observed),
                  missingClassStats=sorted(set(candidate)-observed),
                  unexpectedClassStats=sorted(observed-set(candidate)),
                  physicalChangedInScope=sorted(physically_changed), missing=missing, errors=errors, findings=findings,
                  physicalExaminedExpected=456, injectedPhysical=0, heldBatchPhysicalRead=0,
                  actualProductTests=0, productionEntrypointExecution=0,
                  terminal=execution, staticReport=pin(target_xml) if target_xml.exists() else None,
                  outsideThisScope=["Batch", "API", "Web"], wholeF03Accepted=False,
                  whole451Accepted=False, terminalAtUTC=timestamp())
    dump(out / "manifest.json", status)
    print(pin(out / "manifest.json"), execution["actualExit"], len(observed), len(missing), errors, len(findings))
    return status["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
