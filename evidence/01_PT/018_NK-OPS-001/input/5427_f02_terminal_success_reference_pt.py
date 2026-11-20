"""Verify the one ordinary-success reference adapter against a closed JDBC proxy."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


H = runpy.run_path(str(Path(__file__).with_name("5417_f02_expiry_audit_jdbc_pt.py")))
E, PLAN, JAVA, JUNIT, PKG, JSPECIFY, AGENT = (
    H[key] for key in ("E", "PLAN", "JAVA", "JUNIT", "PKG", "JSPECIFY", "AGENT")
)
git, pin, run = (H[key] for key in ("git", "proof", "run"))
MAIN = H["BATCH"] / "main/java" / PKG / "CleanupTerminalRepository.java"
TEST = H["BATCH"] / "test/java" / PKG / "CleanupTerminalReferencesJdbcGraphTest.java"
OLD_BLOCK = b"""    } catch (SQLException known) {
      StorageIoException.preserveFatal(known);
      throw new BatchRepositoryException();
    }
  }

  // SSC199/BUG784/CTERM006"""
NEW_BLOCK = OLD_BLOCK.replace(b"StorageIoException.", b"JdbcFailureGraph.")


def read(path):
    return json.loads(Path(path).read_bytes())


def main(state):
    event = read(next(PLAN.glob("1095_F02*")))
    v = event["values"]
    assert all(pin(row["path"]) == row for row in v["oracleReferences"])
    package = read(v["oracleReferences"][1]["path"])
    previous = package["candidateProductionSource"]
    assert v["source"] == git("rev-parse", "HEAD").decode().strip()
    stored = git("show", f"{previous}:{MAIN}")
    assert stored.count(OLD_BLOCK) == 1
    expected = stored if state == "before" else stored.replace(OLD_BLOCK, NEW_BLOCK).replace(
        b"import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;",
        b"import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;\n"
        b"import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;",
    )
    assert MAIN.read_bytes() == expected
    out = (E / f'{v["run"]}-{state}').resolve()
    out.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix=f"pgpt-cterm-success-{state}-") as temp:
        root = Path(temp)
        models = H["make_classpath"](package["privateJars"], root / "deps")
        main, tests, reports = (root / name for name in ("main", "tests", "reports"))
        for folder in (main, tests, reports):
            folder.mkdir()
        main_input, test_input = root / MAIN.name, root / TEST.name
        main_input.write_bytes(expected)
        test_input.write_bytes(TEST.read_bytes())
        deps = os.pathsep.join(map(str, (root / "deps", JSPECIFY)))
        compile_main = [JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror", "-proc:none", "-g"]
        steps = {"mainCompile": run("mainCompile", [*compile_main, "-cp", deps, "-d", main, main_input], out, root)}
        prefix = str(PKG).replace("/", ".")
        if steps["mainCompile"]["actualExit"] == 0:
            classpath = os.pathsep.join(map(str, (main, JUNIT, deps)))
            steps["testCompile"] = run("testCompile", [*compile_main, "-cp", classpath,
                                                       "-d", tests, test_input], out, root)
        if steps.get("testCompile", {}).get("actualExit") == 0:
            exe = out / "jacoco.exec"
            session = f"PG40740-CTERM-SUCCESS-{state.upper()}"
            steps["unit"] = run("unit", [JAVA, f"-javaagent:{AGENT}=destfile={exe},sessionid={session},"
                                         f"append=false,includes={prefix}.{MAIN.stem}*", "-jar", JUNIT,
                                         "execute", "--disable-banner", "--disable-ansi-colors", "--fail-if-no-tests",
                                         "--class-path", f"{tests}{os.pathsep}{classpath}", "--reports-dir", reports,
                                         "--select-class", f"{prefix}.{TEST.stem}"], out, root)
        outcomes = {}
        xml = reports / "TEST-junit-jupiter.xml"
        physical = {str(p.relative_to(main)): pin(p)["sha256"] for p in main.rglob("*.class")}
        if xml.is_file():
            for node in ET.parse(xml).iter("testcase"):
                outcomes[node.get("name")] = next((kind for kind in ("error", "failure", "skipped")
                                                   if node.find(kind) is not None), "pass")
            steps["abi"] = run("abi", [JAVA.with_name("javap"), "-classpath", main, "-public",
                                       f"{prefix}.{MAIN.stem}"], out, root)
            tool = read(next(E.glob("PG40696-*-after/manifest.json")))["stages"]["unfiltered"]["command"][:4]
            steps["unfiltered"] = run("unfiltered", [*tool, exe, *(main / name for name in sorted(physical))], out, root)
    okay = all(item["actualExit"] == 0 for item in steps.values()) and outcomes == {
        "successfulReferenceQueryPreservesTheOriginalFatalCause()": "pass",
        "ordinaryProviderErrorIsCataloguedAndTheBorrowedConnectionStaysOpen()": "pass",
    }
    proof = dict(
        actualExit=0 if okay else 1, state=state, source=v["source"], preChangeProduction=previous,
        main=pin(MAIN), test=pin(TEST), physical=physical, dependencies=models, stages=steps, testCases=outcomes,
        inMemoryOnly=True, liveDb=False, failureCohortOperation=0, whole451=False, formalDelta=0,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    (out / "manifest.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(dict(exits={name: stage["actualExit"] for name, stage in steps.items()}, cases=outcomes))
    return proof["actualExit"]


if __name__ == "__main__":
    assert sys.argv[1:] in (["before"], ["after"])
    raise SystemExit(main(sys.argv[1]))
