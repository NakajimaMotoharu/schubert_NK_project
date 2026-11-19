"""Run explicit fixed-wire suites on the approved Protocol JAR in a local scratch directory."""

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
}


def read(path):
    return json.loads(Path(path).read_bytes())


def main(suite="lgs"):
    pattern, simple_name, count, session = SUITES[suite]
    test = "dev.codex.schubert.nk.protocol.codec." + simple_name
    source_path = "src/schubert-nk-protocol/src/test/java/" + test.replace(".", "/") + ".java"
    start = read(next(COMMON["PLAN"].glob(pattern)))
    plan = start["values"]
    pin, git, execute = (COMMON[key] for key in ("pin", "git", "execute"))
    assert all(pin(Path(row["path"])) == row for row in plan["oracleReferences"])
    jar_manifest = read(plan["oracleReferences"][1]["path"])
    assert jar_manifest["sourceCore"] == plan["productionCoreMain"]
    selected = jar_manifest["jars"]["protocol"]
    jar = Path(selected["artifact"]["path"])
    assert pin(jar) == selected["artifact"] and selected["classes"] == 176
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
    out = (EVIDENCE / plan["run"]).resolve()
    out.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-protocol-wire-") as temp:
        work = Path(temp)
        fixture = work / (simple_name + ".java")
        fixture.write_bytes(git("show", f"{source}:{source_path}"))
        sources = work / "sources.txt"
        sources.write_text(str(fixture) + "\n")
        cp = os.pathsep.join(map(str, (jar, junit, annotations)))
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
        result = dict(run=plan["run"], actualExit=next((row["actualExit"] for row in results.values()
                                                       if row["actualExit"] != 0), 0),
                      session=session, source=source, productionCore=plan["productionCoreMain"],
                      testFixture=source_path, testSha256=pin(fixture)["sha256"], jar=selected["artifact"],
                      jarOwnership=dict(uid=ownership.st_uid, mode=oct(stat.S_IMODE(ownership.st_mode)),
                                        regularFile=True, sameBeforeAndAfter=True),
                      scopes=["protocol"], selectedTests=count, executedPreviouslyApprovedTests=0,
                      stages=results, actualBackendActions=0, whole451Accepted=False,
                      terminalAtUTC=COMMON["timestamp"]())
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), result["actualExit"])
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
