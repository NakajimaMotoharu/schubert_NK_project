"""Exercise only the current ScenarioRecordStream fixture in a new owned local run."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


REPO = Path.cwd()
LOCAL = (REPO.parent / "pgpt-runs/PG379").resolve()
PUBLIC = REPO / "evidence/01_PT/018_NK-OPS-001/evidence"
RUN = "PG43080-scenario-stream-finite-current-v1"
BASE = "dev/codex/schubert/nk/api/storage"
PRODUCTION = "src/schubert-nk-api/src/main/java/"
TESTS = "src/schubert-nk-api/src/test/java/"
PRIMARY = BASE + "/ScenarioRecordStream.class"
CORE = "87927ea17c1c8dbef528bc0c6882c24b1fe7c871"
STORAGE_NAMES = {
    "dev/codex/schubert/nk/storage/" + name + ".class"
    for name in ("StorageIoException", "StorageIoException$Reason")
}
EXPECTED_TEST_PHYSICAL = {BASE + "/ScenarioRecordStreamTest" + suffix + ".class"
                          for suffix in ("", "$FaultChannel")}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def load(path):
    return json.loads(path.read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def unix_time():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    with path.open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def verify_physical(root, expected):
    assert {p.relative_to(root).as_posix() for p in root.rglob("*.class")} == expected


def prepare_sources(folder, snapshot):
    main, package = [PRODUCTION + BASE + "/" + name for name in (
        "ScenarioRecordStream.java", "package-info.java")]
    test = TESTS + BASE + "/ScenarioRecordStreamTest.java"
    for path in (main, package, test):
        git_source = CORE if path != test else snapshot
        data = git("show", f"{git_source}:{path}")
        assert Path(path).read_bytes() == data
        if path != test:
            assert git("show", f"{snapshot}:{path}") == data
            selected = folder / "src/main/java" / Path(path).relative_to(PRODUCTION)
            selected.parent.mkdir(parents=True, exist_ok=True)
            selected.write_bytes(data)
    return main, package, test


def prepare_dependencies(folder):
    receipt, = PUBLIC.glob("PG43066*/manifest.json")
    regular = load(receipt)["normalArtifacts"]
    paths = {}
    for module in ("protocol", "storage"):
        baseline = regular[module]
        paths[module] = Path(baseline["jar"]["path"])
        assert pin(paths[module]) == baseline["jar"]
        assert git("rev-parse", f"{CORE}:src/schubert-nk-{module}/src/main").decode().strip() == baseline["mainTree"]
    protocol = paths["protocol"]
    roster_src, = (LOCAL / "PG43018-f02-sax-direct-file-v1").glob("current-protocol-v2/scope-proof.json")
    roster = load(roster_src)
    assert pin(protocol) == roster["protocolJar"]
    with ZipFile(protocol) as archive:
        names = [name for name in archive.namelist() if name.endswith(".class")]
        assert len(names) == 176 and sorted(names) == sorted(roster["exactPermittedPhysicalNames"])
    storage = folder / "qualified-storage-exceptions.jar"
    with ZipFile(paths["storage"]) as original, ZipFile(storage, "x", ZIP_DEFLATED) as selected:
        for name in sorted(STORAGE_NAMES):
            assert original.namelist().count(name) == 1
            selected.writestr(name, original.read(name))
    return protocol, storage, receipt, regular["storage"]["jar"]


def commands(folder, main, test, protocol, storage):
    former, = LOCAL.glob("PG43062-transfer-verification-fatal-contract-v1")
    typed, = LOCAL.glob("PG43064-transfer-test-checked-declaration-v1")
    checked = load(former / "begin.json")["commands"]
    static = load(typed / "begin.json")["commands"]
    pom = (former / "pom.xml").read_text()
    old_aux = former / "qualified-four-safe-types.jar"
    assert pom.count(str(old_aux)) == 1
    (folder / "pom.xml").write_text(pom.replace(
        str(old_aux), str(storage)).replace("api-transfer-content-allowed", "api-scenario-stream-allowed")
        .replace("</dependencies>", (
            "<dependency><groupId>dev.codex.schubert.quality.local</groupId>"
            "<artifactId>qualified-protocol</artifactId><version>1</version><scope>system</scope>"
            f"<systemPath>{protocol}</systemPath></dependency></dependencies>")))
    def adapt(arg):
        return (arg.replace(str(former), str(folder)).replace(str(typed), str(folder))
                .replace(str(folder / old_aux.name), os.pathsep.join(map(str, (protocol, storage))))
                .replace("PG43062-current", "PG43080-current")
                .replace("TransferContentVerifier", "ScenarioRecordStream"))
    planned = {
        key: [adapt(arg) for arg in checked[key]]
        for key in ("format", "style", "compileNullaway", "fixtures", "junit", "rawCompile", "unfiltered")
    }
    (folder / "current-static-sources.txt").write_text(main + "\n" + test + "\n")
    for key in ("pmd", "spotbugs"):
        planned[key] = [adapt(arg) for arg in static[key]]
    return planned


def main():
    folder = LOCAL / RUN
    folder.mkdir(mode=0o700)
    for name in ("test", "xml", "owned-temp", "meter"):
        (folder / name).mkdir()
    snapshot = git("rev-parse", "HEAD").decode().strip()
    main_source, package, test = prepare_sources(folder, snapshot)
    protocol, storage, source_receipt, original_storage = prepare_dependencies(folder)
    planned = commands(folder, main_source, test, protocol, storage)
    order = ("format", "style", "compileNullaway", "fixtures", "junit", "rawCompile",
             "unfiltered", "pmd", "spotbugs")
    jdk = REPO.parent / "toolchain/jdk-25.0.4"
    write_json(folder / "begin.json", dict(
        run=RUN, source=snapshot, productCore=CORE, startedAtUTC=unix_time(),
        inputs=[pin(REPO / name) for name in (main_source, package, test)],
        acceptedArtifacts=pin(source_receipt), protocol=pin(protocol), selectedStorage=pin(storage),
        storageParent=original_storage, storageNames=sorted(STORAGE_NAMES), commands=planned,
        expectedPrimary=[PRIMARY, BASE + "/package-info.class"],
        expectedFixture=sorted(EXPECTED_TEST_PHYSICAL),
    ))
    for stage in order:
        stdout, stderr = [folder / f"{stage}.{stream}" for stream in ("stdout", "stderr")]
        with stdout.open("xb") as out, stderr.open("xb") as err:
            result = subprocess.run(planned[stage], cwd=REPO, stdout=out, stderr=err,
                                    env={**os.environ, "JAVA_HOME": str(jdk)}, timeout=120)
        write_json(folder / f"{stage}.end.json", dict(
            actualExit=result.returncode, at=unix_time(), stdout=pin(stdout), stderr=pin(stderr)))
        print(stage, result.returncode, flush=True)
        allowed = {"pmd": {0, 4}, "spotbugs": {0, 1}}.get(stage, {0})
        if result.returncode not in allowed:
            raise SystemExit(result.returncode)
        if stage == "compileNullaway":
            verify_physical(folder / "target/classes", {PRIMARY, BASE + "/package-info.class"})
        if stage == "fixtures":
            verify_physical(folder / "test", EXPECTED_TEST_PHYSICAL)
    prior = load(PUBLIC / "PG43078-scenario-writer-current-evidence-v1/manifest.json")
    suite_path = folder / "xml/TEST-junit-jupiter.xml"
    suite = ET.parse(suite_path).getroot()
    actual = [c.get("name").removesuffix("()") for c in suite.findall("testcase")]
    assert sorted(actual) == sorted(prior["streamOriginalFiveMethods"])
    assert suite.get("tests") == "5" and all(suite.get(k) == "0" for k in ("failures", "errors", "skipped"))
    assert not any((folder / "owned-temp").iterdir())
    write_json(folder / "terminal.json", dict(
        actualExit=0, finishedAtUTC=unix_time(), source=snapshot, productCore=CORE, names=actual,
        xml=pin(suite_path), exec=pin(folder / "unit.exec"),
        main=pin(folder / "target/classes" / PRIMARY), counters=pin(folder / "unfiltered.stdout"),
        ownedTempFinalEntries=0, failures=0, errors=0, skipped=0,
    ))


if __name__ == "__main__":
    main()
