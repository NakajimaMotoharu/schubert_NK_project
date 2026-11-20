"""Classify direct JDK file handlers from synthetic bytecode without loading a fixture."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


ARCHIVE = runpy.run_path(str(Path(__file__).with_name("5626_f02_file_archive_dependency.py")))
H, C, R, SUPPORT = (ARCHIVE[name] for name in ("H", "C", "R", "SUPPORT"))
P = H["P"]
CONTROLLER = ARCHIVE["CONTROLLER"]
FENCE = ARCHIVE["FENCE"]
FILE = "java.util.logging.FileHandler"
STREAM = "java.util.logging.StreamHandler"
MEMORY = "java.util.logging.MemoryHandler"
CASES = (
    ("web.synthetic.DefaultLogController", FILE, "", "", CONTROLLER, True),
    ("web.synthetic.NamedLogController", FILE, "String pattern", "pattern", CONTROLLER, True),
    ("protocol.DefaultLogSink", FILE, "", "", FENCE, True),
    ("protocol.RollingLogSink", FILE, "String pattern", "pattern, 4096, 2", FENCE, True),
    ("web.synthetic.StreamLogController", STREAM, "java.io.OutputStream stream",
     "stream, new java.util.logging.SimpleFormatter()", CONTROLLER, False),
    ("protocol.MemoryLogSink", MEMORY, "java.util.logging.Handler target",
     "target, 8, java.util.logging.Level.WARNING", FENCE, False),
    ("web.synthetic.OwnedLogAdapter", FILE, "String pattern", "pattern", CONTROLLER, False),
    ("batch.OwnedLogAdapter", FILE, "String pattern", "pattern", FENCE, False),
)


def cases(scratch, definitions, wanted):
    attach = C["write_fixture"]
    sources = []
    for owner, target, params, args, rule, forbidden in definitions:
        origin = P + owner
        sources.append(attach(scratch, origin,
                              f"public {target} assemble({params}) throws java.io.IOException "
                              f"{{ return new {target}({args}); }}"))
        if forbidden:
            wanted.add((rule, origin, target))
    return sources


def known(scratch, findings):
    attach = C["write_fixture"]
    sources = cases(scratch, ARCHIVE["CASES"], findings)
    old = ARCHIVE["old_controller"]
    for name, target, params, args, forbidden in old["CASES"]:
        owner = old["CONTROLLER"] + name + "Controller"
        sources.append(attach(scratch, owner,
                              f"public {target} open({params}) throws java.io.IOException "
                              f"{{ return new {target}({args}); }}"))
        if forbidden:
            findings.add((CONTROLLER, owner, target))
    sources.append(attach(scratch, old["CONTROLLER"] + "FileAdapter",
                          "public java.io.PrintWriter open(String path) throws java.io.IOException "
                          "{ return new java.io.PrintWriter(path); }"))
    prior = ARCHIVE["prior"]
    for owner, text, forbidden in prior["CASES"]:
        sources.append(attach(scratch, P + owner, text))
        if forbidden:
            findings.add((FENCE, P + owner, prior["PATH"]))
    return sources


def main(after, recover=False):
    pin, git, execute = (H[name] for name in ("pin", "git", "execute"))
    ctx = R["read"](next(H["PLAN"].glob("1688_*.json")))["values"]
    assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"][:-1])
    if not after:
        assert pin(H["TOOL"]) == ctx["oracleReferences"][-1]
    src = git("rev-parse", "HEAD").decode().strip()
    assert not git("diff", "--name-only", ctx["source"], src, "--", "src")
    assert git("rev-parse", "origin/main").decode().strip() == ctx["canonicalDesignSource"]
    old = git("show", f'{ctx["source"]}:{H["TOOL"]}')
    body = git("show", f"{src}:{H['TOOL']}")
    assert (body != old) == after and H["sha"](old) == ctx["oracleReferences"][-1]["sha256"]
    run = "PG41288-f02-jdk-file-handler-fixed-v1" if after else ctx["run"]
    output = H["OPS"] / run
    if recover:
        assert not after and not (output / "manifest.json").exists()
        commands = {name: R["read"](output / (name + "-exit.json"))
                    for name in ("compile-auditor", "compile-fixtures", "audit", "jdk")}
        assert all(value["actualExit"] == 0 for value in commands.values())
        return post(ctx, output, src, body, commands, set(), set(), after, True)
    output.mkdir()
    java = H["JAVA"]
    libraries = os.pathsep.join(str(H[key]) for key in ("ARCH", "SLF"))
    javac = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    commands = {}
    wanted, retained = set(), set()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-file-handler-") as path:
        scratch = Path(path)
        tool = scratch / H["TOOL"].name
        tool.write_bytes(body)
        sources = cases(scratch, CASES, wanted)
        if after:
            sources.extend(known(scratch, retained))
            assert len(sources) == 43 and len(retained) == 19
        sources.extend(C["write_fixture"](scratch, P + module + ".Anchor", C["MARKER"])
                       for module in H["MODULES"])
        for name, command in (
            ("compile-auditor", [*javac, "-cp", libraries, "-d", scratch / "tool", tool]),
            ("compile-fixtures", [*javac, "-d", scratch / "classes", *sources]),
        ):
            commands[name], _ = execute(output, name, command, scratch)
            assert commands[name]["actualExit"] == 0
        owners, _ = ARCHIVE["prior"]["fixture_owners"](scratch / "classes")
        args = []
        for module, entries in sorted(owners.items()):
            jar = scratch / (module + ".jar")
            H["archive"](jar, entries, scratch / "classes")
            args.append(f"{module}={jar}")
        class_path = str(scratch / "tool") + os.pathsep + libraries
        commands["audit"], _ = execute(output, "audit",
            [java, "-cp", class_path, "ModuleDependencyAudit", *args], scratch)
        commands["jdk"], _ = execute(output, "jdk",
            [java.with_name("javap"), "-p", "-c", FILE], scratch)
        assert commands["jdk"]["actualExit"] == 0
    post(ctx, output, src, body, commands, wanted, retained, after, False)


def post(ctx, output, src, body, commands, wanted, retained, after, recovered):
    findings = SUPPORT["published_findings"](output / "audit.stdout.txt")
    assert findings == (wanted | retained if after else set())
    assert commands["audit"]["actualExit"] == int(after)
    audit = (output / "audit.stdout.txt").read_text().splitlines()[0].split("\t")
    assert audit[:2] == ["ARCHUNIT", "1.4.2"] and audit[2] == audit[3]
    jdk = (output / "jdk.stdout.txt").read_text()
    direct_opens = jdk.count("// Method openFiles:()V")
    delegations = jdk.count('// Method "<init>":(Ljava/lang/String;JIZ)V')
    assert direct_opens == 5 and delegations == 1
    report = [
        dict(testId=f"PT-F02-LOGFILE{i:03}", origin=P + origin, target=target, rule=rule,
             expected=expected, observed=(rule, P + origin, target) in findings)
        for i, (origin, target, _, _, rule, expected) in enumerate(CASES, 1)
    ]
    manifest = output / "manifest.json"
    H["dump"](manifest, dict(run=output.name, source=src, productionCore=ctx["productionCoreMain"],
        auditorSha256=H["sha"](body), findings=len(findings), fixtures=report,
        targetedMisses=sum(r["expected"] != r["observed"] for r in report),
        requalifiedEarlierDecisions=35 if after else 0, previousExpectedFindings=len(retained),
        physical=int(audit[2]), fixtureInitializations=0, fileOpens=0, actualProductTests=0,
        bytecodePostRecoveredFromExisting=recovered, directJdkOpens=direct_opens,
        delegatedJdkOpen=delegations,
        formalDelta=0, wholeF02=False, whole451=False, stages=commands,
        terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(H["pin"](manifest), len(report), len(findings))


if __name__ == "__main__":
    main(*{"before": (False,), "before-read": (False, True), "after": (True,)}[sys.argv[1]])
