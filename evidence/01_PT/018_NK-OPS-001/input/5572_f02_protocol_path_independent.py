"""Verify literal finding sets and audit only the pinned, permitted Protocol Maven JAR."""

from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
import zipfile


H = runpy.run_path(str(Path(__file__).with_name("5267_f02_controller_archunit_canaries.py")))
OPS, PLAN, P = (H[key] for key in ("OPS", "PLAN", "P"))
JAVA, ARCH, SLF = (H[key] for key in ("JAVA", "ARCH", "SLF"))
git, pin, dump, execute = (H[key] for key in ("git", "pin", "dump", "execute"))


def find(prefix, file="manifest.json"):
    path, = OPS.glob(f"{prefix}-*/{file}")
    return path


def read(path):
    return json.loads(path.read_bytes())


def recorded_findings(path):
    rows = []
    for line in path.read_text().splitlines():
        if line.startswith("FINDING\t"):
            tag, rule, owner, target = line.split("\t")
            rows.append((rule, owner, target))
    assert len(rows) == len(set(rows))
    return set(rows)


def main():
    start_file, = PLAN.glob("1516_*")
    start = read(start_file)["values"]
    before, after = find("PG41062", "receipt.json"), find("PG41064")
    old = find("PG40632")
    for receipt in (before, after, old):
        data = read(receipt)
        key = "steps" if "steps" in data else "receipts"
        assert pin(receipt.with_name("audit.stdout.txt")) == data[key]["audit"]["stdout"]
    expected = {
        ("FRAMEWORK_FENCES", P + "protocol." + name, "java.nio.file.Path")
        for name in ("RealPathRead", "WatchEvents", "WatchModifiers", "RealPathReference")
    }
    assert recorded_findings(before.with_name("audit.stdout.txt")) == set()
    prior = recorded_findings(old.with_name("audit.stdout.txt"))
    actual = recorded_findings(after.with_name("audit.stdout.txt"))
    assert len(prior) == 53 and actual == prior | expected
    assert [row["observed"] for row in read(after)["fixtures"]] == [True] * 4 + [False] * 4

    build = find("PG40802")
    original = read(build)
    core = start["productionCoreMain"]
    module = "src/schubert-nk-protocol"
    assert git("diff", "--name-only", original["source"], core, "--", module, "src/pom.xml") == b""
    recent = read(find("PG40634"))
    jdeps = Path(recent["retainedProtocolJdeps"]["path"])
    assert pin(jdeps) == recent["retainedProtocolJdeps"]
    with gzip.open(jdeps, "rt") as stream:
        edges = [line.split() for line in stream if line.lstrip().startswith(P + "protocol.")]
    allowed = {row[0] for row in edges}
    assert len(edges) == 2609 and len(allowed) == 176
    assert all(row[1] == "->" and row[2] != "java.nio.file.Path" for row in edges)
    jar = Path(original["packaged"]["protocol"]["path"])
    jar_pin = pin(jar)
    assert jar_pin["sha256"] == original["packaged"]["protocol"]["sha256"]
    with zipfile.ZipFile(jar) as archive:
        class_paths = [name for name in archive.namelist() if name.endswith(".class")]
    assert len(class_paths) == len(set(class_paths)) == 176
    assert {name.removesuffix(".class").replace("/", ".") for name in class_paths} == allowed
    assert all(pin(path)["sha256"] == digest for path, digest in H["PINS"].items())
    src = read(after)["toolSource"]
    changed = git("show", f"{src}:{H['TOOL']}")
    assert H["sha"](changed) == read(after)["toolSourceSha256"]
    assert git("show", f"HEAD:{H['TOOL']}") == changed

    out = OPS / "PG41066-f02-protocol-path-io-independent-v1"
    out.mkdir()
    cp = os.pathsep.join(map(str, (ARCH, SLF)))
    steps = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-protocol-path-post-") as temporary:
        base = Path(temporary)
        change = base / "ModuleDependencyAudit.java"
        change.write_bytes(changed)
        modules = sorted(set(H["MODULES"]) - {"protocol"})
        files = []
        for module_name in modules:
            path = base / (module_name + "/UnrelatedAnchor.java")
            path.parent.mkdir()
            path.write_text(f"package {P}{module_name}; public final class UnrelatedAnchor {{}}\n")
            files.append(path)
        compiler = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
        steps["compile"], _ = execute(out, "compile", [
            *compiler, "-cp", cp, "-d", base / "audit", change,
        ], base)
        steps["fixtures"], _ = execute(out, "fixtures", [
            *compiler, "-d", base / "binary", *files,
        ], base)
        assert all(step["actualExit"] == 0 for step in steps.values())
        pairs = [f"protocol={jar}"]
        for module_name in modules:
            anchor_jar = base / (module_name + ".jar")
            H["archive"](anchor_jar, [P + module_name + ".UnrelatedAnchor"], base / "binary")
            pairs.append(f"{module_name}={anchor_jar}")
        steps["audit"], output = execute(out, "audit", [
            JAVA, "-cp", str(base / "audit") + os.pathsep + cp, "ModuleDependencyAudit", *pairs,
        ], base)
    table = [line.split("\t") for line in output.splitlines()]
    assert steps["audit"]["actualExit"] == 0
    assert ["ARCHUNIT", "1.4.2", "181", "181"] in table
    assert {row[1]: int(row[2]) for row in table if row[0] == "MODULE"} == {
        "protocol": 176, **dict.fromkeys(modules, 1),
    }
    assert {row[1]: int(row[2]) for row in table if row[0] == "RULE"} == dict.fromkeys(H["RULES"], 0)
    assert recorded_findings(out / "audit.stdout.txt") == set()
    destination = out / "manifest.json"
    dump(destination, dict(actualExit=0, productionCore=core, toolSource=src,
                           terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                           syntheticBefore=pin(before), syntheticAfter=pin(after), previousControls=pin(old),
                           currentMavenBuild=pin(build), archive=jar_pin, typedInventory=pin(jdeps),
                           productMavenJarsRead=1, productMavenJarsAnalyzed=["protocol"],
                           protocolPhysical=176, allowedClassInventoryMatched=True, anchorClasses=5,
                           beforeUnreported=4, afterFixed=4, allowedControls=4, unchangedOriginalControls=82,
                           realProtocolFindings=0, newProductTestRuns=0, originalProductTestsRerun=0,
                           fixtureMethodsInvoked=0, reservedClassfilesRead=0, wholeF02Accepted=False,
                           whole451Accepted=False, sourcesPins=H["PINS"] and [
                               pin(Path(path)) for path in H["PINS"]
                           ], steps=steps, verifier=pin(Path(__file__))))
    print(pin(destination))


if __name__ == "__main__":
    main()
