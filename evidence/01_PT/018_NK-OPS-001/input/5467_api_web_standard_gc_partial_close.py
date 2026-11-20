"""Reconcile the API and Web owned SDK retry contracts in separately pinned runs."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import sys
import tempfile


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


phase, core, role = sys.argv[1:]
assert role in ("api", "web")
prefix = role.title()
assert phase in ("before", "after")
ops = Path("evidence/01_PT/018_NK-OPS-001")
plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
group = read(next(plan.glob("1287_*")))
context = group["values"]
assert all(pin(Path(item["path"])) == item for item in context["oracleReferences"])
base = context["productionCoreMain"]
java_root = Path(f"src/schubert-nk-{role}/src")
namespace = f"dev.codex.schubert.nk.{role}.monitoring"
relative = Path(namespace.replace(".", "/"))
main = java_root / "main/java" / relative / f"{prefix}StandardMetricSource.java"
fixture = java_root / "test/java" / relative / f"{prefix}StandardMetricSourceTest.java"
spec = Path("evidence/01_PT/018_NK-OPS-001/5468_APIWeb標準SDK段階解放の単体仕様.md")
stems = [prefix + stem for stem in ("StandardMetricSource", "StandardMetrics", "JvmMetrics",
                                    "SystemMetrics", "GcMetricRegistration")]
if role == "web":
    stems.append("HttpMetricContract")
if main.with_name("package-info.java").is_file():
    stems.append("package-info")
inputs = [main.with_name(stem + ".java") for stem in stems]
assert all(path.read_bytes() == git("show", f"{core}:{path}") for path in inputs)
changed = git("diff", "--name-only", base, core, "--", "src",
              ":(exclude)src/**/src/test/**").decode().splitlines()
if phase == "before":
    assert core == base and not changed
else:
    expected = {
        f"src/schubert-nk-{key}/src/main/java/dev/codex/schubert/nk/{key}/monitoring/{key.title()}StandardMetricSource.java"
        for key in ("api", "web")
    }
    assert set(changed) == expected and core == git("rev-parse", "HEAD").decode().strip()
    assert fixture.read_bytes() == git("show", f"{core}:{fixture}")

sdk = read(next((ops / "evidence/provisional").glob("PG8170-*/manifest.json")))
rows = [item["jar"] for item in sdk["downloaded"].values()] + list(sdk["reused"].values())
excluded = {"prometheus-metrics-tracer-initializer-1.7.0.jar",
            "prometheus-metrics-tracer-otel-agent-1.7.0.jar", "prometheus-metrics-tracer-otel-1.7.0.jar"}
jars = [Path(item["path"]) for item in rows if Path(item["path"]).name not in excluded]
assert len(jars) == 12 and all(pin(p)["sha256"] == next(
    item["sha256"] for item in rows if item["path"] == str(p)) for p in jars)
tools = Path.cwd().parent / "toolchain"
java = tools / "jdk-25.0.4/bin/java"
junit = tools / "junit-platform-console-standalone-1.13.4.jar"
fmt = tools / "google-java-format-1.36.1-all-deps.jar"
style = tools / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rulefile = Path("tools/quality/static/checkstyle.xml")
agent = tools / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
cli = tools / "org.jacoco.cli-0.8.15-nodeps.jar"
out = ops / "evidence" / (context["run"] + f"-before-{role}" if phase == "before" else
                           f"PG40878-api-web-standard-gc-partial-close-v1-after-{role}")
session = f"PG40878-{role.upper()}-HOST"
out.mkdir()
started = datetime.now(timezone.utc).isoformat()
steps = {}
cases = []
xml_hash = None
coverage = None


def run(name, *args):
    command = list(map(str, args))
    result = subprocess.run(command, capture_output=True, timeout=70)
    steps[name] = dict(command=command, exit=result.returncode, stdoutSha256=digest(result.stdout),
                       stderrSha256=digest(result.stderr))
    if result.returncode and name != "unit":
        print(name, result.stderr.decode(errors="replace")[:1300])
    return result.returncode


with tempfile.TemporaryDirectory(prefix="pg40876-", dir="/dev/shm") as loc:
    root = Path(loc)
    classes, reports = root / "classes", root / "reports"
    reports.mkdir()
    cp = ":".join(map(str, jars))
    checked = [fixture] if phase == "before" else [main, fixture]
    code = run("format", java, "-jar", fmt, "--skip-reflowing-long-strings", "--dry-run",
               "--set-exit-if-changed", *checked)
    if code == 0:
        code = run("checkstyle", java, "-jar", style, "-c", rulefile, *checked)
    if code == 0:
        code = run("javac", java.with_name("javac"), "--release", 25, "-g", "-proc:none", "-Xlint:all",
                   "-Werror", "-cp", f"{cp}:{junit}", "-d", classes, *inputs, fixture)
    test_class = namespace + f".{prefix}StandardMetricSourceTest"
    test_prefix = role + "host"
    test_method = test_prefix + "017RegistryFailureRetriesOnlyItsUnreleasedHandle"
    target = classes / relative / f"{prefix}StandardMetricSource.class"
    if code == 0:
        selector = ("--select-method", test_class + "#" + test_method) if phase == "before" else ("--select-class", test_class)
        instrumentation = () if phase == "before" else (
            f"-javaagent:{agent}=destfile={root / 'exec'},sessionid={session},append=false,"
            f"includes={namespace}.{prefix}StandardMetricSource",)
        code = run("unit", java, *instrumentation, "-jar", junit, "execute", "--disable-banner",
                   "--disable-ansi-colors", "--class-path", f"{classes}:{cp}", "--reports-dir", reports,
                   "--fail-if-no-tests", *selector)
        xml = reports / "TEST-junit-jupiter.xml"
        if xml.exists():
            xml_hash = pin(xml)["sha256"]
            for item in ET.parse(xml).getroot().findall("testcase"):
                method = item.attrib["name"].removesuffix("()")
                suffix = method.removeprefix(test_prefix)[:3]
                assert method.startswith(test_prefix) and suffix.isdigit()
                outcome = next((tag for tag in ("failure", "error", "skipped") if item.find(tag) is not None),
                               "passed")
                duplicate = (outcome == "failure" and
                             "[gc, registry, gc, registry]" in item.find("failure").get("message", ""))
                cases.append(dict(testId=role.upper() + "HOST" + suffix, method=method, outcome=outcome,
                                  actualDuplicateGcClose=duplicate))
    qualification = (code == 1 and len(cases) == 1 and cases[0]["actualDuplicateGcClose"]) if phase == "before" else (
        code == 0 and sorted(row["testId"] for row in cases) == [f"{role.upper()}HOST{i:03d}" for i in range(1, 18)]
        and all(row["outcome"] == "passed" for row in cases))
    if phase == "after" and qualification:
        cov_file = out / "coverage.xml"
        coverage_code = run("coverage", java, "-jar", cli, "report", root / "exec", "--classfiles",
                            target, "--xml", cov_file)
        if coverage_code == 0:
            cov = ET.parse(cov_file).getroot()
            assert [item.attrib["id"] for item in cov.findall("sessioninfo")] == [session]
            state = {item.attrib["type"]: {k: int(item.attrib[k]) for k in ("missed", "covered")}
                     for item in cov.findall("counter")}
            coverage = dict(xml=pin(cov_file), execSha256=pin(root / "exec")["sha256"], counters=state)
    target_digest = pin(target)["sha256"] if target.is_file() else None
record = dict(actualExit=code, expectedOutcomeMet=qualification, phase=phase, role=role, source=core,
              baseSource=base, startEvent=group["eventId"], startedAtUTC=started,
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), productionInputs=[pin(path) for path in inputs],
              runtimeDependencies=[pin(path) for path in jars], targetClassSha256=target_digest,
              testInput=pin(fixture), specification=pin(spec), steps=steps, selectedCases=cases,
              junitXmlSha256=xml_hash, coverage=coverage, externalServiceRuns=0, full451=False, formalDelta=0)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(phase, code, qualification, len(cases), pin(manifest))
raise SystemExit(0 if qualification else 1)
