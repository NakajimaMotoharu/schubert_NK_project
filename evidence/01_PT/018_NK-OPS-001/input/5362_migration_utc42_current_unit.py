"""Execute retained synthetic migration tests against the two UTC changes."""

from collections import Counter
import gzip
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
OPS, PLAN, JAVA = (H[key] for key in ("OPS", "PLAN", "JAVA"))
SCOPE = "dev/codex/schubert/nk/migration/"
PACKAGE = SCOPE.replace("/", ".")
MAIN = ("MigrationGamesVerifier", "MigrationMasterContentVerifier")
TESTS = (*[name + "Test" for name in MAIN], "MigrationMasterTargetPublisherTest")
MODULE = Path("src/schubert-nk-bootstrap/src")
SOURCE = "2cc96ab800b8753b0f0eafac8e008bd5b69d9a59"
DESIGN = "6dcd9fb65a3dad2011abeac1babc75e52394785d"
RUN = "PG40450-migration-utc42-proxy-87-v1"


def read(path):
    return json.loads(Path(path).read_bytes())


def source_files(scope, types, root):
    output, pins = [], {}
    for name in types:
        path = MODULE / scope / "java" / SCOPE / (name + ".java")
        public = root / path
        public.parent.mkdir(exist_ok=True, parents=True)
        data = H["git"]("show", f"{SOURCE}:{path}")
        public.write_bytes(data)
        pins[str(path)] = H["sha"](data)
        output.append(public)
    return output, pins


def verify_xml(root, expected):
    observed = {}
    result = ElementTree.parse(root / "TEST-junit-jupiter.xml").getroot()
    for case in result.findall("testcase"):
        key = (case.get("classname"), case.get("name"))
        assert key not in observed
        observed[key] = next((tag for tag in ("failure", "error", "skipped")
                              if case.find(tag) is not None), "pass")
    assert set(observed) == expected
    return Counter(observed.values())


def main():
    pin, git, execute, sha = (H[key] for key in ("pin", "git", "execute", "sha"))
    start = read(next(PLAN.glob("869_*")))
    change = start["values"]
    source_main = change["productionCoreMain"]
    refs = change["oracleReferences"]
    assert git("rev-parse", "HEAD").decode().strip() == SOURCE
    assert git("rev-parse", "origin/main").decode().strip() == DESIGN
    assert all(pin(Path(ref["path"])) == ref for ref in refs[:5] if ref is not refs[2])
    assert "getObject(5, OffsetDateTime.class)" in git("show", f"{DESIGN}:{refs[2]['path']}").decode()
    assert "getTimestamp" not in git("show", f"{DESIGN}:{refs[2]['path']}").decode()
    primary = read(refs[5]["path"])
    history_pins = read(refs[-1]["path"])
    assert pin(Path(refs[5]["path"])) == refs[5] and pin(Path(refs[-1]["path"])) == refs[-1]
    assert pin(Path(history_pins["prepare"]["path"])) == history_pins["prepare"]
    history = read(history_pins["prepare"]["path"])
    assert primary["sourceCore"] == source_main
    bootstrap = primary["jars"]["bootstrap"]["artifact"]
    bootstrap_path = Path(bootstrap["path"])
    assert pin(bootstrap_path) == bootstrap
    old_classes = history["physicalClassHashes"]
    assert len(old_classes) == 73 and all(p.startswith(SCOPE) for p in old_classes)
    targets = {SCOPE + name + ".class" for name in MAIN}
    assert targets <= set(old_classes)
    previous = read(next(OPS.glob("PG40128-*/begin.json")))
    assert pin(JAVA) == previous["jdk"]
    pins = {Path(ref["path"]): ref["sha256"] for ref in previous["tools"].values()
            if Path(ref["path"]).name in ("junit-platform-console-standalone-1.13.4.jar",
                                         "org.jacoco.cli-0.8.15-nodeps.jar",
                                         "org.jacoco.agent-0.8.15-runtime.jar")}
    pins.update({Path(p): h for p, h in history["dependencies"].items()})
    assert all(pin(p)["sha256"] == h for p, h in pins.items())

    def artifact(prefix):
        return next(p for p in pins if p.name.startswith(prefix))

    junit, agent, cli = (artifact(n) for n in ("junit-platform", "org.jacoco.agent", "org.jacoco.cli"))
    model = os.pathsep.join(map(str, (artifact("jspecify"), artifact("jsr305"))))
    selectors = {PACKAGE + name for name in TESTS}
    expected = {(r["classname"], r["name"]) for r in history["expectedCases"]
                if r["classname"] in selectors}
    assert len(expected) == 87
    out = OPS / RUN
    out.mkdir()
    report = out / "xml"
    report.mkdir()
    metrics = out / "jacoco.exec"
    compiler = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    stages = {}
    prior_changes = {}
    physical = {}
    counts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-migration-utc42-") as directory:
        root = Path(directory)
        classes, tests = root / "classes", root / "tests"
        trace = root / "class-init.log"
        main_paths, main_pins = source_files("main", MAIN, root)
        test_paths, test_pins = source_files("test", TESTS, root)
        with ZipFile(bootstrap_path) as archive:
            for item, old_hash in sorted(old_classes.items()):
                data = archive.read(item)
                value = sha(data)
                if value != old_hash:
                    prior_changes[item] = value
                if item not in targets:
                    path = classes / item
                    path.parent.mkdir(exist_ok=True, parents=True)
                    path.write_bytes(data)
                    physical[item] = value
        bundled_prior = {
            "AssetStagingTables.class", "AssetStagingTables$Table.class",
            "MigrationMasterColumnVerifier.class", "MigrationMasterConstraintVerifier.class",
            "MigrationMasterContentVerifier.class", "MigrationMasterFinalizer.class",
            "MigrationMasterReferenceVerifier.class",
        }
        assert set(prior_changes) == {SCOPE + name for name in bundled_prior}
        cp = str(classes) + os.pathsep + model
        sequence = dict(
            main=[*compiler, "-cp", cp, "-d", classes, *main_paths],
            tests=[*compiler, "-cp", cp + os.pathsep + str(junit), "-d", tests, *test_paths],
            unit=[JAVA, "-Duser.timezone=Pacific/Honolulu", f"-Xlog:class+init=info:file={trace}",
                  f"-javaagent:{agent}=destfile={metrics.resolve()},sessionid={RUN},append=false",
                  "-jar", junit, "execute", "--disable-banner", "--fail-if-no-tests", "--details=summary",
                  "--class-path", str(tests) + os.pathsep + cp, "--reports-dir", report.resolve(),
                  "--config=junit.jupiter.execution.parallel.enabled=false",
                  *(f"--select-class={name}" for name in sorted(selectors))],
            standard=[JAVA, "-jar", cli, "report", metrics.resolve(), "--classfiles", classes,
                      "--xml", (out / "coverage.xml").resolve()],
        )
        for stage, command in sequence.items():
            stages[stage], _ = execute(out, stage, command, root)
            if stages[stage]["actualExit"] != 0:
                break
        physical = {p.relative_to(classes).as_posix(): pin(p)["sha256"] for p in sorted(classes.rglob("*.class"))}
        if trace.exists():
            trace_data = trace.read_bytes()
            assert all(protected not in trace_data for protected in (
                b"TemporaryInfrastructureException", b"FingerprintKeyRing",
                b"ResponseSnapshotCodec", b"WebStartupException"))
            (out / "class-init.log.gz").write_bytes(gzip.compress(trace_data, mtime=0))
        if (report / "TEST-junit-jupiter.xml").is_file():
            counts = verify_xml(report, expected)
        if (out / "coverage.xml").is_file():
            assert set(physical) == set(old_classes)
            assert all(physical[name] != old_classes[name] for name in targets)
            raw = read(next(OPS.glob("PG40422-*/manifest.json")))["stages"]["raw"]["command"]
            stages["raw"], _ = execute(out, "raw", [*raw[:5], metrics.resolve(),
                *(classes / name for name in sorted(targets))], root)
    checked = (len(stages) == 5 and all(r["actualExit"] == 0 for r in stages.values())
               and counts == {"pass": 87})
    terminal = dict(actualExit=0 if checked else 1, source=SOURCE, productionCore=SOURCE,
                    retainedBaselineCore=source_main, canonicalDesign=DESIGN, admission=history_pins["prepare"],
                    previousCurrentJar=bootstrap, inputPins={**main_pins, **test_pins},
                    expected=87, outcome=counts, stages=stages, runtimeTimezone="Pacific/Honolulu",
                    changedSinceHistory=prior_changes, exactCurrentPhysical=physical, affectedClasses=sorted(targets),
                    scriptsAndConfigs={"runner": pin(Path(__file__).relative_to(Path.cwd()))},
                    tools={str(p): value for p, value in pins.items()}, actualDbSessions=0, actualBackendActions=0,
                    whole451Accepted=False, formalDelta=0, terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", terminal)
    print(pin(out / "manifest.json"), counts)
    return terminal["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
