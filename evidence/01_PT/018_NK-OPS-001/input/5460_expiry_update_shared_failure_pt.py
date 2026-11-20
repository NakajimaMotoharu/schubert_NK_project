"""Run the single admitted Expiry audit proxy test against the current source."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import json
import subprocess
import tempfile


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=15)


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
start = read(next(plan.glob("1269_*")))
values = start["values"]
assert git("rev-parse", "HEAD").decode().strip() == values["source"]
core = values["productionCoreMain"]
assert all(pin(Path(item["path"])) == item for item in values["oracleReferences"])
prior = read(next(evidence.glob("PG40730-*/manifest.json")))
package = read(next(evidence.glob("PG40704-*/manifest.json")))
inputs = read(next(evidence.glob("PG40712-*/manifest.json")))["classpaths"]
assert len(inputs) == 16
main = Path(prior["candidateMain"]["path"])
fixture = Path("src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditPortTest.java")
spec = Path("evidence/01_PT/017_NK-BAT-001/4745_Expiry監査更新の同一例外仕様.md")
assert main.read_bytes() == git("show", f"{core}:{main}")
assert digest(main.read_bytes()) == prior["candidateMain"]["sha256"]
assert digest(git("show", f"HEAD:{fixture}")) == prior["sourceInputs"][str(fixture)]

sdk = Path.cwd().parent / "toolchain"
java = sdk / "jdk-25.0.4/bin/java"
jspecify = sdk / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
junit = sdk / "junit-platform-console-standalone-1.13.4.jar"
formatter = sdk / "google-java-format-1.36.1-all-deps.jar"
style = sdk / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path("tools/quality/static/checkstyle.xml")
owner_by_package = {"batch": "batch", "api": "bootstrap", "bootstrap": "bootstrap", "storage": "storage"}
base = Path("dev/codex/schubert/nk")
method = "updateAndCloseWithTheSameFailureKeepThePublicFailureContract"
out = evidence / values["run"]
out.mkdir()
started = datetime.now(timezone.utc).isoformat()
steps = {}


def run(name, *command):
    argv = list(map(str, command))
    result = subprocess.run(argv, capture_output=True, timeout=45)
    steps[name] = dict(command=argv, exit=result.returncode, stdoutSha256=digest(result.stdout),
                       stderrSha256=digest(result.stderr))
    if result.returncode and name != "test":
        print(name, result.stderr.decode(errors="replace")[:900])
    return result.returncode


cases = []
xml_hash = None
dep_sources = {}
with tempfile.TemporaryDirectory(prefix="pg40858-", dir="/dev/shm") as location:
    root = Path(location)
    deps, compiled, reports = (root / name for name in ("deps", "compiled", "reports"))
    for folder in (deps, compiled, reports):
        folder.mkdir()
    for member, expected_hash in inputs.items():
        relative = Path(member).relative_to(base)
        module = owner_by_package[relative.parts[0]]
        source_name = relative.name.split("$", 1)[0].removesuffix(".class") + ".java"
        core_path = (Path(f"src/schubert-nk-{module}/src/main/java") / base /
                     relative.parent / source_name)
        assert core_path.read_bytes() == git("show", f"{core}:{core_path}")
        assert core_path.read_bytes() == git("show", f"{package['candidateProductionSource']}:{core_path}")
        dep_sources[str(core_path)] = digest(core_path.read_bytes())
        artifact = package["privateJars"][module]["artifact"]
        archive_path = Path(artifact["path"])
        assert pin(archive_path) == artifact
        with ZipFile(archive_path) as archive:
            payload = archive.read(member)
        assert digest(payload) == expected_hash
        target = deps / member
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    code = run("format", java, "-jar", formatter, "--skip-reflowing-long-strings", "--dry-run",
               "--set-exit-if-changed", fixture)
    if code == 0:
        code = run("checkstyle", java, "-jar", style, "-c", rules, fixture)
    if code == 0:
        code = run("compile", java.with_name("javac"), "--release", 25, "-Werror", "-Xlint:all",
                   "-proc:none", "-g", "-cp", f"{deps}:{jspecify}:{junit}", "-d", compiled, main, fixture)
    if code == 0:
        code = run("test", java, "-jar", junit, "execute", "--disable-ansi-colors", "--disable-banner",
                   "--class-path", f"{compiled}:{deps}:{jspecify}", "--select-method",
                   f"dev.codex.schubert.nk.batch.repository.ExpiryAuditPortTest#{method}",
                   "--reports-dir", reports, "--fail-if-no-tests")
        xml = reports / "TEST-junit-jupiter.xml"
        if xml.is_file():
            xml_hash = digest(xml.read_bytes())
            for case in ET.parse(xml).getroot().findall("testcase"):
                assert case.attrib["name"].removesuffix("()") == method
                result = next((key for key in ("failure", "error", "skipped") if case.find(key) is not None),
                              "passed")
                cases.append(dict(testId="EXPPORT-J011", method=method, outcome=result))
output = dict(actualExit=code, core=core, startEvent=start["eventId"], startedAtUTC=started,
              terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              tools=[pin(path) for path in (java, jspecify, junit, formatter, style, rules)], main=pin(main),
              dependencySourceHashes=dep_sources, dependencyClassHashes=inputs, fixture=pin(fixture), spec=pin(spec),
              steps=steps, caseResults=cases, testXmlSha256=xml_hash, plannedVariants=4, oldTestsRerun=0,
              realDbRuns=0, wholeJarAnalyzerInputs=0, coverage=None, formalDelta=0,
              preflightCorrection="PG40730 source field was the pre-change HEAD. Candidate file SHA-256 applies.")
if code == 0:
    assert len(cases) == 1 and cases[0]["outcome"] == "passed"
manifest = out / "manifest.json"
manifest.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
print(code, cases, pin(manifest))
raise SystemExit(code)
