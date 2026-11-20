"""Check that direct PostgreSQL and Artemis edges obey the existing module fences."""

from collections import Counter
from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


R = runpy.run_path(str(Path(__file__).with_name("5382_f02_api_repository_direction.py")))
COMBINED, H = R["COMBINED"], R["H"]
P = H["P"]
PG = "org.postgresql.PGConnection"
ARTEMIS = "org.apache.activemq.artemis.api.core.client.ClientSession"
ARTEMIS_JMS = "org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory"
FRAMEWORK = "FRAMEWORK_FENCES"
CONTROLLER = "CONTROLLER_BOUNDARY"
CASES = (
    ("001", P + "storage.DriverStore", PG, FRAMEWORK, True),
    ("002", P + "protocol.DriverCodec", PG, FRAMEWORK, True),
    ("003", P + "storage.DirectBroker", ARTEMIS, FRAMEWORK, True),
    ("004", P + "protocol.DirectJms", ARTEMIS_JMS, FRAMEWORK, True),
    ("005", P + "web.DriverController", PG, CONTROLLER, True),
    ("006", P + "web.JmsController", ARTEMIS_JMS, CONTROLLER, True),
    ("007", P + "bootstrap.CopyAdapter", PG, FRAMEWORK, False),
    ("008", P + "batch.ManagementAdapter", ARTEMIS, FRAMEWORK, False),
    ("009", P + "api.messaging.JmsAdapter", ARTEMIS_JMS, FRAMEWORK, False),
    ("010", P + "web.session.SessionDriver", PG, CONTROLLER, False),
)
STUBS = {PG, ARTEMIS, ARTEMIS_JMS}


def fixture_sources(root):
    write = COMBINED["write_fixture"]
    paths = [write(root, name, "") for name in STUBS]
    paths += [write(root, name, f"public {t} port;") for _, name, t, _, _ in CASES]
    return paths


def main(after):
    pin, git, run = (H[k] for k in ("pin", "git", "execute"))
    start = R["read"](next(H["PLAN"].glob("956_*")))["values"]
    source = git("rev-parse", "HEAD").decode().strip() if after else start["source"]
    tool = H["TOOL"]
    data = git("show", f"{source}:{tool}")
    assert (data != git("show", f"{start['source']}:{tool}")) == after
    assert all(pin(p)["sha256"] == h for p, h in H["PINS"].items())
    assert all(pin(Path(ref["path"])) == ref for ref in start["oracleReferences"])
    saved = R["read"](start["oracleReferences"][1]["path"])
    assert saved["newCorrect"] == 10 and saved["regressionCorrect"] == 35
    old_manifest = R["read"](saved["after"]["path"])
    old = R["read"](saved["oldControls"]["path"])
    old_expected = {(k["rule"], k["origin"], t) for k in old["cases"] for t in k["expected"]}
    old_expected |= {
        ("REPOSITORY_DIRECTION", k["origin"], k["target"])
        for k in old_manifest["tests"] if k["expected"]
    }
    assert len(old_expected) == 28
    out = H["OPS"] / ("PG40574-f02-vendor-jdbc-jms-after-v1" if after else start["run"])
    java = H["JAVA"]
    cp = os.pathsep.join(str(H[k]) for k in ("ARCH", "SLF"))
    compiler = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    out.mkdir()
    receipts = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-vendor-f02-") as folder:
        root = Path(folder)
        src = root / "fixture"
        tool_src = root / tool.name
        tool_src.write_bytes(data)
        if after:
            fixtures = COMBINED["inputs"](src) + R["additional_sources"](src)
        else:
            fixtures = [COMBINED["write_fixture"](src, P + m + ".Marker", COMBINED["MARKER"])
                        for m in H["MODULES"]]
        fixtures += fixture_sources(src)
        for label, command in (
            ("compile-tool", [*compiler, "-cp", cp, "-d", root / "tool", tool_src]),
            ("compile-fixture", [*compiler, "-d", root / "classes", *fixtures]),
        ):
            receipts[label], _ = run(out, label, command, root)
            assert receipts[label]["actualExit"] == 0
        groups = {m: [] for m in H["MODULES"]}
        physical = {}
        compiled_stubs = set()
        for p in sorted((root / "classes").rglob("*.class")):
            name = p.relative_to(root / "classes").as_posix().removesuffix(".class").replace("/", ".")
            if name in STUBS:
                compiled_stubs.add(name)
                continue
            physical[name] = pin(p)["sha256"]
            if name == R["ANNOTATION"]:
                owner = "api"
            else:
                owner = name.removeprefix(P).split(".", 1)[0] if name.startswith(P) else "web"
            groups[owner].append(name)
        assert compiled_stubs == STUBS
        if after:
            assert all(physical.get(name) == h for name, h in old_manifest["inputPhysical"].items())
        args = []
        for module, names in sorted(groups.items()):
            jar = root / (module + ".jar")
            H["archive"](jar, names, root / "classes")
            args.append(f"{module}={jar}")
        receipts["audit"], stdout = run(out, "audit", [
            java, "-cp", str(root / "tool") + os.pathsep + cp, "ModuleDependencyAudit", *args,
        ], root)
    rows = [line.split("\t") for line in stdout.splitlines()]
    assert [line[2:] for line in rows if line[0] == "ARCHUNIT"] == [[str(len(physical))] * 2]
    findings = {tuple(line[1:]) for line in rows if line[0] == "FINDING"}
    expected_new = {(rule, origin, target) for _, origin, target, rule, expected in CASES if expected}
    assert findings == (old_expected | expected_new if after else set())
    assert receipts["audit"]["actualExit"] == (1 if after else 0)
    results = [dict(id="PT-F02-VENDOR-" + n, origin=origin, target=target, rule=rule,
                    expected=expected, observed=(rule, origin, target) in findings)
               for n, origin, target, rule, expected in CASES]
    correct = sum(case["expected"] == case["observed"] for case in results)
    manifest = out / "manifest.json"
    H["dump"](manifest, dict(
        actualExit=0 if after else 1, source=source, productionCore=start["productionCoreMain"],
        toolSha256=H["sha"](data), actualAuditExit=receipts["audit"]["actualExit"],
        checks=results, correct=correct, regressionControls=45 if after else 0,
        compiledOnlyVendorTypes=sorted(compiled_stubs), inputPhysical=physical, receipts=receipts,
        rawCounts=Counter(row[0] for row in findings), productJars=0, productTests=0,
        wholeF02Accepted=False, whole451Accepted=False, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    ))
    print(pin(manifest), correct, len(physical))
    return 0 if after else 1


if __name__ == "__main__":
    raise SystemExit(main({"before": False, "after": True}[sys.argv[1]]))
