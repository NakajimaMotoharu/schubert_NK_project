"""SS311 entrypoint boundary canaries. Never initialize a target class."""
from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

PREVIOUS = runpy.run_path(str(Path(__file__).with_name("5666_f02_image_xml_file.py")))
H, MAKE, FILELOG = PREVIOUS["H"], PREVIOUS["C"]["write_fixture"], PREVIOUS["FILELOG"]
P, FENCE = H["P"], PREVIOUS["FENCE"]
JDBC = "java.sql.Connection"
FILES = "java.nio.file.Files"
JMS = "jakarta.jms.Message"
JMS_CONTEXT = "jakarta.jms.JMSContext"
PATH = "java.nio.file.Path"
STORAGE = P + "storage.ListenerFixtureValue"
SQL_INPUT = "public void sql(java.sql.Connection connection) {}"
DIRECT_FILE = (
    "public boolean exists(java.nio.file.Path path) { return java.nio.file.Files.exists(path); }"
)
JMS_ONE = "public void onMessage(jakarta.jms.Message message) {}"
JMS_TWO = "public void onMessage(jakarta.jms.JMSContext context, jakarta.jms.Message message) {}"
CASES = (
    ("api.messaging.inbound.DirectSqlListener", JDBC, SQL_INPUT, True),
    ("api.messaging.inbound.DirectFileListener", FILES, DIRECT_FILE, True),
    ("api.messaging.inbound.NestedSqlListener$Handler", JDBC,
     "public static final class Handler { " + SQL_INPUT + " }", True),
    ("web.synthetic.OrdinaryReplyReceiver", JDBC, JMS_TWO + SQL_INPUT, True),
    ("api.synthetic.MessageEntry", PATH, JMS_ONE +
     'public Object path(java.nio.file.Path base) { return base.resolve("fixture"); }', True),
    ("web.synthetic.StorageReplyReceiver", STORAGE,
     JMS_TWO + "public void read(" + STORAGE + " storage) {}", True),
    ("api.messaging.inbound.BorrowedJmsListener", JMS_CONTEXT, JMS_TWO, False),
    ("api.synthetic.RealDataAdapter", JDBC, SQL_INPUT, False),
    ("web.synthetic.RealFileAdapter", FILES, DIRECT_FILE, False),
    ("api.synthetic.NonJmsReceiver", JDBC, "public void onMessage(String value) {}" + SQL_INPUT, False),
)
SUPPORT_TYPES = {
    JMS: "package jakarta.jms; public interface Message {}",
    JMS_CONTEXT: "package jakarta.jms; public interface JMSContext {}",
}


def run(after):
    git, execute = H["git"], H["execute"]
    context, = H["PLAN"].glob("1761_*.json")
    cfg = FILELOG["R"]["read"](context)["values"]
    tool = H["TOOL"]
    current = git("rev-parse", "HEAD").decode().strip()
    before = git("show", f'{cfg["source"]}:{tool}')
    assert H["sha"](before) == cfg["oracleReferences"][-1]["sha256"]
    code = git("show", f"{current}:{tool}")
    assert (before != code) == after
    assert not git("diff", "--name-only", cfg["source"], current, "--", "src")
    out = H["OPS"] / ("PG41390-f02-listener-owner-green-v1" if after else cfg["run"])
    out.mkdir()
    steps = {}
    prior = set()
    java = H["JAVA"]
    libs = os.pathsep.join(str(H[k]) for k in ("ARCH", "SLF"))
    wanted = {(FENCE, P + owner, target) for owner, target, _, denied in CASES if denied}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-listener-fence-") as directory:
        root = Path(directory)
        tool_source = root / tool.name
        tool_source.write_bytes(code)
        sources = [MAKE(root, P + owner.split("$", 1)[0], body) for owner, _, body, _ in CASES]
        sources.append(MAKE(root, STORAGE, FILELOG["C"]["MARKER"]))
        if after:
            sources.extend(FILELOG["cases"](root, FILELOG["CASES"], prior))
            sources.extend(FILELOG["known"](root, prior))
            for owner, target, body, rule, denied in PREVIOUS["CASES"]:
                sources.append(MAKE(root, P + owner, body))
                if denied:
                    prior.add((rule, P + owner, target))
        prior_test_count = len(sources) - len(CASES) - 1
        sources.extend(MAKE(root, P + module + ".Anchor", FILELOG["C"]["MARKER"])
                       for module in H["MODULES"])
        for name, body in SUPPORT_TYPES.items():
            source = root / (name.replace(".", "/") + ".java")
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(body + "\n")
            sources.append(source)
        javac = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        for step, argv in (
            ("compile-tool", [*javac, "-cp", libs, "-d", root / "audit", tool_source]),
            ("compile-synthetic", [*javac, "-d", root / "classes", *sources]),
        ):
            steps[step], _ = execute(out, step, argv, root)
            assert steps[step]["actualExit"] == 0
        classdir = root / "classes"
        owned = [
            path.relative_to(classdir).as_posix().removesuffix(".class").replace("/", ".")
            for path in sorted(classdir.rglob("*.class"))
            if path.relative_to(classdir).as_posix().startswith(P.replace(".", "/"))
        ]
        args = []
        for mod in H["MODULES"]:
            jar = root / (mod + ".jar")
            H["archive"](jar, [name for name in owned if name.startswith(P + mod + ".")], classdir)
            args.append(f"{mod}={jar}")
        steps["audit"], _ = execute(out, "audit", [java, "-cp", str(root / "audit") + os.pathsep + libs,
                                                  "ModuleDependencyAudit", *args], root)
    found = FILELOG["SUPPORT"]["published_findings"](out / "audit.stdout.txt")
    assert found == (wanted | prior if after else set()), (found - (wanted | prior), (wanted | prior) - found)
    assert steps["audit"]["actualExit"] == int(after)
    outcomes = [
        dict(testId=f"PT-F02-LISTENER{i:03}", origin=P+owner, target=target, expected=deny,
             observed=(FENCE, P+owner, target) in found)
        for i, (owner, target, _, deny) in enumerate(CASES, 1)
    ]
    H["dump"](out / "manifest.json", dict(
        run=out.name, actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), source=current,
        core=cfg["productionCoreMain"], toolSha256=H["sha"](code), cases=outcomes,
        priorSyntheticStaticCases=prior_test_count, priorExpectedFindings=len(prior), physical=len(owned),
        missingExpected=sum(row["expected"] != row["observed"] for row in outcomes),
        actualProductTestRuns=0, actualRuntimeCalls=0, heldTypesOpened=0, formalDelta=0,
        wholeF02=False, whole451=False, steps=steps))
    print(out.name, len(found), prior_test_count)


if __name__ == "__main__":
    run(sys.argv[1] == "green")
