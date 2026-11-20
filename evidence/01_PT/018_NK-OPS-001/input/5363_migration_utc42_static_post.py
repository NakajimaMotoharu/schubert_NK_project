"""Check SSC-473 with the inherited compiler and current PMD and Checkstyle rules."""

from collections import Counter
from html import escape
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile


U = runpy.run_path(str(Path(__file__).with_name("5362_migration_utc42_current_unit.py")))
H, OPS, JAVA, SOURCE, RUN = (U[k] for k in ("H", "OPS", "JAVA", "SOURCE", "RUN"))
REPO = Path.cwd()
BASE = "cb1411d94a1d97aedafe1af60400aaec0ae8c8e8"
FIX = "PG40454-migration-utc42-static-independent-v1"


def dependency(group, artifact, version, path=None):
    scope = f"<scope>system</scope><systemPath>{escape(str(path))}</systemPath>" if path else ""
    return (f"<dependency><groupId>{group}</groupId><artifactId>{artifact}</artifactId>"
            f"<version>{version}</version>{scope}</dependency>")


def make_pom(directory, archive):
    file = directory / "pom.xml"
    deps = [
        dependency("org.jspecify", "jspecify", "1.0.1"),
        dependency("com.google.code.findbugs", "jsr305", "3.0.2"),
        dependency("dev.codex.schubert.pgpt", "verified-closure", "1", archive),
    ]
    file.write_text(f"""<project xmlns="http://maven.apache.org/POM/4.0.0">
<modelVersion>4.0.0</modelVersion>
<parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId>
<version>0.1.0-SNAPSHOT</version><relativePath>{escape(str(REPO / 'pom.xml'))}</relativePath></parent>
<artifactId>ssc473-static-check</artifactId>
<dependencies>{''.join(deps)}</dependencies>
</project>
""")
    return file


def findings(path):
    xml = ElementTree.parse(path).getroot()
    assert xml.tag.endswith("pmd")
    processing = [node.attrib for node in xml if node.tag.endswith(("error", "configerror"))]
    result = {}
    for file in xml:
        if file.tag.endswith("file"):
            name = Path(file.get("name")).name
            result[name] = Counter((v.get("rule"), v.get("method", ""), (v.text or "").strip())
                                   for v in file if v.tag.endswith("violation"))
    return result, processing


def main():
    pin, git, execute = (H[k] for k in ("pin", "git", "execute"))
    read = U["read"]
    out = OPS / FIX
    out.mkdir()
    run_manifest = OPS / RUN / "manifest.json"
    run = read(run_manifest)
    assert run["actualExit"] == 0 and run["source"] == SOURCE and run["outcome"] == {"pass": 87}
    live = Path(run["previousCurrentJar"]["path"])
    assert pin(live) == run["previousCurrentJar"]
    assert not git("diff", "--name-only", SOURCE, "HEAD", "--", "src")
    assert git("show", f"{SOURCE}:pom.xml") == (REPO / "pom.xml").read_bytes()
    old_dir = next(OPS.glob("PG33676-*"))
    old = read(old_dir / "manifest.json")
    cfg = REPO / "tools/quality/static"
    assert pin(cfg / "pmd.xml")["sha256"] == old["fullRootRulesetSha256"]
    imported = set(run["exactCurrentPhysical"]) - set(run["affectedClasses"])
    imported.remove(U["SCOPE"] + "MigrationMasterContentVerifier$SqlQuery.class")
    contents = {k: v for k, v in run["exactCurrentPhysical"].items() if k in imported}
    assert len(contents) == 79
    statuses = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-ssc473-static-") as name:
        root = Path(name)
        archive = root / "qualified-closure.jar"
        with ZipFile(live) as source, ZipFile(archive, "x") as target:
            for item, sha in sorted(contents.items()):
                body = source.read(item)
                assert H["sha"](body) == sha
                target.writestr(item, body)
        mains, main_pins = U["source_files"]("main", U["MAIN"], root)
        tests, test_pins = U["source_files"]("test", U["TESTS"], root)
        assert {**main_pins, **test_pins} == run["inputPins"]
        # The isolated Maven child sees only the two changed Main sources.
        for path in mains:
            destination = root / "src/main/java" / U["SCOPE"] / path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
        pom = make_pom(root, archive)
        old_spotbugs = old["stages"]["spotbugs"]["command"]
        env = ["/usr/bin/env", f"JAVA_HOME={JAVA.parents[1]}"]
        mvn = [*env, *old_spotbugs[:-1], "-f", pom]
        commands = {
            "nullaway": [*mvn, "compiler:compile@default-compile"],
            "spotbugs": [*mvn, old_spotbugs[-1]],
        }
        for stage, cmd in commands.items():
            statuses[stage], _ = execute(out, stage, cmd, root)
            if stage == "nullaway" and statuses[stage]["actualExit"] != 0:
                break
        if (root / "target/spotbugsXml.xml").is_file():
            (out / "spotbugs.xml").write_bytes((root / "target/spotbugsXml.xml").read_bytes())
        cs = old["stages"]["checkstyle"]["command"]
        statuses["checkstyle"], _ = execute(out, "checkstyle",
            [*cs[:3], "-c", cfg / "checkstyle.xml", "-f", "xml", "-o",
             (out / "checkstyle.xml").resolve(), *mains, *tests], root)
        pmd = old["stages"]["pmd"]["command"]
        java_sources = root / "sources.txt"
        java_sources.write_text("\n".join(map(str, mains)) + "\n")
        model = [p for p in run["tools"] if "jspecify" in p or "jsr305" in p]
        statuses["pmd"], _ = execute(out, "pmd",
            [*pmd[:pmd.index("check")+1], "--file-list", java_sources,
             "--rulesets", cfg / "pmd.xml", "--use-version", "java-25",
             "--aux-classpath", ":".join(map(str, [JAVA.parents[1] / "lib/jrt-fs.jar", archive, *model])),
             "--no-cache", "--format", "xml", "--report-file", (out / "pmd.xml").resolve()], root)

    pmd_findings, processing = findings(out / "pmd.xml")
    old_findings, old_processing = findings(old_dir / "pmd.xml")
    names = [name + ".java" for name in U["MAIN"]]
    previous_time = {name: sum(n for row,n in old_findings.get(name, {}).items() if row[0]=="ReplaceJavaUtilDate")
                     for name in names}
    current_time = {name: sum(n for row,n in pmd_findings.get(name, {}).items() if row[0]=="ReplaceJavaUtilDate")
                    for name in names}
    exact_source_scan = git("grep", "-l", "-E", r"\.(getTimestamp|setTimestamp)\(", BASE,
                            "--", "src/**/src/main/**/*.java").decode().splitlines()
    from subprocess import run as command
    new_source_scan = command(["git", "grep", "-q", "-E", r"\.(getTimestamp|setTimestamp)\(", SOURCE,
                               "--", "src/**/src/main/**/*.java"], check=False).returncode
    assert len(exact_source_scan) == 2 and new_source_scan == 1
    cs_xml = ElementTree.parse(out / "checkstyle.xml").getroot()
    checks = list(cs_xml.iter("error"))
    sb = ElementTree.parse(out / "spotbugs.xml").getroot() if (out / "spotbugs.xml").is_file() else None
    bugs = len(list(sb.iter("BugInstance"))) if sb is not None else None
    sb_errors = len(list(sb.iter("Error"))) if sb is not None else None
    raw = (OPS / RUN / "raw.stdout.txt").read_text()
    totals = {}
    for row in raw.splitlines():
        cells = row.split("\t")
        if cells[0] == "CLASS":
            assert cells[3] == "true"
            totals[cells[1].split("/")[-1]] = {counter.split(":")[0]: [int(i) for i in counter.split(":")[1:]]
                                              for counter in cells[6:]}
    assert set(totals) == set(U["MAIN"]) and all(missed == 0 for counters in totals.values()
                                               for missed, _ in counters.values())
    result = dict(actualExit=0, source=SOURCE, productionCore=SOURCE, baselineCore=BASE,
                  admissionEvidence=pin(run_manifest), script=pin(Path(__file__).relative_to(REPO)),
                  rootCompilerPom=pin(REPO / "pom.xml"), staticReceipts=statuses,
                  checkstyleFindings=len(checks), spotbugsFindings=bugs, spotbugsErrors=sb_errors,
                  pmdOldTimestampRule=previous_time, pmdCurrentTimestampRule=current_time,
                  pmdCurrentRuleDetails={name: [[*entry, n] for entry, n in details.items()]
                                         for name,details in pmd_findings.items()},
                  pmdProcessingErrors=processing, oldPmdProcessingErrors=len(old_processing),
                  retainedLegacyCallSitesBefore=exact_source_scan, legacyCallsInCurrentProduction=0,
                  touchedPhysicalUnfiltered=totals, reproducedUnitTestsHere=0, wholeF03Accepted=False,
                  whole451Accepted=False, terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"), {k: v["actualExit"] for k,v in statuses.items()},
          "style", len(checks), "spotbugs", bugs, "PMD", previous_time, current_time)


if __name__ == "__main__":
    main()
