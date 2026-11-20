"""Verify the approved screen-facade boundary with ordinary synthetic class files."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

SUPPORT = runpy.run_path(str(Path(__file__).with_name("5384_f02_repository_type_dependencies.py")))
V, R, H, C = (SUPPORT[k] for k in ("V", "R", "H", "C"))
WEB = H["P"] + "web."
REPLY = WEB + "messaging.JmsRequestReplyClient"
FACADE = WEB + "application.ReplyFacade"
RULE = "CONTROLLER_BOUNDARY"
CASES = (
    ("001", WEB + "ui.DirectController", REPLY, f"public int send() {{ return {REPLY}.send(); }}", True),
    ("002", WEB + "ui.FieldController", REPLY, f"public {REPLY} client;", True),
    ("003", WEB + "ui.NestedController$Inner", REPLY + "$Port", f"public {REPLY}.Port client;", True),
    ("004", WEB + "ui.SignatureController", REPLY, f"public void send({REPLY}[] clients) {{}}", True),
    ("005", WEB + "ui.OrderController", FACADE, f"public int send() {{ return {FACADE}.send(); }}", False),
    ("006", FACADE, REPLY, f"public static int send() {{ return {REPLY}.send(); }}", False),
    ("007", WEB + "ui.IndependentController", REPLY + "Support", f"public {REPLY}Support marker;", False),
)


def fixtures(root):
    write = C["write_fixture"]
    inputs = [
        write(root, REPLY, "public static int send() { return 1; } public static final class Port {}"),
        write(root, REPLY + "Support", ""),
    ]
    for _, origin, _, body, _ in CASES:
        if origin.endswith("$Inner"):
            outer = origin.removesuffix("$Inner")
            inputs.append(write(root, outer, "public static final class Inner { " + body + " }"))
        else:
            inputs.append(write(root, origin, body))
    return inputs


def main(after):
    pin, git, execute = (H[k] for k in ("pin", "git", "execute"))
    start = R["read"](next(H["PLAN"].glob("1006_*")))["values"]
    source = git("rev-parse", "HEAD").decode().strip() if after else start["source"]
    tool = H["TOOL"]
    data = git("show", f"{source}:{tool}")
    assert (data != git("show", f"{start['source']}:{tool}")) == after
    assert all(pin(p)["sha256"] == v for p, v in H["PINS"].items())
    assert all(pin(Path(ref["path"])) == ref for ref in start["oracleReferences"])
    past = Path(start["oracleReferences"][2]["path"])
    old = R["read"](past)
    old_findings = SUPPORT["published_findings"](past.with_name("audit.stdout.txt"))
    assert len(old_findings) == 42 and old["matched"] == 10 and old["controlsVerified"] == 55

    out = H["OPS"] / ("PG40626-f02-controller-reply-edge-after-v1" if after else start["run"])
    out.mkdir()
    java = H["JAVA"]
    cp = os.pathsep.join(str(H[n]) for n in ("ARCH", "SLF"))
    compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    receipts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-web-boundary-") as name:
        root = Path(name)
        ts = root / tool.name
        ts.write_bytes(data)
        base = root / "fixture"
        inputs = fixtures(base)
        if after:
            inputs += C["inputs"](base) + R["additional_sources"](base) + V["fixture_sources"](base)
            inputs += SUPPORT["fixture"](base)
        else:
            inputs += [C["write_fixture"](base, H["P"] + m + ".Anchor", C["MARKER"]) for m in H["MODULES"]]
        for tag, command in (
            ("compile-tool", [*compiler, "-cp", cp, "-d", root / "tool", ts]),
            ("compile-fixture", [*compiler, "-d", root / "compiled", *inputs]),
        ):
            receipts[tag], _ = execute(out, tag, command, root)
            assert receipts[tag]["actualExit"] == 0
        bins = root / "compiled"
        owners = {m: [] for m in H["MODULES"]}
        physical = {}
        for path in sorted(bins.rglob("*.class")):
            cn = path.relative_to(bins).as_posix().removesuffix(".class").replace("/", ".")
            if cn in V["STUBS"]:
                continue
            module = ("api" if cn == R["ANNOTATION"] else
                      cn.removeprefix(H["P"]).split(".", 1)[0] if cn.startswith(H["P"]) else "web")
            owners[module].append(cn)
            physical[cn] = pin(path)["sha256"]
        if after:
            assert all(physical[n] == value for n, value in old["inputPhysical"].items())
        argv = []
        for module, names in sorted(owners.items()):
            jar = root / (module + ".jar")
            H["archive"](jar, names, bins)
            argv.append(f"{module}={jar}")
        receipts["audit"], raw = execute(out, "audit", [
            java, "-cp", str(root / "tool") + os.pathsep + cp, "ModuleDependencyAudit", *argv,
        ], root)
    findings = SUPPORT["published_findings"](out / "audit.stdout.txt")
    newly_expected = {(RULE, origin, target) for _, origin, target, _, blocked in CASES if blocked}
    assert findings == (old_findings | newly_expected if after else set())
    assert receipts["audit"]["actualExit"] == int(after)
    assert [line.split("\t")[2:] for line in raw.splitlines() if line.startswith("ARCHUNIT\t")] == [
        [str(len(physical))] * 2
    ]
    rows = [dict(testId="PT-F02-WEB-REPLY-"+num, origin=origin, target=target, expected=blocked,
                 observed=(RULE, origin, target) in findings)
            for num, origin, target, _, blocked in CASES]
    matched = sum(row["expected"] == row["observed"] for row in rows)
    m = out / "manifest.json"
    H["dump"](m, dict(actualExit=0 if after else 1, source=source, productionCore=start["productionCoreMain"],
                      oldControls=pin(past), toolSha256=H["sha"](data), cases=rows, matched=matched,
                      originalControlsVerified=65 if after else 0, inputPhysical=physical, receipts=receipts,
                      findings=len(findings), underlyingAuditExit=receipts["audit"]["actualExit"],
                      productTests=0, productJars=0, wholeF02Accepted=False, whole451Accepted=False,
                      terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(m), matched, len(physical))
    return 0 if after else 1


if __name__ == "__main__":
    raise SystemExit(main({"before": False, "after": True}[sys.argv[1]]))
