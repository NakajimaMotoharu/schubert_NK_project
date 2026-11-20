"""Use compiled but never executed fixtures for SS311 file dependency rules."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


prior = runpy.run_path(str(Path(__file__).with_name("5571_f02_protocol_path_io.py")))
old_controller = runpy.run_path(str(Path(__file__).with_name("5605_f02_controller_file_constructors.py")))
H, C, R, SUPPORT = (prior[key] for key in ("H", "C", "R", "SUPPORT"))
P = H["P"]
ZIP = "java.util.zip.ZipFile"
JAR = "java.util.jar.JarFile"
INPUT = "java.util.zip.ZipInputStream"
JAR_INPUT = "java.util.jar.JarInputStream"
CONTROLLER = "CONTROLLER_BOUNDARY"
FENCE = "FRAMEWORK_FENCES"
# The table is an independent SS311 oracle. Names encode the owned operation but no file path.
CASES = (
    ("web.synthetic.ZipNameController", ZIP, "String name", "name", CONTROLLER, True),
    ("web.synthetic.JarFileController", JAR, "java.io.File file", "file", CONTROLLER, True),
    ("web.synthetic.ZipStreamController", INPUT, "java.io.InputStream in", "in", CONTROLLER, False),
    ("web.synthetic.JarStreamController", JAR_INPUT, "java.io.InputStream in", "in", CONTROLLER, False),
    ("web.synthetic.ArchiveFileAdapter", JAR, "String name", "name", CONTROLLER, False),
    ("protocol.ZipFileReader", ZIP, "java.io.File file", "file", FENCE, True),
    ("protocol.JarNameReader", JAR, "String name", "name", FENCE, True),
    ("protocol.ScanningPath", "java.util.Scanner", "java.nio.file.Path path", "path", FENCE, True),
    ("protocol.NamedWriter", "java.io.PrintWriter", "String name", "name", FENCE, True),
    ("protocol.WriterBuffer", "java.io.PrintWriter", "java.io.Writer sink", "sink", FENCE, False),
    ("protocol.ZipBorrowedStream", INPUT, "java.io.InputStream in", "in", FENCE, False),
    ("storage.ArchiveFileAdapter", ZIP, "String name", "name", FENCE, False),
)


def main(after):
    pin, git, execute = (H[key] for key in ("pin", "git", "execute"))
    start, = H["PLAN"].glob("1643_*.json")
    context = R["read"](start)["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in context["oracleReferences"][:-1])
    design = Path(context["oracleReferences"][1]["path"])
    assert "ControllerはJDBC、JMS template、filesystem APIを直接呼ばない" in git(
        "show", f'{context["canonicalDesignSource"]}:{design}').decode()
    assert all(pin(path)["sha256"] == wanted for path, wanted in H["PINS"].items())
    tool = H["TOOL"]
    baseline = git("show", f'{context["source"]}:{tool}')
    assert H["sha"](baseline) == context["oracleReferences"][-1]["sha256"]
    source = git("rev-parse", "HEAD").decode().strip() if after else context["source"]
    body = git("show", f"{source}:{tool}")
    assert (baseline != body) == after
    assert not git("diff", "--name-only", context["source"], source, "--", "src")
    run = "PG41220-f02-archive-owner-fixed-v1" if after else context["run"]
    dest = H["OPS"]/run
    dest.mkdir()
    outputs = {}
    java = H["JAVA"]
    sz = os.pathsep.join(str(H[key]) for key in ("ARCH", "SLF"))
    javac = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    positive = {(rule, P+owner, target) for owner, target, _, _, rule, forbidden in CASES if forbidden}
    previous_wanted = set()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-archive-static-audit-") as name:
        scratch = Path(name)
        sources = []
        code = scratch/tool.name
        code.write_bytes(body)
        marker = C["write_fixture"]
        for owner, target, params, args, _, _ in CASES:
            sources.append(marker(scratch, P+owner,
                f"public {target} assemble({params}) throws java.io.IOException {{ return new {target}({args}); }}"))
        for module in H["MODULES"]:
            sources.append(marker(scratch, P+module+".Anchor", C["MARKER"]))
        if after:
            for name, target, params, args, bad in old_controller["CASES"]:
                owner = old_controller["CONTROLLER"]+name+"Controller"
                sources.append(marker(scratch, owner,
                   f"public {target} open({params}) throws java.io.IOException {{ return new {target}({args}); }}"))
                if bad:
                    previous_wanted.add((CONTROLLER, owner, target))
            sources.append(marker(scratch, old_controller["CONTROLLER"]+"FileAdapter",
                "public java.io.PrintWriter open(String path) throws java.io.IOException { return new java.io.PrintWriter(path); }"))
            for owner, text, bad in prior["CASES"]:
                sources.append(marker(scratch, P+owner, text))
                if bad:
                    previous_wanted.add((FENCE, P+owner, prior["PATH"]))
        for stage, command in (
            ("compile-auditor", [*javac, "-cp", sz, "-d", scratch/"auditor", code]),
            ("compile-synthetic-classes", [*javac, "-d", scratch/"binary", *sources])
        ):
            outputs[stage], _ = execute(dest, stage, command, scratch)
            assert outputs[stage]["actualExit"] == 0
        owners, physical = prior["fixture_owners"](scratch/"binary")
        args = []
        for name, entries in sorted(owners.items()):
            jar = scratch/(name+".jar")
            H["archive"](jar, entries, scratch/"binary")
            args.append(f"{name}={jar}")
        outputs["audit"], _ = execute(dest, "audit",
            [java, "-cp", str(scratch/"auditor")+os.pathsep+sz, "ModuleDependencyAudit", *args], scratch)
    findings = SUPPORT["published_findings"](dest/"audit.stdout.txt")
    # Independently modeled expected output, including previously recognized Controller and Path calls.
    expected = positive | previous_wanted if after else set()
    assert findings == expected, sorted(findings ^ expected)
    assert outputs["audit"]["actualExit"] == int(after)
    records = [
        dict(testId=f"PT-F02-ARCHIVE-{i:03}", owner=P+owner, target=target, rule=rule,
             expected=forbidden, found=(rule, P+owner, target) in findings)
        for i, (owner, target, _, _, rule, forbidden) in enumerate(CASES, 1)
    ]
    receipt = dict(source=source, productionCore=context["productionCoreMain"], actualExit=0,
                   terminalAtUTC=datetime.now(timezone.utc).isoformat(), mainToolSha256=H["sha"](body),
                   run=run, newCases=records, expectedFindings=len(positive),
                   newlyMissed=sum(entry["expected"] != entry["found"] for entry in records),
                   previousScopedCanaryReruns=23 if after else 0,
                   previousScopedFindings=len(previous_wanted), physicalCount=len(physical),
                   productJarInputs=0, fixtureInitializations=0, actualArchiveOpens=0,
                   wholeF02=False, whole451=False, formalDelta=0, stages=outputs)
    result = dest/"manifest.json"
    H["dump"](result, receipt)
    print(pin(result), len(records), len(findings), receipt["newlyMissed"])


if __name__ == "__main__":
    main({"before": False, "after": True}[sys.argv[1]])
