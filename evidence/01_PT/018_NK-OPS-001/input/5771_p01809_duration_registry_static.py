"""Bind a current in-memory duration registry fixture to the original immutable SDK."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from zipfile import ZipFile


ROOT = Path.cwd()
LOCALS = (ROOT.parent / "pgpt-runs/PG379").resolve()
PUBLIC = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
CORE = "87927ea17c1c8dbef528bc0c6882c24b1fe7c871"
PACKAGE = "dev/codex/schubert/nk/api/monitoring"
TEST = "ExactDurationMeterRegistryTest"
MAIN_NAMES = (
    "ExactDurationMeterRegistry", "ExactDurationSupport",
    "DbQueryDurationMetricRecorder", "MqProcessingDurationMetricRecorder", "package-info",
)
MAIN_CLASS_NAMES = set(MAIN_NAMES) | {
    "ExactDurationMeterRegistry$ExactSummary", "DbQueryDurationMetricRecorder$Outcome",
    "DbQueryDurationMetricRecorder$Query", "MqProcessingDurationMetricRecorder$Outcome",
}
FIXTURE_CLASS_NAMES = {TEST + name for name in ("", "$1", "$2", "$FaultRegistry", "$GenericRegistry", "$Probe")}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def load(path):
    return json.loads(path.read_bytes())


def at():
    return datetime.now(timezone.utc).isoformat()


def verify(root, names):
    assert {p.relative_to(root).as_posix() for p in root.rglob("*.class")} == {
        f"{PACKAGE}/{name}.class" for name in names
    }


def main(folder, run_tests):
    folder = folder.resolve()
    folder.mkdir(mode=0o700)
    for name in ("target/classes", "test", "owned-temp", "xml"):
        (folder / name).mkdir(parents=True)
    head = git("rev-parse", "HEAD").decode().strip()
    old_path, = PUBLIC.glob("PG25592*-preflight-v1/manifest.json")
    old = load(old_path)
    proof, = PUBLIC.glob("PG43066*/manifest.json")
    regular = load(proof)["normalArtifacts"]["protocol"]
    protocol = Path(regular["jar"]["path"])
    assert pin(protocol) == regular["jar"]
    assert git("rev-parse", f"{CORE}:src/schubert-nk-protocol/src/main").decode().strip() == regular["mainTree"]
    roster = load(LOCALS / "PG43018-f02-sax-direct-file-v1/current-protocol-v2/scope-proof.json")
    assert roster["protocolJar"] == regular["jar"]
    with ZipFile(protocol) as archive:
        assert sorted(n for n in archive.namelist() if n.endswith(".class")) == sorted(roster["exactPermittedPhysicalNames"])
    base = Path("src/schubert-nk-api/src")
    main = [base / "main/java" / PACKAGE / f"{name}.java" for name in MAIN_NAMES]
    test = base / "test/java" / PACKAGE / f"{TEST}.java"
    assert all(git("show", f"{CORE}:{path}") == path.read_bytes() for path in main)
    assert git("show", f"{head}:{test}") == test.read_bytes()
    for path in main:
        if str(path) in old["inputHashes"]:
            assert pin(path)["sha256"] == old["inputHashes"][str(path)]
    assert (pin(test)["sha256"] != old["inputHashes"][str(test)]) == run_tests

    dependencies = old["vendorJars"] | {
        name: digest for name, digest in old["dependencies"].items()
        if Path(name).name in ("jspecify-1.0.1.jar", "junit-platform-console-standalone-1.13.4.jar",
                               "org.jacoco.agent-0.8.15-runtime.jar")
    }
    for name, digest in dependencies.items():
        assert pin(Path(name))["sha256"] == digest
    annotation, = [name for name in dependencies if name.endswith("/jspecify-1.0.1.jar")]
    junit, = [name for name in dependencies if name.endswith("console-standalone-1.13.4.jar")]
    agent, = [name for name in dependencies if name.endswith("-runtime.jar")]
    vendor = list(old["vendorJars"])
    aux = os.pathsep.join([str(protocol), annotation, *vendor])
    mains = folder / "target/classes"
    tests = folder / "test"
    fixture_cp = os.pathsep.join([str(mains), junit, aux])
    framework = ROOT.parent / "toolchain/jdk-25.0.4"
    java, javac = [str(framework / "bin" / name) for name in ("java", "javac")]
    compile_flags = ["--release", "25", "-g", "-proc:none", "-implicit:none", "-Xlint:all", "-Werror"]
    stages = {
        "compileMain": [javac, *compile_flags, "-cp", aux, "-d", str(mains), *map(str, main)],
        "compileFixture": [javac, *compile_flags, "-cp", fixture_cp, "-d", str(tests), str(test)],
    }
    old_static = LOCALS / "PG43064-transfer-test-checked-declaration-v1"
    for key in ("style", "pmd", "spotbugs"):
        prior = load(old_static / "begin.json")["commands"][key]
        if key == "style":
            stages[key] = [*prior[:-2], str(test)]
        else:
            position = prior.index("--aux-classpath" if key == "pmd" else "-auxclasspath") + 1
            stages[key] = [str(arg).replace(str(old_static), str(folder)) for arg in prior]
            stages[key][position] = fixture_cp
            if key == "spotbugs":
                assert stages[key][-2:] == [str(mains), str(tests)]
                stages[key].pop(-2)
    (folder / "current-static-sources.txt").write_text(str(test) + "\n")
    if run_tests:
        stages["junit"] = [
            java, "-Dfile.encoding=UTF-8", "-Duser.timezone=Asia/Tokyo",
            "-Djunit.jupiter.extensions.autodetection.enabled=false",
            "-Djunit.jupiter.execution.parallel.enabled=false",
            "-Djunit.jupiter.execution.timeout.default=20 s",
            f"-Djava.io.tmpdir={folder / 'owned-temp'}",
            f"-javaagent:{agent}=destfile={folder / 'unit.exec'},append=false,sessionid={folder.name}",
            "-cp", os.pathsep.join([str(tests), fixture_cp]), "org.junit.platform.console.ConsoleLauncher",
            "execute", "--disable-ansi-colors", "--fail-if-no-tests", "--reports-dir", str(folder / "xml"),
            "--select-class", PACKAGE.replace("/", ".") + "." + TEST,
        ]
        (folder / "meter").mkdir()
        earlier = LOCALS / "PG43080-scenario-stream-finite-current-v1"
        coverage = load(earlier / "begin.json")["commands"]
        stages["rawCompile"] = [arg.replace(str(earlier), str(folder)) for arg in coverage["rawCompile"]]
        stages["unfiltered"] = [
            *(arg.replace(str(earlier), str(folder)) for arg in coverage["unfiltered"][:-1]),
            str(mains / PACKAGE / "ExactDurationMeterRegistry.class"),
            str(mains / PACKAGE / "ExactDurationMeterRegistry$ExactSummary.class"),
        ]
    start = dict(source=head, productCore=CORE, startedAtUTC=at(), main=[pin(p) for p in main],
                 test=pin(test), protocol=pin(protocol), vendor=dependencies, stages=stages,
                 fixtureAdmitted=pin(old_path), runtimeTests=run_tests)
    (folder / "begin.json").write_text(json.dumps(start, indent=2)+"\n")
    receipts = {}
    for name, command in stages.items():
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120)
        for stream in ("stdout", "stderr"):
            (folder / f"{name}.{stream}").write_bytes(getattr(completed, stream))
        receipts[name] = dict(actualExit=completed.returncode, terminalAtUTC=at())
        print(name, completed.returncode, flush=True)
        permitted = {"pmd": {0, 4}, "spotbugs": {0, 1}}.get(name, {0})
        if completed.returncode not in permitted:
            raise SystemExit(completed.returncode)
        if name == "compileMain":
            verify(mains, MAIN_CLASS_NAMES)
        if name == "compileFixture":
            verify(tests, FIXTURE_CLASS_NAMES)
    result = dict(actualExit=0, terminalAtUTC=at(), source=head, stages=receipts,
                  mainPhysical=sorted(MAIN_CLASS_NAMES), fixturePhysical=sorted(FIXTURE_CLASS_NAMES))
    (folder / "terminal.json").write_text(json.dumps(result, indent=2)+"\n")


if __name__ == "__main__":
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument("folder", type=Path)
    options.add_argument("--changed-fixture", action="store_true")
    args = options.parse_args()
    main(args.folder, args.changed_fixture)
