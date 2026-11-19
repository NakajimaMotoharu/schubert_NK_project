"""Run the fixed LGSREQ01 vectors on the approved Protocol JAR in a local scratch directory."""

import gzip
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

COMMON = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
EVIDENCE = COMMON["OPS"]
TEST = "dev.codex.schubert.nk.protocol.codec.LogSearchWireUnicodeTest"
PATH = "src/schubert-nk-protocol/src/test/java/" + TEST.replace(".", "/") + ".java"


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    start = read(next(COMMON["PLAN"].glob("682_*")))
    plan = start["values"]
    pin, git, execute = (COMMON[key] for key in ("pin", "git", "execute"))
    assert all(pin(Path(row["path"])) == row for row in plan["oracleReferences"])
    jar_manifest = read(plan["oracleReferences"][1]["path"])
    assert jar_manifest["sourceCore"] == plan["productionCoreMain"]
    selected = jar_manifest["jars"]["protocol"]
    jar = Path(selected["artifact"]["path"])
    assert pin(jar) == selected["artifact"] and selected["classes"] == 176
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
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-log-wire-") as temp:
        work = Path(temp)
        fixture = work / "LogSearchWireUnicodeTest.java"
        fixture.write_bytes(git("show", f"{source}:{PATH}"))
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
        session = "PG40226-PROTOCOL-LOG-WIRE"
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
                     "--reports-dir", xml, "--select-class", TEST],
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
        result = dict(run=plan["run"], actualExit=next((row["actualExit"] for row in results.values()
                                                       if row["actualExit"] != 0), 0),
                      session=session, source=source, productionCore=plan["productionCoreMain"],
                      testFixture=PATH, testSha256=pin(fixture)["sha256"], jar=selected["artifact"],
                      scopes=["protocol"], selectedTests=2, executedPreviouslyApprovedTests=0,
                      stages=results, actualBackendActions=0, whole451Accepted=False,
                      terminalAtUTC=COMMON["timestamp"]())
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), result["actualExit"])
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
