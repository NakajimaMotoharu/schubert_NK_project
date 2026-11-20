"""Compile the in-memory JDBC fixture against the candidate's actual driver."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from xml.etree import ElementTree


ROOT = Path.cwd()
TOOLCHAIN = ROOT.parent / "toolchain"
CACHE = TOOLCHAIN / "m2/repository"
JAVA = TOOLCHAIN / "jdk-25.0.4/bin/java"
INPUT = Path(__file__).parent
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
PLAN = ROOT / "documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117"
ZONES = ("UTC", "Asia/Tokyo", "America/New_York")


def record(path):
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def assert_dependency(pom, group, name, ver):
    root = ElementTree.fromstring(pom)
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    matches = []
    for dependency in root.findall("m:dependencies/m:dependency", ns):
        if (dependency.findtext("m:groupId", namespaces=ns),
                dependency.findtext("m:artifactId", namespaces=ns)) == (group, name):
            matches.append(dependency.findtext("m:version", namespaces=ns))
    assert matches == [ver]


def call(cmd, cwd, out, label):
    started = datetime.now(timezone.utc).isoformat()
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=60)
    normal = out / (label + ".stdout.txt")
    errors = out / (label + ".stderr.txt")
    normal.write_bytes(p.stdout)
    errors.write_bytes(p.stderr)
    return dict(command=[str(part) for part in cmd], actualExit=p.returncode,
                stdout=record(normal), stderr=record(errors), startedAtUTC=started,
                terminalAtUTC=datetime.now(timezone.utc).isoformat())


def main():
    last = next(PLAN.glob("983_*"))
    start = json.loads(last.read_bytes())["values"]
    out = OPS / start["run"]
    assert all(record(Path(row["path"])) == row for row in start["oracleReferences"])
    assert (out / "first-compile.json").exists()
    vendor = CACHE / "org/postgresql/postgresql/42.7.13/postgresql-42.7.13.jar"
    annotations = CACHE / "org/checkerframework/checker-qual/3.55.1/checker-qual-3.55.1.jar"
    pom = subprocess.check_output(
        ["git", "show", start["productionCoreMain"] + ":src/schubert-nk-bootstrap/pom.xml"]
    )
    assert_dependency(pom, "org.postgresql", "postgresql", "42.7.13")
    assert_dependency(vendor.with_suffix(".pom").read_bytes(),
                      "org.checkerframework", "checker-qual", "3.55.1")
    test = INPUT / "153_PgTemporalRowContract.java"
    vectors = INPUT / "154_PgTemporalRowVectors.tsv"
    inputs = [record(path) for path in (test, vectors, vendor, annotations, vendor.with_suffix(".pom"))]
    wanted = []
    for line in vectors.read_text().splitlines():
        test_id, _, _, expected = line.split("\t")
        wanted.extend((f"{test_id}-TEXT\t{expected}", f"{test_id}-BINARY\t{expected}"))
    wanted.extend(("PT-JDBC42-009-NULL-TEXT\tNULL", "PT-JDBC42-010-NULL-BINARY\tNULL"))
    assert len(wanted) == 18
    with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pgpt-jdbc42-row-") as name:
        work = Path(name)
        fixture = work / "PgTemporalRowContract.java"
        fixture.write_bytes(test.read_bytes())
        classpath = f"{vendor}:{annotations}"
        phases = {"compile": call([JAVA.with_name("javac"), "--release", "25", "-Xlint:all",
                                   "-Werror", "-cp", classpath, "-d", work, fixture],
                                  work, out, "compile")}
        good = 0
        if phases["compile"]["actualExit"] == 0:
            for i, zone in enumerate(ZONES, 1):
                result = call([JAVA, "-Duser.timezone=" + zone, "-cp", f"{work}:{classpath}",
                               "org.postgresql.jdbc.PgTemporalRowContract", vectors.resolve(), zone],
                              work, out, f"zone-{i}")
                actual = Path(result["stdout"]["path"]).read_text().splitlines()
                matches = sum(expected == observed for expected, observed in zip(wanted, actual))
                phases[zone] = dict(result, checksMatched=matches, checksExpected=len(wanted),
                                    noDiagnostic=Path(result["stderr"]["path"]).stat().st_size == 0)
                good += matches
    all_expected = len(ZONES) * len(wanted)
    success = good == all_expected and all(v["actualExit"] == 0 for v in phases.values())
    with (out / "manifest.json").open("x") as f:
        json.dump(dict(actualExit=int(not success), productionCore=start["productionCoreMain"],
                       fixtureSource="17fb9c3397", stages=phases, inputs=inputs,
                       matches=good, expected=all_expected, zones=ZONES, oldProductRunsRepeated=0,
                       jdbcClass="org.postgresql.jdbc.PgResultSet", realDbConnections=0,
                       actualServerSessionZones=0, wholeP00405Accepted=False, whole451Accepted=False,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()), f, indent=2)
        f.write("\n")
    print(success, good, all_expected, {key: value["actualExit"] for key, value in phases.items()})
    return int(not success)


if __name__ == "__main__":
    raise SystemExit(main())
