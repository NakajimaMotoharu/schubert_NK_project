"""Run F03 static gates on the two approved, dependency-closed API Outbox value types."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

ROOT = Path.cwd()
EVIDENCE = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
PLAN = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
RUN = "PG40688-f03-outbox-two-pure-current-static-v1"
OUT = EVIDENCE / RUN
PACKAGE = Path("dev/codex/schubert/nk/api/messaging/outbound")
DIRECTORY = Path("src/schubert-nk-api/src/main/java") / PACKAGE
NAMES = ("OutboxRetrySchedule", "OutboxDispatchReport")
XML_NS = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def git(*args):
    return subprocess.check_output(["git", *args], timeout=15)


def digest_file(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def put(name, contents):
    with (OUT / name).open("x") as file:
        json.dump(contents, file, indent=2, ensure_ascii=False)
        file.write("\n")


def execute(stage, command, directory, java_home):
    now = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(
        list(map(str, command)), cwd=directory, capture_output=True, check=False, timeout=75,
        env={**os.environ, "JAVA_HOME": str(java_home), "LC_ALL": "C.UTF-8"},
    )
    files = {}
    for kind, body in (("stdout", result.stdout), ("stderr", result.stderr)):
        target = OUT / f"{stage}.{kind}"
        with target.open("xb") as output:
            output.write(body)
        files[kind] = dict(path=str(target.relative_to(ROOT)), sha256=digest_file(target))
    return dict(actualExit=result.returncode, command=list(map(str, command)), startedAtUTC=now,
                terminalAtUTC=datetime.now(timezone.utc).isoformat(), **files)


def main():
    start = read(next(PLAN.glob("1052_F03*")))
    group = start["values"]
    assert group["run"] == RUN
    assert all(digest_file(ref["path"]) == ref["sha256"] for ref in group["oracleReferences"])
    core = group["productionCoreMain"]
    assert group["source"] == git("rev-parse", "HEAD").decode().strip()
    old, joined = (read(entry["path"]) for entry in group["oracleReferences"][1:3])
    assert old["currentRaw"] == joined["originalRaw"] == 281
    assert joined["assignedBefore"] + joined["closedHere"] + joined["remaining"] == 281
    assert digest_file(joined["unresolved"]["path"]) == joined["unresolved"]["sha256"]
    held, = read(joined["unresolved"]["path"])
    assert held["path"].endswith("/FixedNativeCoverageCheckpoint.java") and held["method"] == "capture"
    template = read(next(EVIDENCE.glob("PG40660-*/begin.json")))
    commands = template["commands"]
    assert all(digest_file(ref["path"]) == ref["sha256"] for ref in template["toolAndRulePins"])
    java = Path(commands["format"][0])
    java_home = java.parent.parent
    jspecify = java_home.parent / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
    assert jspecify.is_file()
    OUT.mkdir()
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-f03-outbox-values-") as temporary:
        work = Path(temporary)
        source_dir = work / "source" / PACKAGE
        source_dir.mkdir(parents=True)
        sources = []
        inputs = {}
        for name in (*NAMES, "package-info"):
            filename = f"{name}.java"
            path = DIRECTORY / filename
            body = git("show", f"{core}:{path}")
            assert body == git("show", f"{group['source']}:{path}") == path.read_bytes()
            snapshot = source_dir / filename
            snapshot.write_bytes(body)
            sources.append(snapshot)
            inputs[str(path)] = digest_file(snapshot)
        assert all(b"SuppressWarnings" not in source.read_bytes() for source in sources)
        source_list = work / "sources.txt"
        source_list.write_text("".join(f"{path}\n" for path in sources))
        classes = work / "target/classes"
        classes.mkdir(parents=True)
        pom = work / "pom.xml"
        pom.write_text(
            '<project xmlns="http://maven.apache.org/POM/4.0.0">'
            '<modelVersion>4.0.0</modelVersion><groupId>dev.codex.schubert.pt</groupId>'
            '<artifactId>outbox-values-static</artifactId><version>1</version></project>\n'
        )
        put("begin.json", dict(groupStart=start["eventId"], source=group["source"], productionCore=core,
                              sourceHashes=inputs, module="schubert-nk-api", productSources=2,
                              java=digest_file(java), javac=digest_file(java.with_name("javac")),
                              jspecify=digest_file(jspecify), previousStaticTemplate=str(
                                  next(EVIDENCE.glob("PG40660-*/begin.json")).relative_to(ROOT))))
        stages = {"compile": execute("compile", [
            java.with_name("javac"), "--release", "25", "-proc:none", "-Xlint:all", "-Werror",
            "-cp", jspecify, "-d", classes, *sources], work, java_home)}
        physical = {str(p.relative_to(classes)): digest_file(p) for p in classes.rglob("*.class")}
        assert set(physical) == {str(PACKAGE / f"{name}.class") for name in (*NAMES, "package-info")}
        report = {
            "checkstyle": [*commands["checkstyle"][:8], OUT / "checkstyle.xml", f"@{source_list}"],
            "format": [*commands["format"][:6], *sources],
            "pmd": [*commands["pmd"][:6], source_list, "--rulesets", ROOT / "tools/quality/static/pmd.xml",
                    "--use-version", "java-25", "--aux-classpath",
                    os.pathsep.join(map(str, (classes, java_home / "lib/jrt-fs.jar", jspecify))),
                    "--no-cache", "--format", "xml", "--report-file", OUT / "pmd.xml"],
            "spotbugs": [*commands["spotbugs"][:7], pom, *commands["spotbugs"][8:]],
        }
        with ThreadPoolExecutor(max_workers=3) as pool:
            pending = {name: pool.submit(execute, name, cmd, work, java_home) for name, cmd in report.items()}
            stages.update({name: future.result() for name, future in pending.items()})
        spotbugs = work / "target/spotbugsXml.xml"
        if spotbugs.is_file():
            (OUT / "spotbugs.xml").write_bytes(spotbugs.read_bytes())
        results = {}
        for name, violations, error_tags in (
            ("checkstyle", ".//error", ()),
            ("pmd", ".//p:violation", (".//p:error", ".//p:configerror", ".//p:suppressedviolation")),
            ("spotbugs", ".//BugInstance", (".//Error", ".//MissingClass")),
        ):
            path = OUT / f"{name}.xml"
            if not path.is_file():
                results[name] = {"reportExists": False}
                continue
            xml = ET.parse(path).getroot()
            results[name] = dict(reportExists=True, sha256=digest_file(path),
                                 findings=len(xml.findall(violations, XML_NS)),
                                 errors=sum(len(xml.findall(tag, XML_NS)) for tag in error_tags))
            if name == "spotbugs":
                observed = {row.get("class") for row in xml.findall(".//ClassStats")}
                results[name]["observedTypes"] = sorted(observed)
                results[name]["expectedTypesSeen"] = {
                    f"{str(PACKAGE).replace('/', '.')}.{key}" for key in NAMES
                }.issubset(observed)
        assert physical == {str(p.relative_to(classes)): digest_file(p) for p in classes.rglob("*.class")}
        okay = all(row["actualExit"] == 0 for row in stages.values()) and all(
            row.get("findings") == row.get("errors") == 0 for row in results.values()
        ) and results["spotbugs"].get("expectedTypesSeen") is True
        put("manifest.json", dict(
            run=RUN, groupStart=start["eventId"], source=group["source"], productionCore=core,
            actualExit=0 if okay else 1, stages=stages, staticResults=results, physical=physical,
            priorScope=dict(raw=281, dispositions=280, remainingHeld=held),
            runtimePt=0, oldPtReplayed=0, coverageAdded=0, heldTypesOpened=0, externalActions=0,
            nullAwayApplied=False, whole451Accepted=False, wholeF03Accepted=False, formalDelta=0,
            terminalAtUTC=datetime.now(timezone.utc).isoformat()))
        print({name: row["actualExit"] for name, row in stages.items()}, results)
        return 0 if okay else 1


if __name__ == "__main__":
    raise SystemExit(main())
