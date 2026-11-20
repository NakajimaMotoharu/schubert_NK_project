"""Check only the new reference DAO test source with the pinned format tools."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def pin(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def execute(*command):
    args = list(map(str, command))
    result = subprocess.run(args, capture_output=True, text=True, timeout=35, check=False)
    return dict(command=args, exitCode=result.returncode, stdout=result.stdout, stderr=result.stderr)


start = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1334_*"))
group = json.loads(start.read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(row["path"])) == row for row in refs)
unit = json.loads(Path(refs[1]["path"]).read_bytes())
file = Path(unit["fixture"]["path"])
assert str(file) == "src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/RunReferenceRepositoryPureJdbcTest.java"
assert pin(file) == unit["fixture"]
assert subprocess.check_output(["git", "show", f'{ctx["source"]}:{file}'], timeout=10) == file.read_bytes()
toolchain = Path("/home/mini/codex/project1/work/toolchain")
jdk = toolchain / "jdk-25.0.4"
formatter = toolchain / "google-java-format-1.36.1-all-deps.jar"
checker = toolchain / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path(refs[3]["path"])
formatting = execute(jdk / "bin/java", "-jar", formatter, "--dry-run", "--set-exit-if-changed", file)
checkstyle = execute(jdk / "bin/java", "-jar", checker, "-c", rules, "-f", "xml", file)
report = ET.fromstring(checkstyle["stdout"])
visited = list(report.findall("file"))
errors = len(report.findall("file/error"))
passed = (formatting["exitCode"] == checkstyle["exitCode"] == 0
          and len(visited) == 1 and visited[0].attrib["name"] == str(file.resolve()) and errors == 0)
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
result = dict(actualExit=0 if passed else 1, source=ctx["productionCoreMain"],
              testCommit=ctx["source"], startEvent=group["eventId"], testId=unit["testId"],
              terminalAtUTC=datetime.now(timezone.utc).isoformat(), fixture=pin(file),
              inputs=list(map(pin, [jdk / "release", formatter, checker, rules])),
              formatting=formatting, checkstyle=checkstyle, observedFiles=len(visited),
              observedFindings=errors, testsRerun=0, productMainAnalyzed=0, wholeF03=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(result["actualExit"], formatting["exitCode"], checkstyle["exitCode"], len(visited), errors)
raise SystemExit(result["actualExit"])
