"""Check direct Java object-serialization types with harmless, unexecuted class files."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

PREVIOUS = runpy.run_path(str(Path(__file__).with_name("5392_f02_controller_reply_boundary.py")))
V, R, H, C, SUPPORT = (PREVIOUS[k] for k in ("V", "R", "H", "C", "SUPPORT"))
P = H["P"]
RULE = "FRAMEWORK_FENCES"
RESTRICTED = ("Serializable", "Externalizable", "ObjectInputStream", "ObjectOutputStream",
              "ObjectStreamClass", "ObjectInputFilter", "NotSerializableException")
ORDINARY = ("IOException", "DataInputStream")
CASES = [
    (f"PT-F02-OBJECT-SERIAL-{i:03}", P + "protocol.SerialPort" + str(i), "java.io." + name,
     name in RESTRICTED)
    for i, name in enumerate(RESTRICTED + ORDINARY, 1)
] + [("PT-F02-OBJECT-SERIAL-010", P+"api.FileHelper", "java.io.ObjectOutputStream", False)]


def main(after):
    pin, git, execute = (H[k] for k in ("pin", "git", "execute"))
    start = R["read"](next(H["PLAN"].glob("1009_*")))["values"]
    assert all(pin(Path(ref["path"])) == ref for ref in start["oracleReferences"])
    assert all(pin(p)["sha256"] == want for p, want in H["PINS"].items())
    source = git("rev-parse", "HEAD").decode().strip() if after else start["source"]
    tool = H["TOOL"]
    data = git("show", f"{source}:{tool}")
    assert (data != git("show", f"{start['source']}:{tool}")) == after
    last = Path(start["oracleReferences"][2]["path"])
    old = R["read"](last)
    past = SUPPORT["published_findings"](last.with_name("audit.stdout.txt"))
    assert len(past) == 46 and old["matched"] == 7 and old["originalControlsVerified"] == 65
    out = H["OPS"] / ("PG40632-f02-protocol-serialization-after-v1" if after else start["run"])
    out.mkdir()
    java = H["JAVA"]
    cp = os.pathsep.join(str(H[k]) for k in ("ARCH", "SLF"))
    compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    receipts = {}
    write = C["write_fixture"]
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-protocol-serial-") as name:
        root = Path(name)
        src = root / "src"
        code = root / tool.name
        code.write_bytes(data)
        fixtures = [write(src, origin, f"public {target} field;") for _, origin, target, _ in CASES]
        if after:
            fixtures += (C["inputs"](src) + R["additional_sources"](src) + V["fixture_sources"](src)
                         + SUPPORT["fixture"](src) + PREVIOUS["fixtures"](src))
        else:
            fixtures += [write(src, P+m+".Anchor", C["MARKER"]) for m in H["MODULES"]]
        for tag, argv in (
            ("compile-tool", [*compiler, "-cp", cp, "-d", root/"tool", code]),
            ("compile-fixture", [*compiler, "-d", root/"binary", *fixtures]),
        ):
            receipts[tag], _ = execute(out, tag, argv, root)
            assert receipts[tag]["actualExit"] == 0
        binary = root / "binary"
        owners = {m: [] for m in H["MODULES"]}
        physical = {}
        for file in sorted(binary.rglob("*.class")):
            full = file.relative_to(binary).as_posix().removesuffix(".class").replace("/", ".")
            if full in V["STUBS"]:
                continue
            name = "api" if full == R["ANNOTATION"] else full[len(P):].split(".", 1)[0] if full.startswith(P) else "web"
            owners[name].append(full)
            physical[full] = pin(file)["sha256"]
        if after:
            assert all(physical[k] == value for k, value in old["inputPhysical"].items())
        args = []
        for name, types in sorted(owners.items()):
            jar = root / (name+".jar")
            H["archive"](jar, types, binary)
            args.append(f"{name}={jar}")
        receipts["audit"], raw = execute(out, "audit", [
            java, "-cp", str(root/"tool") + os.pathsep + cp, "ModuleDependencyAudit", *args,
        ], root)
    assert receipts["audit"]["actualExit"] == int(after)
    assert [line.split("\t")[2:] for line in raw.splitlines() if line.startswith("ARCHUNIT\t")] == [
        [str(len(physical))] * 2
    ]
    findings = SUPPORT["published_findings"](out / "audit.stdout.txt")
    expected = {(RULE, origin, target) for _, origin, target, want in CASES if want}
    assert findings == (past | expected if after else set())
    checks = [dict(testId=id, origin=origin, target=target, expected=want,
                   observed=(RULE, origin, target) in findings) for id, origin, target, want in CASES]
    done = sum(c["expected"] == c["observed"] for c in checks)
    manifest = out / "manifest.json"
    H["dump"](manifest, dict(actualExit=0 if after else 1, toolSource=source, productionCore=start["productionCoreMain"],
                            fixtures=checks, matched=done, priorBoundaries=pin(last), priorControls=72 if after else 0,
                            findings=len(findings), receipts=receipts, inputPhysical=physical,
                            toolSourceSha=H["sha"](data), actualProductJars=0, productTests=0,
                            realSerializationExecutions=0, wholeF02Accepted=False, whole451Accepted=False,
                            terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(manifest), done, len(physical))
    return 0 if after else 1


if __name__ == "__main__":
    raise SystemExit(main({"before": False, "after": True}[sys.argv[1]]))
