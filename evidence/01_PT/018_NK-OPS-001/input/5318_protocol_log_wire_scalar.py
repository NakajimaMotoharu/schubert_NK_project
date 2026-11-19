"""Run explicit fixed-wire and YAML boundary suites on approved local JARs."""

import gzip
import json
import os
from pathlib import Path
import runpy
import stat
import sys
from tempfile import TemporaryDirectory

COMMON = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
EVIDENCE = COMMON["OPS"]
SUITES = {
    "lgs": ("682_*", "LogSearchWireUnicodeTest", 2, "PG40226-PROTOCOL-LOG-WIRE"),
    "qss-nts": ("687_*", "QuestionNotificationWireTest", 4, "PG40232-PROTOCOL-QSS-NTS"),
    "qss-nts-retest": ("687_*", "QuestionNotificationWireTest", 4, "PG40234-PROTOCOL-QSS-NTS"),
    "usr": ("692_*", "UserListReplyWireTest", 4, "PG40240-PROTOCOL-USR-REPLY"),
    "usr-retest": ("692_*", "UserListReplyWireTest", 4, "PG40242-PROTOCOL-USR-REPLY"),
    "user-command": ("748_*", "UserCommandWireUnicodeTest", 4, "PG40292-PROTOCOL-USER-COMMAND"),
    "yaml-limit": ("751_*", "NonSecretYamlUtf8LimitTest", 2, "PG40296-BOOTSTRAP-YAML-LIMIT"),
}
RETESTS = {
    "qss-nts-retest": ("PG40234-protocol-qss-nts-fixed-wire-retest-v1", "unit", 1),
    "usr-retest": ("PG40242-protocol-user-list-fixed-wire-retest-v1", "pmd", 4),
}


def read(path):
    return json.loads(Path(path).read_bytes())


def main(suite="lgs"):
    pattern, simple_name, count, session = SUITES[suite]
    module, package, classes = (
        ("bootstrap", "api.bootstrap", 201)
        if suite == "yaml-limit"
        else ("protocol", "protocol.codec", 176)
    )
    test = f"dev.codex.schubert.nk.{package}.{simple_name}"
    source_path = f"src/schubert-nk-{module}/src/test/java/" + test.replace(".", "/") + ".java"
    start = read(next(COMMON["PLAN"].glob(pattern)))
    plan = start["values"]
    pin, git, execute = (COMMON[key] for key in ("pin", "git", "execute"))
    for row in plan["oracleReferences"]:
        path = row["path"]
        if suite == "yaml-limit" and path.endswith("/4241_APIWeb設定原十四通常単体仕様.md"):
            assert COMMON["sha"](git("show", f"{plan['source']}:{path}")) == row["sha256"]
        else:
            assert pin(Path(path)) == row
    jar_manifest = read(plan["oracleReferences"][1]["path"])
    assert jar_manifest["sourceCore"] == plan["productionCoreMain"]
    selected = jar_manifest["jars"][module]
    jar = Path(selected["artifact"]["path"])
    assert pin(jar) == selected["artifact"] and selected["classes"] == classes
    ownership = jar.lstat()
    assert stat.S_ISREG(ownership.st_mode) and jar.resolve() == jar
    assert ownership.st_uid == os.getuid() and not ownership.st_mode & stat.S_IWOTH
    source = git("rev-parse", "HEAD").decode().strip()
    assert not git("diff", "--name-only", plan["productionCoreMain"], source, "--",
                   "src", ":(exclude)src/**/src/test/**")

    old_unit = read(next(EVIDENCE.glob("PG40128-*/begin.json")))
    rules = read(next(EVIDENCE.glob("PG40210-*/begin.json")))
    assert all(pin(Path(row["path"])) == row for row in rules["toolAndRulePins"])
    java = Path(old_unit["jdk"]["path"])
    compiler = java.with_name("javac")
    assert pin(java) == old_unit["jdk"] and pin(compiler) == old_unit["javaC"]

    def tool(name):
        saved = old_unit["tools"][name]
        p = Path(saved["path"])
        assert pin(p) == saved
        return p

    junit = tool("junit-platform-console-standalone-1.13.4.jar")
    agent = tool("org.jacoco.agent-0.8.15-runtime.jar")
    cli = tool("org.jacoco.cli-0.8.15-nodeps.jar")
    annotations = tool("jspecify-1.0.1.jar")
    dependencies = []
    if module == "bootstrap":
        storage = jar_manifest["jars"]["storage"]["artifact"]
        assert pin(Path(storage["path"])) == storage
        stored = read(plan["oracleReferences"][3]["path"])["dependencies"]
        yaml = next(path for path in stored if path.endswith("/snakeyaml-engine-3.1.1.jar"))
        assert pin(Path(yaml))["sha256"] == stored[yaml]
        dependencies = [storage, pin(Path(yaml))]
    run = plan["run"]
    if suite in RETESTS:
        run, failed_stage, expected_exit = RETESTS[suite]
        initial = read(EVIDENCE / plan["run"] / "manifest.json")
        assert initial["stages"][failed_stage]["actualExit"] == expected_exit
        assert initial["jar"] == selected["artifact"]
    out = (EVIDENCE / run).resolve()
    out.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-protocol-wire-") as temp:
        work = Path(temp)
        fixture = work / (simple_name + ".java")
        fixture.write_bytes(git("show", f"{source}:{source_path}"))
        sources = work / "sources.txt"
        sources.write_text(str(fixture) + "\n")
        cp = os.pathsep.join([str(jar), str(junit), str(annotations),
                             *(entry["path"] for entry in dependencies)])
        pmd = rules["commands"]["pmd"][:]
        pmd[pmd.index("--file-list") + 1] = sources
        pmd[pmd.index("--aux-classpath") + 1] = cp + os.pathsep + str(java.parents[1] / "lib/jrt-fs.jar")
        pmd[pmd.index("--report-file") + 1] = out / "pmd.xml"
        check = rules["commands"]["checkstyle"][:]
        check[check.index("-o") + 1] = out / "checkstyle.xml"
        check[-1] = "@" + str(sources)
        xml = out / "xml"
        xml.mkdir()
        execution = out / "jacoco.exec"
        init = work / "class-init.log"
        commands = {
            "format": [*rules["commands"]["format"][:6], fixture],
            "compile": [compiler, "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                        "-cp", cp, "-d", work / "tests", fixture],
            "pmd": pmd,
            "checkstyle": check,
            "unit": [java, "-Xmx256m", f"-Xlog:class+init=info:file={init}",
                     f"-javaagent:{agent}=destfile={execution},sessionid={session},append=false",
                     "-jar", junit, "execute", "--disable-banner", "--details=summary",
                     "--fail-if-no-tests", "--class-path", str(work / "tests") + os.pathsep + cp,
                     "--reports-dir", xml, "--select-class", test],
            "coverage": [java, "-jar", cli, "report", execution, "--classfiles", jar,
                         "--xml", out / "coverage.xml"],
        }
        results = {}
        for label, command in commands.items():
            results[label], _ = execute(out, label, command, work)
            if results[label]["actualExit"] != 0:
                break
        if init.is_file():
            (out / "class-init.log.gz").write_bytes(gzip.compress(init.read_bytes(), mtime=0))
        final = jar.lstat()
        assert (final.st_dev, final.st_ino, final.st_uid, final.st_mode, final.st_mtime_ns) == (
            ownership.st_dev, ownership.st_ino, ownership.st_uid, ownership.st_mode, ownership.st_mtime_ns
        )
        assert pin(jar) == selected["artifact"]
        assert all(pin(Path(entry["path"])) == entry for entry in dependencies)
        result = dict(run=run, actualExit=next((row["actualExit"] for row in results.values()
                                                       if row["actualExit"] != 0), 0),
                      session=session, source=source, productionCore=plan["productionCoreMain"],
                      testFixture=source_path, testSha256=pin(fixture)["sha256"], jar=selected["artifact"],
                      jarOwnership=dict(uid=ownership.st_uid, mode=oct(stat.S_IMODE(ownership.st_mode)),
                                        regularFile=True, sameBeforeAndAfter=True),
                      scopes=[module], selectedTests=count, executedPreviouslyApprovedTests=0,
                      stages=results, actualBackendActions=0, whole451Accepted=False,
                      terminalAtUTC=COMMON["timestamp"]())
    if dependencies:
        result["localDependencyPins"] = dependencies
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), result["actualExit"])
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
