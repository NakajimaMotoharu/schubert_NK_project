"""Execute the existing LogQuery audit proxy fixture with exact current source pins."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import sys
import tempfile


def hash_bytes(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=hash_bytes(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


phase, source = sys.argv[1:]
assert phase in ("before", "after")
plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
start = read(next(plan.glob("1272_*")))
values = start["values"]
assert all(hash_bytes(git("show", f'{values["source"]}:{item["path"]}')) == item["sha256"]
           for item in values["oracleReferences"])
old = read(next(evidence.glob("PG27120-*/manifest.json")))["begin"]
jar_receipt = read(next(evidence.glob("PG40802-*/manifest.json")))
references = read(next(evidence.glob("PG40840-*/manifest.json")))
protocol = references["priorSourceUnchangedLibraryReferences"]["protocol"]
jar = Path(protocol["path"])
assert jar.stat().st_size == protocol["fileBytes"] and pin(jar)["sha256"] == protocol["sha256"]
main = Path("src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/log/LogQueryAuditWriter.java")
fixture = Path("src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/log/LogSearchAuditPortTest.java")
spec = Path("evidence/01_PT/010_NK-ADM-001/087_QA054ログ検索成功監査writer単体仕様.md")
base_source = values["productionCoreMain"]
source_inputs = sorted(Path(path) for path in old["inputHashes"]
                       if path.startswith("src/schubert-nk-api/src/main/java/"))
assert len(source_inputs) == 19 and main in source_inputs
assert all(path.read_bytes() == git("show", f"{source}:{path}") for path in source_inputs)
assert not git("diff", "--name-only", jar_receipt["source"], source, "--", "pom.xml",
               "src/schubert-nk-protocol/pom.xml", "src/schubert-nk-protocol/src/main")
diff_main = git("diff", "--name-only", base_source, source, "--", "src",
                ":(exclude)src/**/src/test/**").decode().splitlines()
if phase == "before":
    assert source == base_source and diff_main == []
else:
    assert git("rev-parse", "HEAD").decode().strip() == source and diff_main == [str(main)]
    assert fixture.read_bytes() == git("show", f"{source}:{fixture}")

constants = Path.cwd().parent / "toolchain"
java = constants / "jdk-25.0.4/bin/java"
junit = constants / "junit-platform-console-standalone-1.13.4.jar"
dependencies = [jar, *(Path(path) for path in old["dependencies"]
                       if Path(path).name in ("gson-2.14.0.jar", "jspecify-1.0.1.jar",
                                              "error_prone_annotations-2.48.0.jar"))]
assert len(dependencies) == 4
assert all(pin(path)["sha256"] == old["dependencies"][str(path)] for path in dependencies[1:])
formatter = constants / "google-java-format-1.36.1-all-deps.jar"
style = constants / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path("tools/quality/static/checkstyle.xml")
out = evidence / (values["run"] + "-before" if phase == "before" else "PG40862-log-search-audit-null-v1-after")
out.mkdir()
started = datetime.now(timezone.utc).isoformat()
stages = {}
observed = []
report_hash = None
test_class = "dev.codex.schubert.nk.api.application.log.LogSearchAuditPortTest"
method = "searchPort009MissingStatementUsesFixedSqlFailureBeforeBinding"


def run(name, *args):
    command = list(map(str, args))
    result = subprocess.run(command, capture_output=True, timeout=60)
    stages[name] = dict(command=command, exit=result.returncode, stdoutSha256=hash_bytes(result.stdout),
                        stderrSha256=hash_bytes(result.stderr))
    if result.returncode and name != "test":
        print(name, result.stderr.decode(errors="replace")[:1200])
    return result.returncode


with tempfile.TemporaryDirectory(dir="/dev/shm", prefix=f"pg40860-{phase}-") as place:
    area = Path(place)
    classes = area / "classes"
    reports = area / "reports"
    reports.mkdir()
    classpath = ":".join(str(path) for path in dependencies)
    checked = [fixture] if phase == "before" else [main, fixture]
    status = run("format", java, "-jar", formatter, "--skip-reflowing-long-strings",
                 "--dry-run", "--set-exit-if-changed", *checked)
    if status == 0:
        status = run("checkstyle", java, "-jar", style, "-c", rules, *checked)
    if status == 0:
        status = run("compile", java.with_name("javac"), "--release", 25, "-Xlint:all", "-Werror",
                     "-proc:none", "-g", "-cp", f"{classpath}:{junit}", "-d", classes,
                     *source_inputs, fixture)
    if status == 0:
        selector = ("--select-method", f"{test_class}#{method}") if phase == "before" else ("--select-class", test_class)
        status = run("test", java, "-jar", junit, "execute", "--disable-banner", "--disable-ansi-colors",
                     "--class-path", f"{classes}:{classpath}", "--fail-if-no-tests",
                     "--reports-dir", reports, *selector)
        xml = reports / "TEST-junit-jupiter.xml"
        if xml.is_file():
            body = xml.read_bytes()
            report_hash = hash_bytes(body)
            for case in ET.fromstring(body).findall("testcase"):
                name = case.get("name").removesuffix("()")
                number = name.removeprefix("searchPort")[:3]
                assert number in {str(i).zfill(3) for i in range(1, 10)}
                outcome = next((key for key in ("failure", "error", "skipped") if case.find(key) is not None), "passed")
                root_cause = ("NullPointerException" if outcome == "failure" and
                              "but was: <java.lang.NullPointerException>" in case.find("failure").get("message", "")
                              else None)
                observed.append(dict(testId="PT-ADM-SEARCHPORT" + number, method=name,
                                     outcome=outcome, actualUnexpectedFailureType=root_cause))
    if phase == "before":
        verified = (status == 1 and len(observed) == 1 and observed[0]["method"] == method
                    and observed[0]["actualUnexpectedFailureType"] == "NullPointerException")
    else:
        verified = (status == 0 and sorted(item["testId"][-3:] for item in observed) ==
                    [str(i).zfill(3) for i in range(1, 10)] and
                    all(item["outcome"] == "passed" for item in observed))
    physical = {str(path.relative_to(classes)): pin(path)["sha256"]
                for path in classes.rglob("LogQueryAuditWriter*.class")}
record = dict(phase=phase, actualExit=status, qualificationMatched=verified, source=source,
              sourceAtGroupStart=base_source, startEvent=start["eventId"], startedAtUTC=started,
              terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              sourceInputs=[pin(path) for path in source_inputs], fixture=pin(fixture), spec=pin(spec),
              dependencyAndToolPins=[pin(path) for path in [*dependencies, java, junit, formatter, style, rules]],
              stages=stages, testXmlSha256=report_hash, cases=observed, changedWriterClassHashes=physical,
              realDbRuns=0, realServiceRuns=0, whole451=False, coverage=None, formalDelta=0)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(status, verified, [item["outcome"] for item in observed], pin(manifest))
raise SystemExit(0 if verified else 1)
