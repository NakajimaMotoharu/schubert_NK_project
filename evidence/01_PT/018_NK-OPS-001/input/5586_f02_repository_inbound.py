"""Run exact dependency-direction fixtures through the static auditor."""

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

WEB = runpy.run_path(str(Path(__file__).with_name("5582_f02_web_controller_transport.py")))
BASE, H, C, R, SUPPORT = (WEB[key] for key in ("BASE", "H", "C", "R", "SUPPORT"))
API = H["P"] + "api."
INBOUND = API + "messaging.inbound.InboundPort"
DAO = API + "persistence.InboundFieldFixture"
MONITOR = API + "monitoring.persistence.InboundCallFixture"
REPOSITORY = API + "fence.DirectionFixtureRepository"
ARRAY = API + "persistence.InboundArrayFixture"
DOMAIN = API + "domain.DirectionFixtureValue"
OUTGOING = API + "messaging.outbound.DirectionFixturePublisher"
APPLICATION = API + "application.DirectionFixtureService"
RULE = "REPOSITORY_DIRECTION"
CASES = (
    (DAO, INBOUND, True),
    (MONITOR, INBOUND, True),
    (REPOSITORY + "$Nested", INBOUND, True),
    (ARRAY, INBOUND, True),
    (APPLICATION, DAO, False),
    (DAO, DOMAIN, False),
    (DAO, OUTGOING, False),
)


def fixture_inputs(root):
    write = C["write_fixture"]
    return [
        write(root, INBOUND, "public void receive() {}"),
        write(root, DAO, f"public {INBOUND} inbound; public {DOMAIN} value; public {OUTGOING} events;"),
        write(root, MONITOR, f"public void drain({INBOUND} inbound) {{ inbound.receive(); }}"),
        write(root, REPOSITORY, f"public static class Nested {{ public {INBOUND} inbound; }}"),
        write(root, ARRAY, f"public {INBOUND}[][] inbound;"),
        write(root, DOMAIN, ""),
        write(root, OUTGOING, ""),
        write(root, APPLICATION, f"public {DAO} repository;"),
    ]


def main(after):
    pin, git, execute = (H[key] for key in ("pin", "git", "execute"))
    start_file, = H["PLAN"].glob("1552_*")
    start = R["read"](start_file)["values"]
    assert all(pin(Path(row["path"])) == row for row in start["oracleReferences"])
    assert all(pin(path)["sha256"] == wanted for path, wanted in H["PINS"].items())
    tool_source = git("rev-parse", "HEAD").decode().strip() if after else start["source"]
    tool = H["TOOL"]
    data = git("show", f"{tool_source}:{tool}")
    assert (data != git("show", f"{start['source']}:{tool}")) == after
    assert not git("diff", "--name-only", start["source"], tool_source, "--", "src")
    prior_path = Path(start["oracleReferences"][1]["path"])
    prior = R["read"](prior_path)
    prior_findings = SUPPORT["published_findings"](prior_path.with_name("audit.stdout.txt"))
    assert len(prior_findings) == 67 and prior["oldControls"] + prior["matched"] == 103
    out = H["OPS"] / ("PG41112-f02-repository-inbound-after-v1" if after else start["run"])
    out.mkdir()
    java = H["JAVA"]
    classpath = os.pathsep.join(str(H[key]) for key in ("ARCH", "SLF"))
    javac = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    steps = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f02-repository-") as dirname:
        root = Path(dirname)
        fixture = root / "source"
        code = root / tool.name
        code.write_bytes(data)
        sources = fixture_inputs(fixture) + WEB["source_inputs"](fixture)[0]
        sources += [C["write_fixture"](fixture, H["P"]+name, body)
                    for name, body, _ in BASE["CASES"] if name != "protocol.PathValue"]
        sources += BASE["prior_sources"](fixture)
        sources.append(C["write_fixture"](fixture, H["P"]+"protocol.PathDescriptorField",
                                          "public java.nio.file.Path value;"))
        assert len(sources) == len(set(sources))
        for key, argv in (
            ("compile-tool", [*javac, "-cp", classpath, "-d", root/"tool", code]),
            ("compile-fixture", [*javac, "-d", root/"binary", *sources]),
        ):
            steps[key], _ = execute(out, key, argv, root)
            assert steps[key]["actualExit"] == 0
        owners, physical = BASE["fixture_owners"](root/"binary")
        assert all(physical[row["className"]] == row["sha256"] for row in prior["physical"])
        args = []
        for module, types in sorted(owners.items()):
            jar = root / (module + ".jar")
            H["archive"](jar, types, root/"binary")
            args.append(f"{module}={jar}")
        steps["audit"], raw = execute(out, "audit",
            [java, "-cp", str(root/"tool")+os.pathsep+classpath, "ModuleDependencyAudit", *args], root)
    findings = SUPPORT["published_findings"](out/"audit.stdout.txt")
    expected = {(RULE, origin, target) for origin, target, prohibited in CASES if prohibited}
    assert findings == (prior_findings | expected if after else prior_findings), sorted(findings-prior_findings)
    assert steps["audit"]["actualExit"] == 1
    assert f"ARCHUNIT\t1.4.2\t{len(physical)}\t{len(physical)}" in raw.splitlines()
    checks = [
        dict(testId=f"PT-F02-REPO-INBOUND-{index:03}", origin=origin, target=target,
             expected=prohibited, observed=(RULE, origin, target) in findings)
        for index, (origin, target, prohibited) in enumerate(CASES, 1)
    ]
    manifest = out/"manifest.json"
    H["dump"](manifest, dict(
        actualExit=0 if after else 1, rawAuditExit=1, productionCore=start["productionCoreMain"],
        toolSource=tool_source, toolSha256=H["sha"](data), priorReceipt=pin(prior_path),
        priorControls=103, priorPhysical=len(prior["physical"]), physical=len(physical),
        priorFindings=len(prior_findings), findings=len(findings),
        matched=sum(row["expected"] == row["observed"] for row in checks),
        caseCount=len(checks), cases=checks, productJars=0, productTests=0, fixtureInvocations=0,
        wholeF02Accepted=False, whole451Accepted=False, steps=steps,
        terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(manifest), len(physical))


if __name__ == "__main__":
    main({"before": False, "after": True}[sys.argv[1]])
