"""Run the amended dependency audit against the previously admitted exact Protocol JAR."""

from datetime import datetime, timezone
import gzip
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from zipfile import ZipFile


a = runpy.run_path(str(Path(__file__).with_name("5572_f02_protocol_path_independent.py")))
H, OPS, PLAN, P = (a[k] for k in ("H", "OPS", "PLAN", "P"))
JAVA, ARCH, SLF, git, pin, dump, execute, read = (
    a[k] for k in ("JAVA", "ARCH", "SLF", "git", "pin", "dump", "execute", "read")
)


def main():
    start_file, = PLAN.glob("1646_*.json")
    start = read(start_file)["values"]
    for row in start["oracleReferences"]:
        assert pin(Path(row["path"])) == row
    _, precedent, build, new_canaries, selected_tool = [Path(row["path"]) for row in start["oracleReferences"]]
    previous = read(precedent)
    package = read(build)
    expected = read(new_canaries)
    assert previous["actualExit"] == expected["actualExit"] == 0
    assert previous["productMavenJarsAnalyzed"] == ["protocol"] and previous["allowedClassInventoryMatched"]
    assert previous["currentMavenBuild"] == pin(build)
    assert expected["newCanaries"] == 12 and expected["findingsActual"] == 19
    assert not git("diff", "--name-only", package["source"], start["productionCoreMain"],
                   "--", "pom.xml", "src/pom.xml", "src/schubert-nk-protocol")
    binary = Path(previous["archive"]["path"])
    archive = pin(binary)
    assert archive == previous["archive"] == {
        k: package["packaged"]["protocol"][k] for k in ("path", "sha256")
    }
    jdeps = Path(previous["typedInventory"]["path"])
    assert pin(jdeps) == previous["typedInventory"]
    with gzip.open(jdeps, "rt") as stream:
        permitted = {raw.split()[0] for raw in stream if raw.lstrip().startswith(P+"protocol.")}
    assert len(permitted) == 176
    with ZipFile(binary) as opened:
        names = [path.removesuffix(".class").replace("/", ".")
                 for path in opened.namelist() if path.endswith(".class")]
    assert len(names) == len(set(names)) == 176 and set(names) == permitted
    assert all(pin(path)["sha256"] == value for path, value in H["PINS"].items())
    assert selected_tool == H["TOOL"]
    frozen = selected_tool.read_bytes()
    assert git("show", f'{start["source"]}:{selected_tool}') == frozen
    assert git("show", f'{previous["toolSource"]}:{selected_tool}') != frozen
    out = OPS/"PG41224-f02-current-protocol-archive-rule-v1"
    out.mkdir()
    stages = {}
    modules = sorted(set(H["MODULES"]) - {"protocol"})
    cp = os.pathsep.join(map(str, (ARCH, SLF)))
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-protocol-archive-") as temp:
        space = Path(temp)
        code = space/selected_tool.name
        code.write_bytes(frozen)
        anchors = []
        for owner in modules:
            src = space/owner/"UnrelatedAnchor.java"
            src.parent.mkdir()
            src.write_text(f"package {P}{owner}; public final class UnrelatedAnchor {{}}\n")
            anchors.append(src)
        strict = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        stages["compile"], _ = execute(out, "compile", [*strict, "-cp", cp, "-d", space/"audit", code], space)
        stages["anchors"], _ = execute(out, "anchors", [*strict, "-d", space/"bin", *anchors], space)
        assert all(receipt["actualExit"] == 0 for receipt in stages.values())
        args = [f"protocol={binary}"]
        for owner in modules:
            jar = space/(owner+".jar")
            H["archive"](jar, [P+owner+".UnrelatedAnchor"], space/"bin")
            args.append(f"{owner}={jar}")
        stages["audit"], output = execute(out, "audit", [
            JAVA, "-cp", f"{space/'audit'}{os.pathsep}{cp}", "ModuleDependencyAudit", *args], space)
    table = [line.split("\t") for line in output.splitlines()]
    assert stages["audit"]["actualExit"] == 0 and ["ARCHUNIT", "1.4.2", "181", "181"] in table
    assert {row[1]: int(row[2]) for row in table if row[0] == "MODULE"} == {"protocol":176, **dict.fromkeys(modules, 1)}
    rules = {row[1]: int(row[2]) for row in table if row[0] == "RULE"}
    assert rules == dict.fromkeys(H["RULES"], 0)
    assert not a["recorded_findings"](out/"audit.stdout.txt")
    read_edges = next(row[1:] for row in table if row[0] == "INSPECTED")
    assert all(int(count) > 0 for count in read_edges)
    assert pin(binary) == archive
    data = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                source=start["source"], core=start["productionCoreMain"], tool=pin(selected_tool),
                originalStatic=pin(precedent), exactArchive=archive, exactPackage=pin(build), allowedNames=pin(jdeps),
                protocolPhysical=176, anchorPhysical=5, productModuleCoverage="1/6",
                ruleViolations=rules, inspectedDependencies=int(read_edges[0]), inspectedCodeCalls=int(read_edges[1]),
                productTests=0, productMethodsExecuted=0, productClassInitializations=0,
                allOtherProductArchivesOpened=0, stages=stages, wholeF02=False, whole451=False, formalDelta=0)
    result = out/"manifest.json"
    dump(result, data)
    print(pin(result), read_edges, rules)


if __name__ == "__main__":
    main()
