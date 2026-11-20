"""Check the screen facade/transport-owner split without loading any Web product bytecode."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory


BASE = runpy.run_path(str(Path(__file__).with_name("5571_f02_protocol_path_io.py")))
H, C, R, SUPPORT = (BASE[k] for k in ("H", "C", "R", "SUPPORT"))
P = H["P"]
LINK = P+"web.messaging."
UI = P+"web.fence."
RULE = "CONTROLLER_BOUNDARY"
BLOCKED = (
    "JmsRequestSender", "ArtemisRequestSender", "ReplyCorrelationRegistry", "JmsContextFactory",
    "WebBrokerContexts", "ArtemisReplyConsumer", "ArtemisReplyConsumers", "JmsReplyDecoder",
    "ArtemisReplyDlqSender", "PendingReply",
)
ALLOW = (
    (UI+"ScreenFacadeController", LINK+"ScenarioWireClient"),
    (UI+"SupportController", LINK+"JmsRequestSenderSupport"),
    (LINK+"ScenarioWireClient", LINK+"JmsRequestSender"),
)


def source_inputs(root):
    write = C["write_fixture"]
    classes = []
    expected = []
    for index, name in enumerate(BLOCKED, 1):
        target = LINK+name
        origin = UI+f"Owner{index}Controller"
        body = f"public {target} direct;"
        if name == "ReplyCorrelationRegistry":
            classes.append(write(root,target,"public static class Ticket {}"))
            target += "$Ticket"
            body = f"public {LINK+name}.Ticket[] direct;"
        else:
            classes.append(write(root,target,""))
        if name == "ArtemisReplyConsumer":
            classes.append(write(root,origin,"public static class Nested { "+body+" }"))
            origin += "$Nested"
        else:
            classes.append(write(root,origin,body))
        expected.append((RULE, origin, target))
    classes += [
        write(root, LINK+"JmsRequestSenderSupport", ""),
        write(root, LINK+"ScenarioWireClient", f"public {LINK}JmsRequestSender transport;"),
        write(root, UI+"ScreenFacadeController", f"public {LINK}ScenarioWireClient facade;"),
        write(root, UI+"SupportController", f"public {LINK}JmsRequestSenderSupport marker;"),
    ]
    return classes, expected


def main(after):
    pin, git, execute = (H[k] for k in ("pin", "git", "execute"))
    start_file, = H["PLAN"].glob("1540_*")
    start = R["read"](start_file)["values"]
    assert all(pin(Path(row["path"])) == row for row in start["oracleReferences"])
    assert all(pin(path)["sha256"] == want for path, want in H["PINS"].items())
    source = git("rev-parse","HEAD").decode().strip() if after else start["source"]
    tool = H["TOOL"]
    data = git("show", f"{source}:{tool}")
    assert (data != git("show", f"{start['source']}:{tool}")) == after
    assert not git("diff","--name-only",start["source"],source,"--","src")
    last = Path(start["oracleReferences"][1]["path"])
    previous = R["read"](last)
    prior_found = SUPPORT["published_findings"](last.with_name("audit.stdout.txt"))
    assert previous["matched"] + previous["priorControls"] == 90
    assert len(prior_found) == 57
    out = H["OPS"] / ("PG41094-f02-web-transport-layer-after-v1" if after else start["run"])
    out.mkdir()
    java = H["JAVA"]
    cp = os.pathsep.join(str(H[key]) for key in ("ARCH","SLF"))
    strict = [java.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none"]
    steps = {}
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-f02-transport-fences-") as dirname:
        root = Path(dirname)
        fixture = root / "src"
        code = root / tool.name
        code.write_bytes(data)
        inputs, newly_expected = source_inputs(fixture)
        if after:
            inputs += BASE["prior_sources"](fixture)
            inputs += [C["write_fixture"](fixture, P+owner, body) for owner,body,flag in BASE["CASES"]]
        else:
            inputs += [C["write_fixture"](fixture, P+m+".Anchor", C["MARKER"]) for m in H["MODULES"]]
        for key, argv in (
            ("compile-tool", [*strict, "-cp", cp, "-d", root/"tool", code]),
            ("compile-fixture", [*strict, "-d", root/"binary", *inputs]),
        ):
            steps[key], _ = execute(out,key,argv,root)
            assert steps[key]["actualExit"] == 0
        owners, physical = BASE["fixture_owners"](root/"binary")
        if after:
            assert all(physical[row["className"]] == row["sha256"] for row in previous["physical"])
        argv = []
        for name, types in sorted(owners.items()):
            jar = root / (name+".jar")
            H["archive"](jar,types,root/"binary")
            argv.append(f"{name}={jar}")
        steps["audit"], raw = execute(out,"audit",
            [java, "-cp", str(root/"tool")+os.pathsep+cp, "ModuleDependencyAudit", *argv],root)
    findings = SUPPORT["published_findings"](out/"audit.stdout.txt")
    assert findings == (prior_found | set(newly_expected) if after else set())
    assert steps["audit"]["actualExit"] == int(after)
    assert ["ARCHUNIT","1.4.2",str(len(physical)),str(len(physical))] in [
        line.split("\t") for line in raw.splitlines()]
    expected = [(*row,True) for row in newly_expected]+[(RULE,*pair,False) for pair in ALLOW]
    cases = []
    for i,(rule,origin,target,expected_violation) in enumerate(expected,1):
        cases.append(dict(testId=f"PT-F02-WEB-TRANSPORT-{i:03}",origin=origin,target=target,
                          expected=expected_violation,observed=(rule,origin,target) in findings))
    receipt = out/"manifest.json"
    H["dump"](receipt, dict(actualExit=0, toolSource=source, productionCore=start["productionCoreMain"],
                            cases=cases, oldControls=90 if after else 0,
                            matched=sum(c["expected"]==c["observed"] for c in cases),
                            physical=[dict(className=n,sha256=h) for n,h in physical.items()],
                            inputToolSha256=H["sha"](data), previousResult=pin(last),
                            sourcesAnalyzedByProductCompiler=0, productJars=0, fixtureExecuted=0,
                            plansHeldUnchanged=True, formalDelta=0, steps=steps, whole451=False,
                            terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print(pin(receipt),len(cases),len(physical))


if __name__=="__main__":
    main({"before":False,"after":True}[sys.argv[1]])
