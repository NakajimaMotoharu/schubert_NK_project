"""Execute retained synthetic migration tests against the two UTC changes."""

from collections import Counter
import gzip
import json
import os
from pathlib import Path
import re
import runpy
from stat import S_IMODE
import sys
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
RUN = "PG40452-migration-utc42-proxy-87-typed-v1"
MAVEN_RUN = "PG40462-migration-utc42-maven-exact87-v1"
SQL_CLOSURE = {
    "AssetStagingTables": ("SqlMutation", "SqlQuery"),
    "MigrationMasterColumnVerifier": ("SqlQuery",),
    "MigrationMasterConstraintVerifier": ("SqlQuery",),
    "MigrationMasterContentVerifier": ("SqlQuery",),
    "MigrationMasterFinalizer": ("SqlMutation", "SqlPrepare", "SqlQuery"),
    "MigrationMasterReferenceVerifier": ("SqlQuery",),
}


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


def pack_text(out, receipt):
    for channel in ("stdout", "stderr"):
        item = receipt[channel]
        old = Path(item["path"])
        new = old.with_suffix(".log.gz")
        new.write_bytes(gzip.compress(old.read_bytes(), mtime=0))
        receipt[channel] = {**H["pin"](new), "expandedSha256": item["sha256"]}
        old.unlink()
    (out / "unit-exit.json").write_text(json.dumps(receipt, indent=2) + "\n")


def main(packaged=False):
    pin, git, execute, sha = (H[key] for key in ("pin", "git", "execute", "sha"))
    start = read(next(PLAN.glob("869_*")))
    change = start["values"]
    source_main = change["productionCoreMain"]
    refs = change["oracleReferences"]
    assert not git("diff", "--name-only", SOURCE, "HEAD", "--", "src")
    assert git("rev-parse", "origin/main").decode().strip() == DESIGN
    assert all(pin(Path(refs[i]["path"])) == refs[i] for i in (0, 1, 3, 4))
    assert "getObject(5, OffsetDateTime.class)" in git("show", f"{DESIGN}:{refs[2]['path']}").decode()
    assert "getTimestamp" not in git("show", f"{DESIGN}:{refs[2]['path']}").decode()
    primary = read(refs[5]["path"])
    history_pins = read(refs[-1]["path"])
    assert pin(Path(refs[5]["path"])) == refs[5] and pin(Path(refs[-1]["path"])) == refs[-1]
    assert pin(Path(history_pins["prepare"]["path"])) == history_pins["prepare"]
    history = read(history_pins["prepare"]["path"])
    assert primary["sourceCore"] == source_main
    bootstrap = primary["jars"]["bootstrap"]["artifact"]
    run = RUN
    source_alignment = None
    package_receipt = None
    if packaged:
        run = MAVEN_RUN
        receipt = read(next(PLAN.glob("875_*")))
        assert receipt["values"]["productionCoreMain"] == SOURCE and receipt["values"]["run"] == run
        package_ref = receipt["values"]["oracleReferences"][2]
        alignment_ref = receipt["values"]["oracleReferences"][1]
        assert pin(Path(package_ref["path"])) == package_ref and pin(Path(alignment_ref["path"])) == alignment_ref
        package_receipt = read(package_ref["path"])
        source_alignment = read(alignment_ref["path"])
        assert package_receipt["sourceCore"] == source_alignment["productionCore"] == SOURCE
        assert source_alignment["newPackageReceipt"] == package_ref
        bootstrap = package_receipt["packagedJars"]["bootstrap"]["artifact"]
        assert bootstrap == source_alignment["qualifiedLocalArtifacts"]["bootstrap"]["artifact"]
    bootstrap_path = Path(bootstrap["path"])
    assert pin(bootstrap_path) == bootstrap
    assert S_IMODE(bootstrap_path.lstat().st_mode) == 0o600 and bootstrap_path.lstat().st_uid == os.getuid()
    old_classes = history["physicalClassHashes"]
    assert len(old_classes) == 73 and all(p.startswith(SCOPE) for p in old_classes)
    companions = {SCOPE + f"{owner}${name}.class" for owner, names in SQL_CLOSURE.items() for name in names}
    assert len(companions) == 9 and not (companions & old_classes.keys())
    for owner, nested in SQL_CLOSURE.items():
        path = MODULE / "main" / "java" / SCOPE / (owner + ".java")
        code = git("show", f"{SOURCE}:{path}").decode()
        for name in nested:
            assert re.search(r"private interface " + name + r"\s*\{", code), (str(path), name)
    targets = {SCOPE + name + ".class" for name in MAIN}
    assert targets <= set(old_classes)
    recompiled = targets | {SCOPE + "MigrationMasterContentVerifier$SqlQuery.class"}
    full_scope = old_classes.keys() | companions
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
    out = OPS / run
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
            for item in sorted(full_scope):
                data = archive.read(item)
                value = sha(data)
                if item in old_classes and value != old_classes[item]:
                    prior_changes[item] = value
                if packaged or item not in recompiled:
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
        if packaged:
            bundled_prior.add("MigrationGamesVerifier.class")
        assert set(prior_changes) == {SCOPE + name for name in bundled_prior}
        cp = str(classes) + os.pathsep + model
        sequence = dict(
            main=[*compiler, "-cp", cp, "-d", classes, *main_paths],
            closure=[JAVA.with_name("jdeps"), "-verbose:class", "-filter:none", "--ignore-missing-deps",
                     "--class-path", model, classes],
            tests=[*compiler, "-cp", cp + os.pathsep + str(junit), "-d", tests, *test_paths],
            unit=[JAVA, "-Duser.timezone=Pacific/Honolulu", f"-Xlog:class+init=info:file={trace}",
                  f"-javaagent:{agent}=destfile={metrics.resolve()},sessionid={run},append=false",
                  "-jar", junit, "execute", "--disable-banner", "--fail-if-no-tests", "--details=summary",
                  "--class-path", str(tests) + os.pathsep + cp, "--reports-dir", report.resolve(),
                  "--config=junit.jupiter.execution.parallel.enabled=false",
                  *(f"--select-class={name}" for name in sorted(selectors))],
            standard=[JAVA, "-jar", cli, "report", metrics.resolve(), "--classfiles", classes,
                      "--xml", (out / "coverage.xml").resolve()],
        )
        if packaged:
            sequence.pop("main")
            assert set(source_alignment["requalificationRequired"]) == targets
            assert all(physical[name] == rec["mavenPackaged"] and physical[name] != rec["javacFixtureRun"]
                       for name, rec in source_alignment["requalificationRequired"].items())
        known = {name.removesuffix(".class").replace("/", ".") for name in full_scope}
        for stage, command in sequence.items():
            stages[stage], stdout = execute(out, stage, command, root)
            if stage == "closure":
                typed = [line.split()[2] for line in stdout.splitlines()
                         if line.startswith(" ") and " -> " in line and line.split()[2].startswith("dev.codex.")]
                missing = set(typed) - known
                H["dump"](out / "closure-result.json", dict(productTypedTargets=len(set(typed)), missing=sorted(missing)))
                assert stages[stage]["actualExit"] == 0 and not missing and set(typed) >= {
                    name.removesuffix(".class").replace("/", ".") for name in companions}
            if stage == "unit":
                pack_text(out, stages[stage])
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
            assert set(physical) == full_scope
            assert all(physical[name] != old_classes[name] for name in targets)
            raw = read(next(OPS.glob("PG40422-*/manifest.json")))["stages"]["raw"]["command"]
            stages["raw"], _ = execute(out, "raw", [*raw[:5], metrics.resolve(),
                *(classes / name for name in sorted(targets))], root)
    checked = (len(stages) == (5 if packaged else 6) and all(r["actualExit"] == 0 for r in stages.values())
               and counts == {"pass": 87})
    terminal = dict(actualExit=0 if checked else 1, source=SOURCE, productionCore=SOURCE,
                    retainedBaselineCore=source_main, canonicalDesign=DESIGN, admission=history_pins["prepare"],
                    previousCurrentJar=bootstrap, inputPins={**main_pins, **test_pins},
                    expected=87, outcome=counts, stages=stages, runtimeTimezone="Pacific/Honolulu",
                    changedSinceHistory=prior_changes, privateSqlCompanions=sorted(companions),
                    exactCurrentPhysical=physical, affectedClasses=sorted(targets),
                    mavenPackagedMainUsed=packaged, samePhysicalMainRecompiled=not packaged,
                    artifactAlignment=(source_alignment["requalificationRequired"] if packaged else None),
                    scriptsAndConfigs={"runner": pin(Path(__file__).relative_to(Path.cwd()))},
                    tools={str(p): value for p, value in pins.items()}, actualDbSessions=0, actualBackendActions=0,
                    whole451Accepted=False, formalDelta=0, terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", terminal)
    print(pin(out / "manifest.json"), counts)
    return terminal["actualExit"]


if __name__ == "__main__":
    assert sys.argv[1:] in ([], ["--packaged-maven"])
    raise SystemExit(main(bool(sys.argv[1:])))
