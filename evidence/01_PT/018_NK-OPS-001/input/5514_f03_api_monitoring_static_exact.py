"""Analyze only the 30 exact API monitoring physical files and their admitted inputs."""
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
group = json.loads(next(plan.glob("1383_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(item["path"])) == item for item in refs)
typed, sdk, post, hikari = [json.loads(Path(item["path"]).read_bytes()) for item in refs[1:]]
assert typed["actualExit"] == post["actualExit"] == hikari["actualExit"] == 0
assert typed["source"] == ctx["productionCoreMain"] and typed["targetJoin"]["exactClassBytes"]
assert hikari["actualDatabaseDriverSqlNetworkRoleAdmissionVmRootNativeOperations"] == 0
source_inputs = typed["explicitSourcePins"]
retained = next(p for p in Path(typed["targetJoin"]["executed"]["path"]).parents if p.name == "classes")
held = {"TemporaryInfrastructureException", "FingerprintKeyRing", "ResponseSnapshotCodec",
        "WebStartupException"}
classes = typed["generatedPhysical"]
assert len(classes) == 30 and len(source_inputs) == 23
assert all(pin(Path(row["path"])) == row for row in source_inputs)
aux = []
for entry in typed["dependencies"]:
    path = Path(entry["path"])
    assert pin(path) == entry
    with ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist() if name.endswith(".class"))
    assert names and len(names) == len(set(names))
    assert not any(Path(name).stem.split("$", 1)[0] in held for name in names)
    if path.name.startswith("schubert-nk-"):
        assert path.name == "schubert-nk-protocol-0.1.0-SNAPSHOT.jar"
        assert all(name.startswith("dev/codex/schubert/nk/protocol/") or name.endswith("/module-info.class")
                   or name == "module-info.class" for name in names)
    else:
        assert path.is_relative_to(Path("../toolchain/m2/repository").resolve())
    aux.append(dict(artifact=entry, physicalFiles=len(names), inventorySha256=sha("\n".join(names).encode())))
assert len(aux) == 15
root = Path(refs[1]["path"]).parent.parent
out = root / ctx["run"]
saved_spotbugs = pin(out / "spotbugs.xml")
start_time = datetime.now(timezone.utc).isoformat()
tc = Path("../toolchain").resolve()
java = tc / "jdk-25.0.4/bin/java"
environment = {"PATH": f"{java.parent}:/usr/bin:/bin", "LANG": "C.UTF-8"}
steps = {}


def run(name, args):
    command = list(map(str, args))
    result = subprocess.run(command, env=environment, capture_output=True, timeout=90)
    steps[name] = dict(command=command, exitCode=result.returncode,
                       stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr))
    if result.returncode and result.stderr:
        print(name, result.stderr.decode(errors="replace")[:1200])
    return result.returncode


with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40948-analysis-") as temp:
    place = Path(temp)
    measured = place / "classfiles"
    for row in classes:
        name = row["classPath"]
        assert name.startswith("dev/codex/schubert/nk/api/monitoring/") and Path(name).stem.split("$")[0] not in held
        payload = (retained / name).read_bytes()
        assert sha(payload) == row["sha256"]
        target = measured / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    classpath = place / "aux"
    classpath.write_text("\n".join(row["artifact"]["path"] for row in aux) + "\n")
    sb_path = Path(saved_spotbugs["path"])
    sb_cp = sdk["steps"]["spotbugs"]["command"][3]
    sb_exit = None
    sb = ET.parse(sb_path).getroot()
    assert pin(sb_path) == saved_spotbugs
    observed = {node.attrib["class"] for node in sb.findall(".//ClassStats")}
    expected = {row["classPath"].removesuffix(".class").replace("/", ".")
                for row in classes}
    assert observed == expected
    original_inputs = [node.text for node in sb.findall("./Project/Jar")]
    assert len(original_inputs) == 1 and original_inputs[0].startswith("/dev/shm/pg40948-analysis-")
    sb_actual = dict(findings=len(sb.findall(".//BugInstance")), errors=len(sb.findall(".//Error")),
                     missing=len(sb.findall(".//MissingClass")), measured=len(observed),
                     metadata=sum(name.endswith(".package-info") for name in observed),
                     originalInputs=original_inputs, originalExit=sb_exit, report=saved_spotbugs)
    sources_file = place / "sources"
    sources_file.write_text("\n".join(str(Path(item["path"]).resolve()) for item in source_inputs) + "\n")
    pmd_path = out / "pmd.xml"
    pmd_cp = sdk["steps"]["pmd"]["command"][2]
    pmd_aux = ":".join([str(measured), *(row["artifact"]["path"] for row in aux),
                       str(java.parents[1] / "lib/jrt-fs.jar")])
    rules = Path("tools/quality/static/pmd.xml")
    pmd_exit = run("pmd", [java, "-cp", pmd_cp, "net.sourceforge.pmd.cli.PmdCli", "check",
                           "--file-list", sources_file, "--rulesets", rules.resolve(),
                           "--use-version", "java-25", "--aux-classpath", pmd_aux, "--no-cache",
                           "--format", "xml", "--report-file", pmd_path])
    report = ET.parse(pmd_path).getroot()
    ns = {"p": report.tag.partition("}")[0].removeprefix("{")}
    rows = [dict(source=Path(file.attrib["name"]).name, line=int(node.attrib["beginline"]),
                 rule=node.attrib["rule"])
            for file in report.findall("p:file", ns) for node in file.findall("p:violation", ns)]
    processing = len(report.findall("p:error", ns))
    pmd = dict(rawFindings=rows, processingErrors=processing, report=pin(pmd_path), rules=pin(rules))
    assert all(Path(artifact).is_relative_to(tc) for artifact in (sb_cp + ":" + pmd_cp).split(":"))
receipts_present = pmd_exit in (0, 4) and not processing
record = dict(actualExit=0 if receipts_present else 1, source=ctx["productionCoreMain"], startEvent=group["eventId"],
              startedAtUTC=start_time, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              typed=refs[1], allowedAuxiliaryInventories=aux, targetPhysical=classes, targetSource=source_inputs,
              steps=steps, spotbugs=sb_actual, pmd=pmd, productTestsRerun=0, compilerRerun=0,
              spotbugsReplayed=0, originalWrapperExit=1, originalToolExitRecovered=False,
              staticFinalPass=False, originalAttemptBug="BUG-3428",
              actualExternalOperations=0, wholeF03=False, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
print(record["actualExit"], sb_actual, pmd_exit, rows)
raise SystemExit(record["actualExit"])
