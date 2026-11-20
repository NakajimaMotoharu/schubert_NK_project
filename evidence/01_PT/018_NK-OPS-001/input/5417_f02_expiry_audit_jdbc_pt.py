"""Run the approved memory-only ExpiryAudit JDBC contract before or after SSC-461."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path.cwd()
E = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PLAN = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
PKG = Path("dev/codex/schubert/nk/batch/repository")
BATCH = Path("src/schubert-nk-batch/src")
TARGET = BATCH / "main/java" / PKG / "ExpiryAuditRepository.java"
TEST = BATCH / "test/java" / PKG / "ExpiryAuditJdbcFailureGraphTest.java"
SDK = ROOT.parent / "toolchain"
JAVA = SDK / "jdk-25.0.4/bin/java"
JUNIT = SDK / "junit-platform-console-standalone-1.13.4.jar"
JAR_REPO = SDK / "m2/repository"
JSPECIFY = JAR_REPO / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
AGENT = JAR_REPO / "org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"


def git(*args):
    return subprocess.check_output(["git", *args], timeout=20)


def proof(path):
    return {"path": str(path), "sha256": sha256(Path(path).read_bytes()).hexdigest()}


def run(stage, cmd, output, cwd):
    args = list(map(str, cmd))
    result = subprocess.run(args, cwd=cwd, capture_output=True, timeout=60, check=False,
                            env={"LANG": "C.UTF-8", "PATH": "/usr/bin:/bin"})
    logs = {}
    for label, body in (("stdout", result.stdout), ("stderr", result.stderr)):
        path = output / f"{stage}.{label}"
        path.write_bytes(body)
        logs[label] = proof(path)
    return dict(actualExit=result.returncode, command=args, **logs)


def make_classpath(receipts, parent):
    base = "dev/codex/schubert/nk/"
    types = {
        "batch": [*(f"batch/repository/{name}" for name in (
            "BatchRepositoryException", "BatchRun", "BatchStep", "BatchStepAttempt", "BatchStepResult",
            "BatchStepResult$Status", "BatchStepResult$Reason", "JdbcResourceFailures",
            "RunReferenceRepository", "RunReferences", "SuccessRunLookup"))],
        "bootstrap": ["api/bootstrap/JdbcFailureGraph", "bootstrap/MaintenanceOwnerFrame$Guard",
                      "bootstrap/MaintenanceOwnerFrame"],
        "storage": ["storage/StorageIoException", "storage/StorageIoException$Reason"],
    }
    output = {}
    for artifact, names in types.items():
        receipt = receipts[artifact]["artifact"]
        assert proof(receipt["path"]) == receipt
        with ZipFile(receipt["path"]) as archive:
            for name in names:
                member = f"{base}{name}.class"
                data = archive.read(member)
                target = parent / member
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                output[member] = sha256(data).hexdigest()
    return output


def main(mode):
    output = (E / f"PG40696-f02-expiry-audit-jdbc-owner-v2-{mode}").resolve()
    group = json.loads(next(PLAN.glob("1055_F02*")).read_bytes())
    values = group["values"]
    for item in values["oracleReferences"]:
        assert proof(item["path"]) == item
    base_core = values["productionCoreMain"]
    gate = json.loads(Path(values["oracleReferences"][2]["path"]).read_bytes())
    assert gate["productionCore"] == base_core
    head = git("rev-parse", "HEAD").decode().strip()
    assert head == values["source"]
    baseline = git("show", f"{base_core}:{TARGET}")
    edited = TARGET.read_bytes()
    pure_move = baseline.replace(
        b"import dev.codex.schubert.nk.storage.StorageIoException;",
        b"import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;",
    ).replace(b"StorageIoException.preserveFatal(", b"JdbcFailureGraph.preserveFatal(")
    assert baseline.count(b"StorageIoException.preserveFatal(") == 4
    assert (baseline if mode == "before" else pure_move) == edited
    test = TEST.read_bytes()
    output.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix=f"pgpt-expiry-{mode}-") as scratch:
        work = Path(scratch)
        fixed = make_classpath(gate["packagedBuild"], work / "deps")
        main_dir, test_dir, report = (work / label for label in ("main", "test", "xml"))
        for directory in (main_dir, test_dir, report):
            directory.mkdir()
        actual_main, actual_test = work / TARGET.name, work / TEST.name
        actual_main.write_bytes(edited)
        actual_test.write_bytes(test)
        cp = os.pathsep.join(map(str, (work / "deps", JSPECIFY)))
        session = f"PG40696-EXPIRY-JDBC-{mode.upper()}"
        stages = {"compile": run("compile", [
            JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none", "-g", "-cp", cp,
            "-d", main_dir, actual_main], output, work)}
        if stages["compile"]["actualExit"] == 0:
            stages["testCompile"] = run("testCompile", [
                JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                "-cp", os.pathsep.join(map(str, (main_dir, cp, JUNIT))), "-d", test_dir, actual_test], output, work)
        if stages.get("testCompile", {}).get("actualExit") == 0:
            stages["unit"] = run("unit", [
                JAVA, f"-javaagent:{AGENT}=destfile={output/'jacoco.exec'},sessionid={session},append=false,"
                f"includes={str(PKG).replace('/', '.')}.ExpiryAuditRepository*",
                "-jar", JUNIT, "execute", "--disable-banner", "--disable-ansi-colors", "--fail-if-no-tests",
                "--class-path", os.pathsep.join(map(str, (main_dir, test_dir, cp))), "--reports-dir", report,
                "--select-class", f"{str(PKG).replace('/', '.')}.{TEST.stem}"], output, work)
        results = {}
        xml = report / "TEST-junit-jupiter.xml"
        if xml.is_file():
            portable = output / "junit.xml"
            root = ET.parse(xml).getroot()
            for child in tuple(root):
                if child.tag not in {"testcase"}:
                    root.remove(child)
            for case in root.findall("testcase"):
                for child in tuple(case):
                    if child.tag in {"system-out", "system-err"}:
                        case.remove(child)
            ET.ElementTree(root).write(portable, encoding="utf-8", xml_declaration=True)
            results = {name: int(root.attrib[name]) for name in ("tests", "failures", "errors", "skipped")}
        physical = {str(p.relative_to(main_dir)): proof(p)["sha256"] for p in main_dir.rglob("*.class")}
        abi = run("abi", [JAVA.with_name("javap"), "-classpath", main_dir, "-public",
                          f"{str(PKG).replace('/', '.')}.{TARGET.stem}"], output, work)
        stages["abi"] = abi
        if results.get("tests"):
            coverage_source = next(E.glob("PG40614-*/manifest.json"))
            tool = json.loads(coverage_source.read_bytes())["stages"]["raw"]["command"][:4]
            stages["unfiltered"] = run("unfiltered", [
                *tool, output / "jacoco.exec", *(main_dir / name for name in sorted(physical))], output, work)
            stages["bytecode"] = run("bytecode", [
                JAVA.with_name("javap"), "-classpath", main_dir, "-c", "-private",
                f"{str(PKG).replace('/', '.')}.{TARGET.stem}"], output, work)
        success = results == dict(tests=8, failures=0, errors=0, skipped=0) and all(
            value["actualExit"] == 0 for value in stages.values()
        )
        data = dict(
            mode=mode, groupStart=group["eventId"], baselineCore=base_core, checkoutHead=head,
            actualExit=0 if success else 1, unit=results, stages=stages, main=proof(TARGET),
            test=proof(TEST), physical=physical, pinnedAllowedDependencies=fixed,
            session=session, actualExternalActions=0, all451=False, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        )
        (output / "manifest.json").write_text(json.dumps(data, indent=2) + "\n")
        print({"mode": mode, "unit": results, "stages": {key: row["actualExit"] for key, row in stages.items()}})
        return data["actualExit"]


if __name__ == "__main__":
    assert sys.argv[1:] in (["before"], ["after"])
    raise SystemExit(main(sys.argv[1]))
