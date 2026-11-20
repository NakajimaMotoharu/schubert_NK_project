"""Run the seven existing ordinary Cleanup request codec tests against pinned current bytes."""

import gzip
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from zipfile import ZipFile


UPPER = runpy.run_path(str(Path(__file__).with_name("5326_f02_group_lookup_upper.py")))
STORE, PLAN, COMMON = (UPPER[k] for k in ("EVIDENCE", "PLAN", "COMMON"))
PACKAGE = "dev/codex/schubert/nk/batch/"
OUTER = PACKAGE + "platform/CleanupWorkerRequest"
SELECTION = {OUTER, PACKAGE + "platform/CleanupProfile", PACKAGE + "repository/BatchRun"}
TEST = OUTER.replace("/", ".") + "Test"


def main():
    read, pin = UPPER["read"], COMMON["pin"]
    sha, git, dump = (COMMON[k] for k in ("sha", "git", "dump"))
    start = read(next(PLAN.glob("839_*")))
    work = start["values"]
    source = git("rev-parse", "HEAD").decode().strip()
    core = work["productionCoreMain"]
    fixture = work["oracleReferences"][-1]
    assert all(pin(Path(row["path"])) == row for row in work["oracleReferences"][:-1])
    path = fixture["path"]
    before = git("show", f"{work['source']}:{path}")
    after = git("show", f"{source}:{path}")
    assert sha(before) == fixture["sha256"] and sha(before) != sha(after)
    assert git("diff", "--name-only", core, source, "--", "src").decode().splitlines() == [path]
    assert before.count(b"@Test") == after.count(b"@Test") == 7
    assert before[:before.index(b"  @Test")] != after[:after.index(b"  @Test")]
    assert before[before.index(b"  @Test"):before.index(b"  void creq007")] == (
           after[after.index(b"  @Test"):after.index(b"  void creq007")])
    assert after.count(b"get(5, TimeUnit.SECONDS)") == 2
    assert b"workers.shutdownNow();" in after and b"awaitTermination(5, TimeUnit.SECONDS)" in after
    assert b"a.get()" not in after and b"b.get()" not in after
    archive = read(work["oracleReferences"][1]["path"])
    assert archive["sourceCore"] == core
    batch = archive["jars"]["batch"]["artifact"]
    assert pin(Path(batch["path"])) == batch
    inv = read(next(STORE.glob("PG40374-*/compiled-classes.json")))["classHashes"]["batch"]
    base = read(next(STORE.glob("PG40128-*/begin.json")))
    java = Path(base["jdk"]["path"])
    tools = base["tools"]
    assert pin(java) == base["jdk"] and all(pin(Path(row["path"])) == row for row in tools.values())
    junit = Path(tools["junit-platform-console-standalone-1.13.4.jar"]["path"])
    agent = Path(tools["org.jacoco.agent-0.8.15-runtime.jar"]["path"])
    cli = Path(tools["org.jacoco.cli-0.8.15-nodeps.jar"]["path"])
    annotation = Path(tools["jspecify-1.0.1.jar"]["path"])
    old_static = read(next(STORE.glob("PG40210-*/begin.json")))
    output = (STORE / work["run"]).resolve()
    output.mkdir()
    env = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
    stages = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-current-creq7-") as path_name:
        temp = Path(path_name)
        classes = temp / "target"
        testclasses = temp / "test"
        file = temp / "CleanupWorkerRequestTest.java"
        file.write_bytes(after)
        crc64 = runpy.run_path(str(STORE.parent / "input/5257_p01810_broker_evidence_value_post.py"))["crc64"]
        shapes = {}
        with ZipFile(batch["path"]) as jar:
            for name in sorted(SELECTION):
                entry = name + ".class"
                data = jar.read(entry)
                assert sha(data) == inv[entry]
                dest = classes / entry
                dest.parent.mkdir(exist_ok=True, parents=True)
                dest.write_bytes(data)
                shapes[name] = dict(sha256=sha(data), crc64=crc64(data))
        cp = os.pathsep.join(map(str, (classes, junit, annotation)))
        rules = temp / "files.txt"
        rules.write_text(str(file) + "\n")
        checkstyle = old_static["commands"]["checkstyle"][:]
        checkstyle[checkstyle.index("-o") + 1] = output / "checkstyle.xml"
        checkstyle[-1] = "@" + str(rules)
        pmd = old_static["commands"]["pmd"][:]
        pmd[pmd.index("--file-list") + 1] = rules
        pmd[pmd.index("--aux-classpath") + 1] = cp + ":" + str(java.parents[1] / "lib/jrt-fs.jar")
        pmd[pmd.index("--report-file") + 1] = output / "pmd.xml"
        data = output / "jacoco.exec"
        ini = temp / "class-init.log"
        xml = output / "xml"
        xml.mkdir()
        session = "PG40408-CREQ-SEVEN-ORDINARY"
        commands = dict(
            compile=[java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror",
                     "-proc:none", "-cp", cp, "-d", testclasses, file],
            format=[*old_static["commands"]["format"][:6], file],
            checkstyle=checkstyle, pmd=pmd,
            unit=[java, "-Xmx192m", f"-Xlog:class+init=info:file={ini}",
                  f"-javaagent:{agent}=destfile={data},sessionid={session},append=false",
                  "-jar", junit, "execute", "--fail-if-no-tests", "--disable-banner", "--details=summary",
                  "--class-path", os.pathsep.join((str(testclasses), cp)), "--select-class", TEST,
                  "--reports-dir", xml, "--config=junit.jupiter.execution.parallel.enabled=false"],
            coverage=[java, "-jar", cli, "report", data, "--classfiles", classes, "--xml", output / "coverage.xml"])
        for stage, command in commands.items():
            receipt = UPPER["run"](output, stage, command, temp, env)
            limit = {0, 4} if stage == "pmd" else {0}
            stages[stage] = receipt
            if receipt["actualExit"] not in limit:
                break
        if ini.exists():
            (output / "class-init.log.gz").write_bytes(gzip.compress(ini.read_bytes(), mtime=0))
    okay = len(stages) == len(commands) and stages["coverage"]["actualExit"] == 0
    result = dict(actualExit=0 if okay else 1, source=source, productionCore=core,
                  previousFixture=fixture, exactFixture=pin(Path(fixture["path"])), liveJar=batch,
                  inventory=shapes, session=session, stages=stages, actionsPerformedByProductFixture=0,
                  regularJdkThreadsOwned=True, newProductTests=0, whole451Accepted=False, formalDelta=0,
                  terminalAtUTC=COMMON["timestamp"]())
    dump(output / "manifest.json", result)
    print(pin(output / "manifest.json"), {key: value["actualExit"] for key, value in stages.items()})
    return result["actualExit"]


if __name__ == "__main__":
    raise SystemExit(main())
