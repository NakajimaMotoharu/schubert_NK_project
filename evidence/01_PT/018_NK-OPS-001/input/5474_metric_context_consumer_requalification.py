"""Requalify both existing metric context cohorts after the direct SDK change."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile


def sha(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


pmo = Path("documents/400_PGPT/470_PMO")
start = read(next(pmo.glob("601_*/1306_*")))
ctx = start["values"]
core = ctx["productionCoreMain"]
assert all(pin(Path(row["path"])) == row for row in ctx["oracleReferences"])
proofs = [read(Path(row["path"])) for row in ctx["oracleReferences"][1:3]]
assert len(proofs) == 2 and all(x["actualExit"] == 0 for x in proofs)
deps = proofs[0]["dependencies"]
assert deps == proofs[1]["dependencies"] and len(deps) == 13
assert all(pin(Path(path))["sha256"] == stamp for path, stamp in deps.items())
junit, = (Path(path) for path in deps if Path(path).name == "junit-platform-console-standalone-1.13.4.jar")
inputs = {}
changed = []
for proof in proofs:
    for file, old in proof["inputHashes"].items():
        path = Path(file)
        if path.suffix != ".java":
            continue
        current = pin(path)["sha256"]
        exact = subprocess.check_output(["git", "show", f"{core}:{path}"], timeout=20)
        assert current == sha(exact)
        if current != old:
            changed.append(path.name)
        inputs[file] = current
assert len(inputs) == 45 and sorted(changed) == ["ApiStandardMetricSource.java", "WebStandardMetricSource.java"]
expected = {(case["classname"], case["name"]) for proof in proofs for case in proof["expectedCases"]}
selected = [name for proof in proofs for name in proof["selectedClasses"]]
assert len(expected) == 66 and len(selected) == 2

tc = Path.cwd().parent / "toolchain"
java = tc / "jdk-25.0.4/bin/java"
agent = tc / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
cli = tc / "org.jacoco.cli-0.8.15-nodeps.jar"
evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
out = evidence / ctx["run"]
out.mkdir()
started = datetime.now(timezone.utc).isoformat()
steps = {}


def run(label, *args):
    command = list(map(str, args))
    response = subprocess.run(command, capture_output=True, timeout=120)
    steps[label] = dict(command=command, exit=response.returncode, stdoutSha256=sha(response.stdout),
                        stderrSha256=sha(response.stderr))
    if response.returncode and label != "unit":
        print(label, response.stderr.decode(errors="replace")[:1200])
    return response.returncode


xml_hash = None
observed = []
cov = None
with tempfile.TemporaryDirectory(prefix="pg40892-", dir="/dev/shm") as loc:
    folder = Path(loc)
    classes, reports = folder / "classes", folder / "reports"
    reports.mkdir()
    cp = ":".join(deps)
    status = run("compile", java.with_name("javac"), "--release", 25, "-g", "-Xlint:all", "-Werror",
                 "-proc:none", "-cp", cp, "-d", classes, *sorted(inputs))
    namespaces = [name.removesuffix("Test") for name in selected]
    if status == 0:
        session = "PG40892-CURRENT-METRIC-CONTEXT"
        exec_file = folder / "jacoco.exec"
        agentarg = f"-javaagent:{agent}=destfile={exec_file},sessionid={session},append=false,includes={':'.join(namespaces)}"
        selector = [arg for name in selected for arg in ("--select-class", name)]
        status = run("unit", java, agentarg, "-jar", junit, "execute", "--disable-banner",
                     "--disable-ansi-colors", "--class-path", f"{classes}:{cp}",
                     "--reports-dir", reports, "--fail-if-no-tests", *selector)
        report = reports / "TEST-junit-jupiter.xml"
        if report.is_file():
            xml_hash = pin(report)["sha256"]
            for case in ET.parse(report).getroot().findall("testcase"):
                outcome = next((tag for tag in ("failure", "error", "skipped") if case.find(tag) is not None), "passed")
                observed.append(dict(classname=case.attrib["classname"], method=case.attrib["name"], outcome=outcome))
        if status == 0:
            assert len(observed) == 66 and {(c["classname"], c["method"]) for c in observed} == expected
            assert all(c["outcome"] == "passed" for c in observed)
            cov_path = out / "coverage.xml"
            targets = [classes / (name.replace(".", "/") + ".class") for name in namespaces]
            arguments = [arg for target in targets for arg in ("--classfiles", target)]
            status = run("coverage", java, "-jar", cli, "report", exec_file, *arguments, "--xml", cov_path)
            if status == 0:
                report = ET.parse(cov_path).getroot()
                assert [node.attrib["id"] for node in report.findall("sessioninfo")] == [session]
                counters = {
                    cls.attrib["name"]: {node.attrib["type"]: [int(node.attrib[k]) for k in ("covered", "missed")]
                                         for node in cls.findall("counter")}
                    for cls in report.findall(".//class")
                }
                assert set(counters) == {name.replace(".", "/") for name in namespaces}
                cov = dict(xml=pin(cov_path), execSha256=pin(exec_file)["sha256"], targetCounters=counters)
manifest = out / "manifest.json"
record = dict(actualExit=status, source=core, startEvent=start["eventId"],
              startedAtUTC=started, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              selected=selected, inputHashes=inputs, changedProductInputs=changed, oldInputReceipts=ctx["oracleReferences"][1:3],
              runtimeJarHashes=[pin(Path(path)) for path in deps], testXmlSha256=xml_hash,
              expectedCaseCount=66, observedCases=observed, steps=steps, coverage=cov,
              newProductTests=0, actualExternalOperations=0, full451=False, formalDelta=0)
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(status, len(observed), pin(manifest))
raise SystemExit(status)
