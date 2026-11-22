"""Qualify the two existing immutable snapshot fixtures using current Protocol only."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path.cwd()
LOCALS = (ROOT.parent / "pgpt-runs/PG379").resolve()
PUBLIC = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
RUN = "PG43098-scenario-snapshot-current-six-v1"
PKG = "dev/codex/schubert/nk/api/persistence"
FIXTURES = ("ScenarioDetailSnapshotBoundaryTest", "ScenarioSnapshotShapeTest")
MAIN_NAMES = ("ScenarioDetailSnapshot", "package-info")


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path))


def now():
    return datetime.now(timezone.utc).isoformat()


def receipt(path, data):
    with path.open("x") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def bytes_match(source, path):
    return git("show", f"{source}:{path}") == path.read_bytes()


def check_physical(folder, names):
    assert {path.relative_to(folder).as_posix() for path in folder.rglob("*.class")} == {
        f"{PKG}/{name}.class" for name in names
    }


def main():
    ref = PUBLIC / "PG43096-scenario-snapshot-current-proof-v1/manifest.json"
    spec = read(ref)
    local = LOCALS / RUN
    local.mkdir(mode=0o700)
    for name in ("test", "xml", "owned-temp", "meter"):
        (local / name).mkdir()
    core, source = spec["productCore"], git("rev-parse", "HEAD").decode().strip()
    sources = Path("src/schubert-nk-api/src")
    main_paths = [sources / "main/java" / PKG / (name + ".java") for name in MAIN_NAMES]
    tests = [sources / "test/java" / PKG / (name + ".java") for name in FIXTURES]
    pinned = {row["path"]:row["sha256"] for row in spec["currentInputsAllSameFour"]}
    for path in main_paths + tests:
        assert bytes_match(source, path)
        assert sha(path)==pinned[str(path)]
    for path in main_paths:
        assert bytes_match(core, path)
        p = local / "src/main/java" / path.relative_to(sources / "main/java")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(path.read_bytes())
    protocol = Path(spec["currentRegularJar"]["path"])
    assert pin(protocol) == spec["currentRegularJar"]
    prior_scope = read(LOCALS / "PG43018-f02-sax-direct-file-v1/current-protocol-v2/scope-proof.json")
    assert prior_scope["protocolJar"] == pin(protocol)
    with ZipFile(protocol) as archive:
        classes = sorted(name for name in archive.namelist() if name.endswith(".class"))
    assert classes == sorted(prior_scope["exactPermittedPhysicalNames"]) and len(classes) == 176

    previous = LOCALS / "PG43080-scenario-stream-finite-current-v1"
    data = read(previous / "begin.json")
    prior = data["commands"]
    model = ET.parse(previous / "pom.xml")
    ns = "http://maven.apache.org/POM/4.0.0"
    deps = model.getroot().find(f"{{{ns}}}dependencies")
    storage_dependency, = [dep for dep in deps if (
        dep.findtext(f"{{{ns}}}systemPath") or "").endswith("qualified-storage-exceptions.jar")]
    deps.remove(storage_dependency)
    ET.register_namespace("", ns)
    model.write(local / "pom.xml", encoding="utf-8", xml_declaration=True)
    def adapt(argument):
        return (argument.replace(str(previous), str(local))
            .replace(os.pathsep + str(local / "qualified-storage-exceptions.jar"), "")
            .replace("PG43080-current", RUN)
            .replace("dev/codex/schubert/nk/api/storage/ScenarioRecordStream.class", PKG + "/ScenarioDetailSnapshot.class"))
    stages = {key:[adapt(arg) for arg in prior[key]] for key in (
        "format", "style", "compileNullaway", "fixtures", "junit", "rawCompile", "unfiltered", "pmd", "spotbugs")}
    for key in ("format", "style"):
        stages[key] = stages[key][:-2] + [str(main_paths[0]), *map(str, tests)]
    stages["fixtures"] = stages["fixtures"][:-1] + list(map(str, tests))
    stages["junit"] = stages["junit"][:-2]
    for name in FIXTURES:
        stages["junit"].extend(["--select-class", PKG.replace("/", ".") + "." + name])
    assert stages["unfiltered"][-1] == str(local / "target/classes" / PKG / "ScenarioDetailSnapshot.class")
    formatter_inputs = [main_paths[0], *tests]
    (local / "current-static-sources.txt").write_text("".join(f"{path}\n" for path in formatter_inputs))
    receipt(local / "begin.json",dict(source=source,productCore=core,startedAtUTC=now(),
        commands=stages,inputs=[pin(x) for x in main_paths+tests],pinnedProtocol=pin(protocol),
        priorGate=pin(ref),toolchainReceipt=pin(previous/"begin.json"),isolatedPom=pin(local/"pom.xml"),
        actualFsDbNetworkOrOtherApiInitialization=False))
    jdk = ROOT.parent / "toolchain/jdk-25.0.4"
    outcomes = {}
    for key, command in stages.items():
        process = subprocess.run(command, cwd=ROOT, env={**os.environ,"JAVA_HOME":str(jdk)},
                                 capture_output=True, timeout=120)
        for stream in ("stdout", "stderr"):
            (local / f"{key}.{stream}").write_bytes(getattr(process,stream))
        outcomes[key] = dict(exit=process.returncode,terminalAtUTC=now())
        print(key,process.returncode,flush=True)
        allowed = {"pmd":{0,4},"spotbugs":{0,1}}.get(key,{0})
        if process.returncode not in allowed:
            receipt(local / "failed.json", outcomes)
            raise SystemExit(process.returncode)
        if key == "compileNullaway":
            check_physical(local/"target/classes", MAIN_NAMES)
        if key == "fixtures":
            check_physical(local/"test", FIXTURES)
    receipt(local / "terminal.json",dict(actualExit=0,source=source,productCore=core,
        terminalAtUTC=now(), stages=outcomes, junit=pin(local/"xml/TEST-junit-jupiter.xml"),
        exec=pin(local/"unit.exec"), raw=pin(local/"unfiltered.stdout")))


if __name__ == "__main__":
    main()
