"""Run only the new Unicode oracle against already qualified in-memory parser bytes."""

import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

COMMON = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
EVIDENCE = COMMON["OPS"]
DESIGN = "dev.codex.schubert.nk.api.logging.RequestLogDetailsTest"
APIPREFIX = "dev/codex/schubert/nk/api/logging/"
PROTOPREFIX = "dev/codex/schubert/nk/protocol/"
TEST = ("src/schubert-nk-api/src/test/java/" + APIPREFIX + "RequestLogDetailsTest.java")
TARGETS = {
    "api": [APIPREFIX + "RequestLogDetails", APIPREFIX + "package-info"],
    "protocol": [PROTOPREFIX + "codec/PermanentProtocolException",
                 PROTOPREFIX + "layout/semantic/UserRole", PROTOPREFIX + "layout/semantic/WireEnum"],
}
RUN = "PG40216-p01809-request-details-scalar-guard-v2"
METHOD = "rejectsMalformedUnicodeInKeysAndFamilyButPreservesAsciiEscapes"


def read(file):
    return json.loads(Path(file).read_bytes())


def main():
    pin, git, sha, execute = (COMMON[k] for k in ("pin", "git", "sha", "execute"))
    start = read(next(COMMON["PLAN"].glob("673_P01809*")))
    values = start["values"]
    assert all(pin(Path(item["path"])) == item for item in values["oracleReferences"])
    prepare = read(values["oracleReferences"][0]["path"])
    former_post = read(values["oracleReferences"][1]["path"])
    assert former_post["actualExit"] == 0 and former_post["all457CrcBound"]
    assert prepare["heldFourClassfileActions"] == 0
    source = git("rev-parse", "HEAD").decode().strip()
    assert not git("diff", "--name-only", values["productionCoreMain"], source, "--",
                   "src", ":(exclude)src/**/src/test/**")
    assert set(git("diff", "--name-only", values["source"], source, "--", "src").decode().splitlines()) == {TEST}
    compiled = [Path(entry) for entry in prepare["classPath"].split(os.pathsep)
                if not entry.endswith(".jar")]
    fixture_dirs = {path.parents[1].name.removeprefix("schubert-nk-"): path for path in compiled}
    assert all(path.name == "classes" and path.parent.name == "target" for path in compiled)
    assert len(fixture_dirs) == len(compiled) and TARGETS.keys() <= fixture_dirs.keys()
    tools = COMMON["TC"]
    java = tools / "jdk-25.0.4/bin/java"
    junit = tools / "junit-platform-console-standalone-1.13.4.jar"
    jacoco_agent = tools / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    jacoco_cli = tools / "org.jacoco.cli-0.8.15-nodeps.jar"
    formatter = tools / "google-java-format-1.36.1-all-deps.jar"
    dependencies = [Path(name) for name in prepare["jars"]]
    assert all(pin(dep)["sha256"] == prepare["jars"][str(dep)] for dep in dependencies)
    out = (EVIDENCE / RUN).resolve()
    out.mkdir()
    bundle = read(next(EVIDENCE.glob("PG40210-*/begin.json")))
    assert all(pin(Path(item["path"])) == item for item in bundle["toolAndRulePins"])
    old_begin = read(next(EVIDENCE.glob("PG40128-*/begin.json")))
    assert pin(java) == old_begin["jdk"] and pin(java.with_name("javac")) == old_begin["javaC"]
    assert pin(jacoco_agent)["sha256"] == old_begin["tools"][jacoco_agent.name]["sha256"]
    assert pin(jacoco_cli)["sha256"] == old_begin["tools"][jacoco_cli.name]["sha256"]

    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-request-details-scalar-") as temp:
        work = Path(temp)
        narrowed = work / "owned-inputs"
        physical = {}
        for module, classnames in TARGETS.items():
            for name in classnames:
                label = name + ".class"
                oldclass = fixture_dirs[module] / label
                data = oldclass.read_bytes()
                expected = prepare["physicalClassHashes"][module][label]
                assert sha(data) == expected
                dest = narrowed / label
                dest.parent.mkdir(exist_ok=True, parents=True)
                dest.write_bytes(data)
                original = f"src/schubert-nk-{module}/src/main/java/{name}.java"
                assert sha(git("show", f"{source}:{original}")) == prepare["inputHashes"][original]
                physical[label] = expected

        test_file = work / "RequestLogDetailsTest.java"
        test_file.write_bytes(git("show", f"{source}:{TEST}"))
        source_files = out / "sources.txt"
        source_files.write_text(str(test_file) + "\n")
        cp = os.pathsep.join(map(str, [narrowed, *dependencies]))
        compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        checkstyle = bundle["commands"]["checkstyle"][:]
        checkstyle[checkstyle.index("-o") + 1] = out / "checkstyle.xml"
        checkstyle[-1] = "@" + str(source_files)
        pmd = bundle["commands"]["pmd"][:]
        pmd[pmd.index("--file-list") + 1] = source_files
        pmd[pmd.index("--aux-classpath") + 1] = cp + os.pathsep + str(java.parents[1] / "lib/jrt-fs.jar")
        pmd[pmd.index("--report-file") + 1] = out / "pmd.xml"
        scopes = out / "xml"
        scopes.mkdir(mode=0o700)
        execution = out / "jacoco.exec"
        init = work / "class-init.log"
        receipts = {}
        phases = {
            "format": [java, "-jar", formatter, "--skip-reflowing-long-strings", "--dry-run",
                       "--set-exit-if-changed", test_file],
            "compile": [*compiler, "-cp", cp, "-d", work / "tests", test_file],
            "pmd": pmd,
            "checkstyle": checkstyle,
            "unit": [java, "-Xmx256m", f"-Xlog:class+init=info:file={init}",
                     f"-javaagent:{jacoco_agent}=destfile={execution},sessionid=PG40214-REQUEST-DETAILS-UTF16,append=false",
                     "-jar", junit, "execute", "--disable-banner", "--details=summary",
                     "--fail-if-no-tests", "--class-path", str(work / "tests") + os.pathsep + cp,
                     "--reports-dir", scopes, "--select-method", DESIGN + "#" + METHOD,
                     "--config=junit.jupiter.execution.parallel.enabled=false"],
            "report": [java, "-jar", jacoco_cli, "report", execution, "--classfiles",
                       narrowed / (APIPREFIX + "RequestLogDetails.class"), "--xml", out / "coverage.xml"],
        }
        for label, command in phases.items():
            receipts[label], _ = execute(out, label, command, work)
            if receipts[label]["actualExit"] not in ((0, 4) if label == "pmd" else (0,)):
                break
        if init.is_file():
            import gzip
            with (out / "class-init.log.gz").open("xb") as stream:
                stream.write(gzip.compress(init.read_bytes(), mtime=0))
        actual = next((r["actualExit"] for name, r in receipts.items()
                       if r["actualExit"] not in ((0, 4) if name == "pmd" else (0,))), 0)
        manifest = dict(actualExit=actual, source=source, productionCore=values["productionCoreMain"],
                        selectedMethod=METHOD, testSourceSha256=sha(test_file.read_bytes()), archivedMain=physical,
                        historicalParser=values["oracleReferences"][:2], stages=receipts,
                        changedMain=0, previousTestsExecuted=0, newFormalAcceptance=0,
                        terminalAtUTC=COMMON["timestamp"]())
        COMMON["dump"](out / "manifest.json", manifest)
    print(pin(out / "manifest.json"), {name: r["actualExit"] for name, r in receipts.items()})
    return actual


if __name__ == "__main__":
    raise SystemExit(main())
