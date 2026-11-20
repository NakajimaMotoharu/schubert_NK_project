"""Verify the exact current Storage failure types with ordinary memory tests."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from xml.etree import ElementTree as XML
from zipfile import ZipFile


ROOT = Path.cwd()
TOOLS = ROOT.parent / "toolchain"
JAVA = TOOLS / "jdk-25.0.4/bin/java"
REPO = TOOLS / "m2/repository"
JUNIT = TOOLS / "junit-platform-console-standalone-1.13.4.jar"
AGENT = REPO / "org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
NULLABILITY = REPO / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PLAN = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
PKG = "dev.codex.schubert.nk.storage"
TEST_PATH = Path("src/schubert-nk-storage/src/test/java") / PKG.replace(".", "/")
NAMES = ("StorageFailureGraphTest", "StorageReasonValueContractTest")
PHYSICAL = tuple(PKG.replace(".", "/") + "/StorageIoException" + inner + ".class" for inner in ("", "$Reason"))
CASE_IDS = {
    "fixedReasonsAndNullContract", "directCauseAndSuppressedIdentityAndOrder",
    "sqlNextAndMixedEdgesRetainIdentity", "nonFatalCyclesAndDuplicateEdgesFinishWithoutMutation",
    "injectedGraphRejectsNullInputsBeforeCallingTheEdge",
}


def pin(p):
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def checked(ref):
    p = Path(ref["path"])
    assert pin(p) == ref
    return p


def read(p):
    return json.loads(p.read_bytes())


def write(p, body):
    with p.open("x") as fp:
        json.dump(body, fp, ensure_ascii=False, indent=2)
        fp.write("\n")


def run(args, root, out, label):
    result = subprocess.run(args, cwd=root, capture_output=True, timeout=60)
    stdout, stderr = out / (label + ".stdout"), out / (label + ".stderr")
    stdout.write_bytes(result.stdout)
    stderr.write_bytes(result.stderr)
    return dict(actualExit=result.returncode, command=[str(x) for x in args], stdout=pin(stdout),
                stderr=pin(stderr), terminalAtUTC=datetime.now(timezone.utc).isoformat())


def bin_report(origin):
    fp = next(OPS.glob("PG31432-*/compile.json"))
    m = read(fp)
    jars = [checked(dep).resolve() for dep in m["dependencies"]]
    build = m["command"][m["command"].index("-d") + 1]
    bin_path = Path(build) / "org/jacoco/core/internal/analysis/UnfilteredCodeMeasurement.class"
    assert pin(bin_path)["sha256"] == read(origin)["rawAnalyzer"]["sha256"]
    return ":".join([build, *map(str, jars)])


def main():
    v = read(next(PLAN.glob("992_*")))["values"]
    refs = [checked(ref) for ref in v["oracleReferences"]]
    physical_jar = checked(read(refs[3])["packagedBuild"]["storage"]["artifact"])
    crc_expected = {r["name"] + ".class": r["currentCrc"] for run in read(refs[1])["independentSourceRuns"]
                    for r in run["checked"] if r["name"] + ".class" in PHYSICAL}
    assert len(crc_expected) == len(PHYSICAL) == 2
    protocol_meta = next(OPS.glob("PG40602-*/manifest.json"))
    cp = bin_report(protocol_meta)
    unit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    main_delta = subprocess.check_output(
        ["git", "diff", "--name-only", v["productionCoreMain"], unit, "--", ":(glob)src/**/src/main/**"]
    )
    assert not main_delta
    out = (OPS / v["run"]).resolve()
    out.mkdir()
    private = ROOT.parent / "pgpt-runs/PG379/pg40614-storage-caddy-companions-retained-v1"
    private.mkdir(mode=0o700)
    with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pgpt-current-storage-two-") as work:
        root = Path(work)
        main = root / "main"
        with ZipFile(physical_jar) as jar:
            for name in PHYSICAL:
                assert name in jar.namelist()
                file = main / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(jar.read(name))
        files = []
        for name in NAMES:
            expected_path = TEST_PATH / (name + ".java")
            frozen = root / expected_path.name
            frozen.write_bytes(subprocess.check_output(["git", "show", f"{unit}:{expected_path}"]))
            files.append(frozen)
        tests = root / "test"
        label = "PG40614-STORAGE-CADDY-COMPANIONS"
        exec_file = private / "jacoco.exec"
        xml_dir = private / "xml"
        stages = {
            "compile": run([JAVA.with_name("javac"), "--release", "25", "-Xlint:all", "-Werror",
                            "-proc:none", "-cp", f"{main}:{JUNIT}:{NULLABILITY}", "-d", tests, *files],
                           root, out, "compile")
        }
        assert stages["compile"]["actualExit"] == 0
        stages["test"] = run([JAVA, f"-javaagent:{AGENT}=destfile={exec_file},sessionid={label},append=false,includes={PKG}.StorageIoException*",
                              "-jar", JUNIT, "execute", "--disable-banner", "--disable-ansi-colors",
                              "--class-path", f"{main}:{tests}", "--reports-dir", xml_dir,
                              *[part for name in NAMES for part in ("--select-class", PKG + "." + name)]],
                             root, out, "test")
        assert stages["test"]["actualExit"] == 0
        report = xml_dir / "TEST-junit-jupiter.xml"
        suite = XML.parse(report).getroot()
        nodes = suite.findall("testcase")
        names = {node.get("name").removesuffix("()") for node in nodes if node.get("classname").endswith(NAMES[0])}
        assert names == CASE_IDS and len(nodes) == 6 and int(suite.get("tests")) == 6
        assert all(int(suite.get(key)) == 0 for key in ("failures", "errors", "skipped"))

        stages["raw"] = run([JAVA, "-cp", cp, "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
                             exec_file, *[main / name for name in PHYSICAL]], root, out, "unfiltered")
        assert stages["raw"]["actualExit"] == 0
        raw = Path(stages["raw"]["stdout"]["path"]).read_text()
        classes = {line.split("\t")[1] + ".class": line.split("\t")[2:]
                   for line in raw.splitlines() if line.startswith("CLASS\t")}
        assert classes.keys() == set(PHYSICAL)
        assert all(values[0] == crc_expected[name] for name, values in classes.items())
        coverage = {name: {row.split(":")[0]: tuple(map(int, row.split(":")[1:]))
                           for row in runs[4:]} for name, runs in classes.items()}
        passed = all(miss == 0 for counters in coverage.values() for miss, _ in counters.values())
        write(out / "manifest.json", dict(
            actualExit=0, currentCore=v["productionCoreMain"], testSource=unit, tests=6, newDefinitions=1,
            failed=0, errors=0, skipped=0, notRun=0, singleExec=pin(exec_file), originalXml=pin(report),
            executedExactCases=[dict(className=row.get("classname"), name=row.get("name")) for row in nodes],
            selectedJar=pin(physical_jar), physicalClassNames=list(PHYSICAL), coverage=coverage,
            localRawFour100=passed, classCrc=crc_expected, stages=stages, liveCaddyOrStorageOps=0,
            realNativeOrExternalOps=0, oldExecMerged=False, whole451Accepted=False,
            terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        ))
    print(pin(out / "manifest.json"), passed, coverage)


if __name__ == "__main__":
    main()
