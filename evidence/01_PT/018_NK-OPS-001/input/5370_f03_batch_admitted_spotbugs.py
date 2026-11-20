"""Measure Batch's permitted static closure without loading or reading held classfiles."""

import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile, ZIP_DEFLATED


G = runpy.run_path(str(Path(__file__).with_name("5364_f02_utc42_four_current_jars.py")))
OPS, PLAN, UPPER, COMMON = (G[k] for k in ("OPS", "PLAN", "UPPER", "COMMON"))
INTERNAL = "dev.codex.schubert.nk."


def classfile(binary_name):
    return binary_name.replace(".", "/") + ".class"


def archive_classes(file, classes):
    with ZipFile(file, "x", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(classes.items()):
            archive.writestr(name, data)


def closed_subset(batch, peers, edges):
    remaining = set(batch)
    exclusions = {}
    while True:
        lost = {}
        visible = remaining | peers
        for origin in sorted(remaining):
            uncovered = {classfile(target) for target in edges.get(origin[:-6].replace("/", "."), ())
                         if target.startswith(INTERNAL) and classfile(target) not in visible}
            if uncovered:
                lost[origin] = sorted(uncovered)
        if not lost:
            return remaining, exclusions
        remaining.difference_update(lost)
        exclusions.update(lost)


def main():
    pin, sha, dump = (COMMON[key] for key in ("pin", "sha", "dump"))
    read = UPPER["read"]
    start = read(next(PLAN.glob("887_*")))
    values = start["values"]
    core = values["productionCoreMain"]
    assert all(pin(Path(ref["path"])) == ref for ref in values["oracleReferences"])
    package, three, broad, sdk, latest = (read(ref["path"]) for ref in values["oracleReferences"][1:])
    assert package["sourceCore"] == latest["productionCore"] == three["productionCore"] == core
    assert three["allObserved456"] and broad["terminal"]["actualExit"] == 2
    permitted, auxiliary, held = {}, {}, []
    for name, jar in package["packagedJars"].items():
        path = Path(jar["artifact"]["path"])
        assert pin(path) == jar["artifact"]
        target = permitted if name == "batch" else auxiliary
        with ZipFile(path) as archive:
            for member in archive.namelist():
                if not member.endswith(".class"):
                    continue
                if member not in broad["targetHashes"]:
                    assert name == "batch"
                    held.append(member)
                    continue
                assert member not in target
                target[member] = archive.read(member)
    assert len(permitted) == 593 and len(auxiliary) == 456 and len(held) == 53
    assert not (permitted.keys() & auxiliary.keys())
    assert all(sha(content) == broad["targetHashes"][member] for member, content in permitted.items())
    cmd = latest["terminal"]["command"]
    known_aux = Path(cmd[cmd.index("-auxclasspathFromFile")+1])
    tool_files = sorted(set(known_aux.read_text().splitlines()))
    assert sdk["explicitMetricsSdk"]["path"] in tool_files
    begin = read(next(OPS.glob("PG39810-*/begin.json")))
    models = begin["sdkJars"]
    annotation = read(next(OPS.glob("PG39812-*/manifest.json")))["onlyAdditionalAux"]
    assert tool_files == sorted(set(models) | {annotation["path"], sdk["explicitMetricsSdk"]["path"]})
    fingerprints = {**models, annotation["path"]: annotation["sha256"],
                    sdk["explicitMetricsSdk"]["path"]: sdk["explicitMetricsSdk"]["sha256"]}
    assert all(pin(Path(path))["sha256"] == value for path, value in fingerprints.items())
    tool_names = begin["toolAndRulePins"]
    known_tools = {ref["path"]:ref["sha256"] for ref in tool_names}
    assert all(pin(Path(path))["sha256"] == known_tools[path] for path in cmd[cmd.index("-cp")+1].split(":"))
    java = Path(cmd[0])
    env = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
    out = (OPS/values["run"]).resolve()
    out.mkdir()
    spot_report = out / "spotbugs.xml"
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-closed-typed-batch-") as folder:
        scratch = Path(folder)
        all_batch = scratch / "admitted-batch-input.jar"
        peers = scratch / "three-qualified-modules.jar"
        archive_classes(all_batch, permitted)
        archive_classes(peers, auxiliary)
        sdk_path = ":".join([str(peers), *tool_files])
        typed_receipt = UPPER["run"](out, "jdeps", [
            java.with_name("jdeps"), "--ignore-missing-deps", "-verbose:class", "-filter:none",
            "--class-path", sdk_path, all_batch,
        ], scratch, env)
        assert typed_receipt["actualExit"] == 0
        edges = G["G"]["dependency_rows"](typed_receipt)
        closed, removed = closed_subset(permitted.keys(), auxiliary.keys(), edges)
        assert 0 < len(closed) < len(permitted)
        assert len(closed) + len(removed) + len(held) == 646
        assert len({t for ts in edges.values() for t in ts if t in broad["missing"]}) > 0
        closure = out/"admitted-closure.json"
        dump(closure, dict(approvedSeeds=593, checkedSet=sorted(closed), deferredTransitive=removed,
                           explicitPhysicalHoldMetadataOnly=sorted(held), typedInput=typed_receipt,
                           heldArtifactClassDataRead=0))
        packed = scratch / "closed-batch-targets.jar"
        selected = {key:permitted[key] for key in closed}
        archive_classes(packed, selected)
        aux_file = out / "spotbugs-aux.txt"
        aux_file.write_text("\n".join([str(peers),*tool_files])+"\n")
        execution = UPPER["run"](out, "spotbugs", [
            *cmd[:cmd.index("-auxclasspathFromFile")+1], aux_file, "-output", spot_report, packed,
        ], scratch, env)
    if spot_report.is_file():
        xml = ElementTree.parse(spot_report).getroot()
        observed = {classfile(node.get("class")) for node in xml.findall(".//ClassStats")}
        missing = [node.text for node in xml.findall(".//MissingClass")]
        errors = len(xml.findall(".//Error"))
        findings = [dict(rule=r.get("type"), typedTarget=r.find("Class").get("classname"))
                    for r in xml.findall("BugInstance")]
    else:
        observed, missing, errors, findings = set(), [], None, []
    matched = execution["actualExit"] == 0 and not any((findings, missing, errors)) and observed == closed
    data = dict(actualExit=0 if matched else 1, source=values["source"], productionCore=core,
                originalWholeBatchPhysical=646, physicallyAdmitted=593, heldPhysical=53,
                closedTypedClasses=len(closed), transitiveExceptionClasses=len(removed), observed=len(observed),
                stableScopeVerified=matched, candidatePhysicalMapSha256=sha(json.dumps(
                    {name:sha(body) for name,body in selected.items()},sort_keys=True).encode()),
                missingFromClassStats=sorted(closed-observed), unexpectedClassStats=sorted(observed-closed),
                rawFindings=findings, rawMissing=missing, analyzerErrors=errors,
                evidence=dict(graph=pin(closure), rawXml=pin(spot_report) if spot_report.is_file() else None),
                priorBroadSpotBugsRerun=False, protectedClassBytesRead=0, actualProductTests=0,
                realBackendActions=0, wholeBatchModuleAccepted=False, wholeF03Accepted=False, whole451Accepted=False,
                stages=dict(typed=typed_receipt, spotbugs=execution), terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",data)
    print(pin(out/"manifest.json"), len(closed), len(removed), execution["actualExit"], len(missing), errors, len(findings))
    return data["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
