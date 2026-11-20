from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
import hashlib
import json
import subprocess


def fixed(revision, path):
    return subprocess.check_output(["git", "show", f"{revision}:{path}"])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
begin_path = next(plan.glob("1214_*"))
begin = json.loads(begin_path.read_bytes())
ctx = begin["values"]
core = ctx["productionCoreMain"]
ops = Path("evidence/01_PT/018_NK-OPS-001/evidence")
package_path = next(ops.glob("PG40802-*/manifest.json"))
package = json.loads(package_path.read_bytes())
assert package["source"] == core and package["actualExit"] == 0
assert all(package["steps"][phase]["exit"] == 0 for phase in ("compile", "jar"))
assert package["heldClassfilesProvidedToAnalyzers"] == 0
modules = ("protocol", "storage", "bootstrap", "batch", "api", "web")
dirs = {m:f"src/schubert-nk-{m}" for m in modules}
root_bytes = fixed(core,"pom.xml")
root = ET.fromstring(root_bytes)
assert set(m.text for m in root.findall("{*}modules/{*}module")) == {*dirs.values(), "program/characterization"}
assert not root.findall("{*}dependencies/{*}dependency")
assert not root.findall("{*}profiles/{*}profile/{*}modules/{*}module")
design_path = next(Path("documents/300_SS/310_アプリケーション").glob("311_*"))
design_source = ctx["canonicalDesignSource"]
design_bytes = fixed(design_source, design_path)
design = design_bytes.decode()
assert all(s in design for s in ("WebとAPIは互いにcompile/runtime依存しない。",
    "bootstrapはStorageだけを内部依存とする", "schubert-nk-batch", "SSC142", "SSC-461"))
expect_compile = {"protocol":set(), "storage":set(), "bootstrap":{"storage"},
    "batch":{"bootstrap","storage"}, "api":{"bootstrap","storage","protocol"}, "web":{"bootstrap","storage","protocol"}}
expect_test = {"protocol":set(), "storage":set(), "bootstrap":set(),
    "batch":{("bootstrap","test-jar")}, "api":{("bootstrap","test-jar")}, "web":{("api","jar"),("bootstrap","test-jar")}}
deps, poms = {}, [dict(path="pom.xml",sha256=sha(root_bytes))]
for name,directory in dirs.items():
    path = f"{directory}/pom.xml"
    data = fixed(core, path)
    pom = ET.fromstring(data)
    assert pom.findtext("{*}artifactId") == f"schubert-nk-{name}"
    assert pom.findtext("{*}parent/{*}artifactId") == "schubert-nk"
    active = set()
    tests = set()
    for dep in pom.findall("{*}dependencies/{*}dependency"):
        if dep.findtext("{*}groupId") != "dev.codex.schubert":
            continue
        target = dep.findtext("{*}artifactId")
        assert target.startswith("schubert-nk-")
        edge = (target.removeprefix("schubert-nk-"),dep.findtext("{*}type","jar"))
        scope = dep.findtext("{*}scope","compile")
        if scope == "test":
            assert edge not in tests
            tests.add(edge)
        else:
            assert scope == "compile" and edge[1] == "jar" and edge[0] not in active
            active.add(edge[0])
        assert dep.findtext("{*}version") == "${project.version}"
    assert active == expect_compile[name] and tests == expect_test[name]
    assert not any(dep.findtext("{*}groupId") == "dev.codex.schubert"
                   for dep in pom.findall("{*}profiles/{*}profile/{*}dependencies/{*}dependency"))
    deps[name] = dict(compile=sorted(active),test=sorted(tests))
    poms.append(dict(path=path,sha256=sha(data)))
present = set(package["packaged"])
assert present == {"protocol","storage","bootstrap","batch"}
assert all(expect_compile[m] <= present for m in present)
assert set(package["metadataOnlyModules"]) == {*(f"{dirs[m]}/pom.xml" for m in set(modules)-present), "program/characterization/pom.xml"}
old_issue_path = next(ops.glob("PG38580-*/manifest.json"))
old_issue = json.loads(old_issue_path.read_bytes())
storage_path = "src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/StorageIoException.java"
assert old_issue["actualExit"] != 0 and len(old_issue["findings"]) == 1 and "java.sql.SQLException" in old_issue["findings"][0]
roster_path = next(ops.glob("PG40702-*/manifest.json"))
roster = json.loads(roster_path.read_bytes())
assert b"java.sql.SQLException" in fixed(core, storage_path)
scope_prior = roster["candidateProductionSource"]
assert isinstance(scope_prior,str)
assert not subprocess.check_output(["git","diff","--name-only",scope_prior,core,"--",
    "src/schubert-nk-storage/src/main", "src/schubert-nk-bootstrap/src/main"])
result = dict(actualExit=0,startEvent=begin["eventId"],core=core,canonicalSS311=dict(path=str(design_path),revision=design_source,
    sha256=sha(design_bytes)), poms=poms, declarations=deps, characterizationReactorProject="program/characterization", currentFourPackage=pin(package_path), currentPackagedModules=sorted(present),
    awaitingCurrentBuild=sorted(set(modules)-present), businessWebToApiCompileEdges=0, webToApiTestOnly=True,
    legacyStorageJdbcSource=dict(path=storage_path,sha256=sha(fixed(core,storage_path))),
    ssc461Reference=pin(roster_path), historicalPhysicalFinding=pin(old_issue_path), replayedBuilds=0, jarsOpened=0,
    actualTypeBoundaryRuns=0, wholeSixBuild=False, completeModuleBoundary=False, whole451=False, formalDelta=0,
    terminalAtUTC=datetime.now(timezone.utc).isoformat(),runner=pin(Path(__file__)))
out = ops/"PG40820-f02-declared-four-package-boundary-v2"/"manifest.json"
out.parent.mkdir()
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(pin(out))
