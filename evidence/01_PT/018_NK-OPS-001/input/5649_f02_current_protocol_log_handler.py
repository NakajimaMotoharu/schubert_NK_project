"""Apply the amended file-constructor rule to the currently admitted Protocol JAR."""

from datetime import datetime, timezone
import gzip
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5629_f02_current_protocol_archive_rule.py")))
OPS, PLAN, P, JAVA, ARCH, SLF = (H[n] for n in ("OPS", "PLAN", "P", "JAVA", "ARCH", "SLF"))
git, pin, dump, execute, read = (H[n] for n in ("git", "pin", "dump", "execute", "read"))
TOOL = H["H"]["TOOL"]


def main():
    ctx = read(next(PLAN.glob("1688_*.json")))["values"]
    red_path = OPS / ctx["run"] / "manifest.json"
    green_path = next(OPS.glob("PG41288-*/manifest.json"))
    precedent = next(OPS.glob("PG41224-*/manifest.json"))
    red, green, old = map(read, (red_path, green_path, precedent))
    source = git("rev-parse", "HEAD").decode().strip()
    assert green["source"] == source and green["productionCore"] == ctx["productionCoreMain"]
    assert red["targetedMisses"] == 4 and green["targetedMisses"] == 0
    assert green["findings"] == 23 and green["requalifiedEarlierDecisions"] == 35
    assert {r["testId"] for r in red["fixtures"]} == {r["testId"] for r in green["fixtures"]}
    assert not git("diff", "--name-only", old["core"], ctx["productionCoreMain"],
                   "--", "pom.xml", "src/pom.xml", "src/schubert-nk-protocol")
    assert old["productModuleCoverage"] == "1/6" and old["protocolPhysical"] == 176
    archive = Path(old["exactArchive"]["path"])
    assert pin(archive) == old["exactArchive"]
    allowed = Path(old["allowedNames"]["path"])
    assert pin(allowed) == old["allowedNames"]
    with gzip.open(allowed, "rt") as file:
        names = {line.split()[0] for line in file if line.lstrip().startswith(P + "protocol.")}
    with ZipFile(archive) as jar:
        physical = [name.removesuffix(".class").replace("/", ".")
                    for name in jar.namelist() if name.endswith(".class")]
    assert set(physical) == names and len(physical) == len(names) == 176
    body = git("show", f"{source}:{TOOL}")
    assert H["H"]["sha"](body) == green["auditorSha256"]
    assert all(pin(path)["sha256"] == value for path, value in H["H"]["PINS"].items())
    modules = sorted(set(H["H"]["MODULES"]) - {"protocol"})
    out = OPS / "PG41290-f02-current-protocol-file-handler-v1"
    out.mkdir()
    steps = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-file-handler-protocol-") as temp:
        scratch = Path(temp)
        code = scratch / TOOL.name
        code.write_bytes(body)
        lib = os.pathsep.join(map(str, (ARCH, SLF)))
        javac = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        anchors = []
        for module in modules:
            anchor = scratch / module / "UnrelatedAnchor.java"
            anchor.parent.mkdir()
            anchor.write_text(f"package {P}{module}; public final class UnrelatedAnchor {{}}\n")
            anchors.append(anchor)
        for name, cmd in (
            ("auditor", [*javac, "-cp", lib, "-d", scratch / "tool", code]),
            ("anchors", [*javac, "-d", scratch / "bin", *anchors]),
        ):
            steps[name], _ = execute(out, name, cmd, scratch)
            assert steps[name]["actualExit"] == 0
        args = [f"protocol={archive}"]
        for module in modules:
            jar = scratch / (module + ".jar")
            H["H"]["archive"](jar, [P + module + ".UnrelatedAnchor"], scratch / "bin")
            args.append(f"{module}={jar}")
        steps["audit"], report = execute(out, "audit", [JAVA, "-cp",
            str(scratch / "tool") + os.pathsep + lib, "ModuleDependencyAudit", *args], scratch)
    table = [row.split("\t") for row in report.splitlines()]
    assert ["ARCHUNIT", "1.4.2", "181", "181"] in table and steps["audit"]["actualExit"] == 0
    result = {row[1]: int(row[2]) for row in table if row[0] == "RULE"}
    assert result == old["ruleViolations"] == dict.fromkeys(H["H"]["RULES"], 0)
    dependencies, calls = next(tuple(map(int, row[1:])) for row in table if row[0] == "INSPECTED")
    assert (dependencies, calls) == (old["inspectedDependencies"], old["inspectedCodeCalls"])
    assert {row[1]: int(row[2]) for row in table if row[0] == "MODULE"} == {
        "protocol": 176, **dict.fromkeys(modules, 1)}
    protocol_sources = git("ls-files", "src/schubert-nk-protocol/src/main/java").decode().splitlines()
    assert len(protocol_sources) == 169 and all(path.endswith(".java") for path in protocol_sources)
    admitted = next(OPS.glob("PG41100-*/manifest.json"))
    outcomes = read(admitted)["controllerSourcePins"]
    assert len(outcomes) == 13 and all(pin(Path(row["path"])) == row for row in outcomes)
    assert all(b"FileHandler" not in git("show", f"{source}:{path}")
               for path in [*protocol_sources, *(row["path"] for row in outcomes)])
    dump(out / "manifest.json", dict(
        actualExit=0, source=source, core=ctx["productionCoreMain"], prior=pin(precedent),
        numericProtocolClassCount=len(physical), verifiedInputs=old["exactArchive"],
        syntheticOtherModules=len(modules), verdicts=result, dependencies=dependencies, calls=calls,
        testFixtures=pin(green_path), inspectedProtocolJavaFiles=len(protocol_sources),
        admittedControllerFiles=len(outcomes), admittedControllerPins=pin(admitted), productTests=0,
        classInitializersRun=0, wholeF02=False, whole451=False, formalDelta=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(), steps=steps))
    print(pin(out / "manifest.json"), dependencies, calls)


if __name__ == "__main__":
    main()
