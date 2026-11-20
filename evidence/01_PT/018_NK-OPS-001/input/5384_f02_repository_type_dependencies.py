"""Measure direct API dependency direction with handwritten class declarations."""

import os
from datetime import datetime, timezone
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


V = runpy.run_path(str(Path(__file__).with_name("5383_f02_vendor_jdbc_jms_boundaries.py")))
R, H, C = V["R"], V["H"], V["COMBINED"]
API = H["P"] + "api."
UPPER = API + "application.audit.TypedService"
ERROR = API + "application.audit.TypedFailure"
LOWER = API + "domain.AuditRow"
RULE = "REPOSITORY_DIRECTION"
CASES = (
    ("001", API + "persistence.FieldPort", UPPER, f"public {UPPER} value;", True),
    ("002", API + "support.ReturnRepository", UPPER, f"public {UPPER} read() {{ return null; }}", True),
    ("003", API + "support.ArgumentRepository", UPPER, f"public void save({UPPER} value) {{}}", True),
    ("004", API + "support.GenericRepository", UPPER, f"public java.util.List<{UPPER}> values;", True),
    ("005", API + "support.ArrayRepository", UPPER, f"public {UPPER}[][] values;", True),
    ("006", API + "support.ThrowsRepository", ERROR, f"public void save() throws {ERROR} {{}}", True),
    ("007", API + "monitoring.persistence.BuildPort", UPPER, "constructor", True),
    ("008", API + "support.CallRepository", UPPER, f"public int read() {{ return {UPPER}.read(); }}", True),
    ("009", API + "support.NormalFlow", UPPER, f"public {UPPER} value;", False),
    ("010", API + "support.LowerRepository", LOWER, f"public {LOWER} value;", False),
)


def fixture(root):
    write = C["write_fixture"]
    inputs = [write(root, UPPER, "public static int read() { return 2; }"), write(root, LOWER, "")]
    error = root / (ERROR.replace(".", "/") + ".java")
    error.write_text(f"package {ERROR.rpartition('.')[0]};\n"
                     "public final class TypedFailure extends Exception {\n"
                     "  private static final long serialVersionUID = 1L;\n}\n")
    for _, origin, _, body, _ in CASES:
        if body == "constructor":
            body = f"public {origin.rpartition('.')[2]}({UPPER} value) {{}}"
        inputs.append(write(root, origin, body))
    return inputs + [error]


def published_findings(path):
    return {tuple(line.split("\t")[1:]) for line in path.read_text().splitlines()
            if line.startswith("FINDING\t")}


def main(after):
    pin, git, execute = (H[k] for k in ("pin", "git", "execute"))
    begin = R["read"](next(H["PLAN"].glob("968_*")))["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in begin["oracleReferences"])
    selected = git("rev-parse", "HEAD").decode().strip() if after else begin["source"]
    tool = H["TOOL"]
    code = git("show", f"{selected}:{tool}")
    assert (code != git("show", f"{begin['source']}:{tool}")) == after
    assert all(pin(p)["sha256"] == want for p, want in H["PINS"].items())
    old = next(H["OPS"].glob("PG40574-*/manifest.json"))
    saved = R["read"](old)
    old_findings = published_findings(old.with_name("audit.stdout.txt"))
    assert saved["correct"] == 10 and saved["regressionControls"] == 45 and len(old_findings) == 34
    out = H["OPS"] / ("PG40586-f02-repository-declaration-after-v1" if after else begin["run"])
    out.mkdir()
    cp = os.pathsep.join(str(H[name]) for name in ("ARCH", "SLF"))
    java = H["JAVA"]
    compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    receipts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-repository-decl-") as folder:
        root = Path(folder)
        inputs_at = root / "inputs"
        source = root / tool.name
        source.write_bytes(code)
        inputs = fixture(inputs_at)
        if after:
            inputs += C["inputs"](inputs_at) + R["additional_sources"](inputs_at) + V["fixture_sources"](inputs_at)
        else:
            inputs += [C["write_fixture"](inputs_at, H["P"] + m + ".Anchor", C["MARKER"]) for m in H["MODULES"]]
        for name, cmd in (
            ("compile-tool", [*compiler, "-cp", cp, "-d", root / "tool", source]),
            ("compile-fixture", [*compiler, "-d", root / "classes", *inputs]),
        ):
            receipts[name], _ = execute(out, name, cmd, root)
            assert receipts[name]["actualExit"] == 0
        physical = {}
        groups = {m: [] for m in H["MODULES"]}
        compiled = root / "classes"
        for path in sorted(compiled.rglob("*.class")):
            name = path.relative_to(compiled).as_posix().removesuffix(".class").replace("/", ".")
            if name in V["STUBS"]:
                continue
            physical[name] = pin(path)["sha256"]
            module = ("api" if name == R["ANNOTATION"] else
                      name.removeprefix(H["P"]).split(".", 1)[0] if name.startswith(H["P"]) else "web")
            groups[module].append(name)
        if after:
            assert all(physical.get(name) == want for name, want in saved["inputPhysical"].items())
        args = []
        for module, classes in sorted(groups.items()):
            jar = root / (module + ".jar")
            H["archive"](jar, classes, compiled)
            args.append(f"{module}={jar}")
        receipts["audit"], raw = execute(out, "audit", [
            java, "-cp", str(root / "tool") + os.pathsep + cp, "ModuleDependencyAudit", *args,
        ], root)
    findings = published_findings(out / "audit.stdout.txt")
    expected = {(RULE, origin, target) for _, origin, target, _, want in CASES if want}
    observed = expected if after else {(RULE, CASES[7][1], UPPER)}
    assert findings == (observed | old_findings if after else observed)
    assert receipts["audit"]["actualExit"] == 1
    assert [line.split("\t")[2:] for line in raw.splitlines() if line.startswith("ARCHUNIT\t")] == [
        [str(len(physical))] * 2
    ]
    results = [
        dict(testId="PT-F02-REPO-TYPE-" + num, expected=want, actual=(RULE, origin, target) in findings,
             origin=origin, target=target)
        for num, origin, target, _, want in CASES
    ]
    matched = sum(row["actual"] == row["expected"] for row in results)
    assert matched == (10 if after else 3)
    manifest = out / "manifest.json"
    H["dump"](manifest, dict(
        source=selected, productionCore=begin["productionCoreMain"], toolSha256=H["sha"](code),
        testInput=pin(Path(__file__)), previous55=pin(old), controlsVerified=55 if after else 0,
        actualExit=0 if after else 1, auditExpectedExit=1, auditActualExit=receipts["audit"]["actualExit"],
        inputPhysical=physical, measured=results, matched=matched, rawFindingCount=len(findings),
        receipts=receipts, productJars=0, productTests=0, wholeF02Accepted=False,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    ))
    print(pin(manifest), matched, len(physical))
    return 0 if after else 1


if __name__ == "__main__":
    raise SystemExit(main({"before": False, "after": True}[sys.argv[1]]))
