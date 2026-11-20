"""Reconcile the read-only PG40838 input record with its analyzer reports."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
start = read(next(plan.glob("1281_*")))
values = start["values"]
core = values["productionCoreMain"]
assert all(pin(Path(item["path"])) == item for item in values["oracleReferences"])
evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
prior_path = next(evidence.glob("PG40838-*/manifest.json"))
prior = read(prior_path)
assert prior["source"] == core and prior["actualExit"] == 0
assert prior["analyzerProductJarInputs"] == prior["heldClassfilesRead"] == 0
expected_sources = {"BatchRepositoryException", "BatchRun", "CleanupCounts", "InspectionSummary",
                    "InspectionSummaryRepository", "JdbcResourceFailures", "JdbcFailureGraph",
                    "StorageIoException"}
assert len(prior["sources"]) == 8
assert {Path(item["path"]).stem for item in prior["sources"]} == expected_sources
for item in prior["sources"]:
    path = Path(item["path"])
    original = subprocess.check_output(["git", "show", f"{core}:{path}"], timeout=15)
    assert pin(path) == item and sha256(original).hexdigest() == item["sha256"]
expected_members = expected_sources | {"StorageIoException$Reason"}
assert {Path(name).stem for name in prior["exactLocalClassFiles"]} == expected_members

pmd_report = Path(prior["pmd"]["report"]["path"])
sb_report = Path(prior["spotbugs"]["report"]["path"])
assert pin(pmd_report) == prior["pmd"]["report"] and pin(sb_report) == prior["spotbugs"]["report"]
sb = ET.parse(sb_report).getroot()
pmd = ET.parse(pmd_report).getroot()
sb_cmd = prior["steps"]["spotbugs"]["command"]
pmd_cmd = prior["steps"]["pmd"]["command"]
assert prior["steps"]["spotbugs"]["exit"] == 0
assert prior["steps"]["pmd"]["exit"] in (0, 4)
assert all(prior["compilerControls"].values())
target = sb_cmd[-1]
package_dir = Path(target).parents[1]
assert target.endswith("/scope/target/classes") and package_dir.is_relative_to("/dev/shm")
assert [node.text for node in sb.findall("./Project/Jar")] == [target]
aux = [node.text for node in sb.findall("./Project/AuxClasspathEntry")]
assert len(aux) == 1 and Path(aux[0]).name == "jspecify-1.0.1.jar"
assert Path(sb_cmd[sb_cmd.index("-auxclasspathFromFile") + 1]).parent == package_dir.parent
product_names = {path.removesuffix(".class").replace("/", ".") for path in prior["exactLocalClassFiles"]}
reported_names = [node.attrib["class"] for node in sb.findall(".//ClassStats")]
assert len(reported_names) == 9 and set(reported_names) == product_names
assert not (sb.findall(".//BugInstance") or sb.findall(".//MissingClass") or sb.findall(".//Error"))
pmd_sources = pmd_cmd[pmd_cmd.index("-d") + 1]
assert Path(pmd_sources) == package_dir / "src/main/java"
pmd_aux = pmd_cmd[pmd_cmd.index("--aux-classpath") + 1].split(":")
assert len(pmd_aux) == 3 and pmd_aux[:2] == [target, aux[0]] and Path(pmd_aux[2]).name == "jrt-fs.jar"
ns = {"p": pmd.tag.partition("}")[0].removeprefix("{")}
for item in pmd.findall("p:file", ns):
    path = Path(item.attrib["name"])
    assert path.is_relative_to(pmd_sources) and path.stem in expected_sources
assert len(pmd.findall(".//p:violation", ns)) == prior["pmd"]["raw"] == 10
assert not (pmd.findall("p:error", ns) or pmd.findall("p:suppressedviolation", ns))

out = evidence / values["run"]
out.mkdir()
manifest = out / "manifest.json"
record = dict(actualExit=0, source=core, startEvent=start["eventId"], prior=pin(prior_path),
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), spotbugsTarget=target,
              spotbugsReportedNineClasses=sorted(reported_names), spotbugsAux=aux,
              spotbugsReport=pin(sb_report), spotbugsFindings=0, pmdSourceDir=pmd_sources,
              pmdAux=pmd_aux, pmdReport=pin(pmd_report), preservedPmdRaw=10, exactSourceCount=8,
              commandsReplayed=0, productOrToolJarReads=0, wholeF03=False, whole451=False, formalDelta=0)
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(pin(manifest), len(reported_names))
