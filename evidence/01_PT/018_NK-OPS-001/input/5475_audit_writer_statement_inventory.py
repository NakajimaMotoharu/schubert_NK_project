"""Read JDBC writer boundaries and preserve an unapplied null-contract patch."""
from datetime import datetime, timezone
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import tempfile


def sha(value):
    return sha256(value).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
group = json.loads(next(plan.glob("1310_*")).read_bytes())
values = group["values"]
core = values["productionCoreMain"]
assert all(pin(Path(row["path"])) == row for row in values["oracleReferences"])
base = Path("src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api")
expected = {
    "LogQueryAuditWriter": "UNGUARDED",
    "QuestionMutationAuditWriter": "UNGUARDED",
    "QuestionQueryAuditWriter": "UNGUARDED",
    "ScenarioAuditWriter": "UNGUARDED",
    "UserAuditWriter": "UNGUARDED",
    "UserQueryAuditWriter": "UNGUARDED",
    "UserRequestAuditWriter": "UNGUARDED",
    "LoginAuditWriter": "REQUIRED_COLUMN",
    "SessionAuditWriter": "REQUIRED_COLUMN",
}
assert {p.stem for p in base.rglob("*AuditWriter.java")} == set(expected)
entries = []
target = None
for name, expected_classification in expected.items():
    path, = base.rglob(name + ".java")
    body = git("show", f"{core}:{path}").decode()
    assert path.read_text() == body
    sites = list(re.finditer(r"\bprepareStatement\s*\(", body))
    assert len(sites) == 1
    site = sites[0].start()
    proven = ("RequiredColumn.requireValue" in body and
              re.search(r"\brequireValue\s*\(\s*\w+\.\s*$", body[:site]) is not None)
    classification = "REQUIRED_COLUMN" if proven else "UNGUARDED"
    assert classification == expected_classification, name
    entries.append(dict(file=pin(path), resourceContract=classification,
                        acquisitionLine=body.count("\n", 0, site) + 1, dynamicRun=False))
    if name == "LogQueryAuditWriter":
        target = path
assert target is not None
old = target.read_text()
added_import = "\nimport static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;\n"
candidate = old.replace("import com.google.gson.JsonObject;", added_import.lstrip() + "\nimport com.google.gson.JsonObject;", 1)
candidate = candidate.replace("        connection.prepareStatement(", "        requireValue(connection.prepareStatement(", 1)
candidate = candidate.replace('            """)) {', '            """))) {', 1)
assert candidate.count("requireValue(") == 1 and candidate != old
assert 'connection.prepareStatement(' in candidate

tools = Path.cwd().parent / "toolchain"
java = tools / "jdk-25.0.4/bin/java"
fmt = tools / "google-java-format-1.36.1-all-deps.jar"
cs = tools / "static-gates-20261015/checkstyle-14.3.0-all.jar"
rules = Path("tools/quality/static/checkstyle.xml").resolve()
with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40894-") as area:
    copy = Path(area) / target.name
    copy.write_text(candidate)
    subprocess.run([java, "-jar", fmt, "--skip-reflowing-long-strings", "-i", copy],
                   capture_output=True, check=True, timeout=20)
    style = subprocess.run([java, "-jar", cs, "-c", rules, copy], capture_output=True, timeout=20)
    assert style.returncode == 0
    candidate = copy.read_text()


def sql_token(body):
    token, = re.findall(r'"""\n(.*?)"""', body, flags=re.DOTALL)
    lines = token.splitlines()
    indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
    return "".join(line[indent:] + "\n" for line in lines if line.strip())


assert sql_token(candidate) == sql_token(old)
assert candidate.count("statement.set") == old.count("statement.set")
assert not re.findall(r"connection\.(close|commit|rollback|setAutoCommit)\(", candidate)
proposal = Path("evidence/01_PT/018_NK-OPS-001/input/5476_log_query_audit_writer_fix_proposed.patch")
patch = "".join(unified_diff(old.splitlines(keepends=True), candidate.splitlines(keepends=True),
                            fromfile=f"a/{target}", tofile=f"b/{target}", n=0))
with proposal.open("x") as stream:
    stream.write(patch)
subprocess.run(["git", "apply", "--check", "--unidiff-zero", str(proposal)], check=True, timeout=15)
assert target.read_text() == old
assert not git("diff", "--name-only", "--", str(target))
out = Path("evidence/01_PT/018_NK-OPS-001/evidence") / values["run"]
out.mkdir()
record = dict(actualExit=0, source=core, startEvent=group["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              findings=entries, proposedPatch=pin(proposal), exactStatementTextUnchanged=True,
              checkstyleProposedSourceExit=style.returncode, productionPatchApplied=False,
              compileOrProductTestsStarted=0, heldTypesOpened=0, qa056StillOnHold=True,
              bug="BUG-3417", expansion="YKT-2739", whole451=False, formalDelta=0)
manifest = out / "manifest.json"
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(pin(manifest), len(entries))
