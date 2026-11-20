"""Check the Controller file rule against constructor signatures and stream-only controls."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


base = runpy.run_path(str(Path(__file__).with_name("5571_f02_protocol_path_io.py")))
H, C, R, SUPPORT = (base[k] for k in ("H", "C", "R", "SUPPORT"))
CONTROLLER = H["P"] + "web.synthetic."
RULE = "CONTROLLER_BOUNDARY"
CASES = (
    ("WriterName", "java.io.PrintWriter", "String name", "name", True),
    ("StreamName", "java.io.PrintStream", "String name", "name, java.nio.charset.StandardCharsets.UTF_8", True),
    ("FormatterName", "java.util.Formatter", "String name", "name", True),
    ("WriterFile", "java.io.PrintWriter", "java.io.File file", "file", True),
    ("StreamFile", "java.io.PrintStream", "java.io.File file", "file", True),
    ("FormatterFile", "java.util.Formatter", "java.io.File file", "file", True),
    ("ScannerFile", "java.util.Scanner", "java.io.File file", "file", True),
    ("ScannerPath", "java.util.Scanner", "java.nio.file.Path path", "path, java.nio.charset.StandardCharsets.UTF_8", True),
    ("WriterStream", "java.io.PrintWriter", "java.io.Writer writer", "writer", False),
    ("PrintStream", "java.io.PrintStream", "java.io.OutputStream stream", "stream", False),
    ("FormatterBuffer", "java.util.Formatter", "java.lang.Appendable buffer", "buffer", False),
    ("ScannerContent", "java.util.Scanner", "String text", "text", False),
    ("ScannerStream", "java.util.Scanner", "java.io.InputStream stream", "stream", False),
    ("DirectFile", "java.io.File", "String name", "name", True),
)


def main(after):
    pin, git, execute = (H[k] for k in ("pin", "git", "execute"))
    start_path, = H["PLAN"].glob("1591_*.json")
    context = R["read"](start_path)["values"]
    assert all(pin(Path(row["path"])) == row for row in context["oracleReferences"])
    assert all(pin(path)["sha256"] == want for path, want in H["PINS"].items())
    source = git("rev-parse", "HEAD").decode().strip() if after else context["source"]
    meter = H["TOOL"]
    data = git("show", f"{source}:{meter}")
    assert (H["sha"](data) != context["oracleReferences"][-1]["sha256"]) is after
    assert not git("diff", "--name-only", context["source"], source, "--", "src")
    out = H["OPS"] / ("PG41168-f02-controller-file-ctor-green-v1" if after else context["run"])
    out.mkdir()
    java = H["JAVA"]
    cp = os.pathsep.join(str(H[key]) for key in ("ARCH", "SLF"))
    strict = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    steps = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-controller-ctor-") as dirname:
        root = Path(dirname)
        code = root / meter.name
        code.write_bytes(data)
        fixtures = [C["write_fixture"](root, H["P"]+m+".Anchor", C["MARKER"]) for m in H["MODULES"]]
        expected = []
        for label, target, parameters, arguments, should_report in CASES:
            owner = CONTROLLER + label + "Controller"
            code_body = f"public {target} open({parameters}) throws java.io.IOException {{ return new {target}({arguments}); }}"
            fixtures.append(C["write_fixture"](root, owner, code_body))
            expected.append((owner, target, should_report))
        owner = CONTROLLER + "FileAdapter"
        target = "java.io.PrintWriter"
        fixtures.append(C["write_fixture"](root, owner,
            f"public {target} open(String path) throws java.io.IOException {{ return new {target}(path); }}"))
        expected.append((owner, target, False))
        for stage, command in (("compile-tool", [*strict, "-cp", cp, "-d", root/"tool", code]),
                               ("compile-fixture", [*strict, "-d", root/"binary", *fixtures])):
            steps[stage], _ = execute(out, stage, command, root)
            assert steps[stage]["actualExit"] == 0
        owners, physical = base["fixture_owners"](root/"binary")
        argv = []
        for name, types in sorted(owners.items()):
            jar = root / (name+".jar")
            H["archive"](jar, types, root/"binary")
            argv.append(f"{name}={jar}")
        steps["audit"], _ = execute(out, "audit",
            [java,"-cp",str(root/"tool")+os.pathsep+cp,"ModuleDependencyAudit",*argv],root)
    found = SUPPORT["published_findings"](out/"audit.stdout.txt")
    assert steps["audit"]["actualExit"] == 1
    want = {(RULE,o,t) for o,t,invalid in expected if invalid}
    assert found == (want if after else {(RULE, CONTROLLER+"DirectFileController", "java.io.File")})
    cases = [dict(testId=f"PT-F02-WEB-FILE-CTOR-{i:03}",origin=o,target=t,expected=bad,
                  observed=(RULE,o,t) in found) for i,(o,t,bad) in enumerate(expected,1)]
    result = out/"manifest.json"
    H["dump"](result,dict(actualExit=0, toolSource=source, productionCore=context["productionCoreMain"],
                         toolSourceSha256=H["sha"](data), cases=cases,
                         missingBeforeOrAfter=sum(c["expected"] != c["observed"] for c in cases),
                         inspectedFixtureClasses=len(physical), fileSystemFixtureExecuted=0,
                         steps=steps, productOperations=0, formalDelta=0, whole451=False,
                         terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(result),len(cases),len(found))


if __name__ == "__main__":
    main({"before":False,"after":True}[sys.argv[1]])
