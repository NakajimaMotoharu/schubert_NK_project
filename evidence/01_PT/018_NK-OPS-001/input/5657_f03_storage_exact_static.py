"""Bind the previously measured Storage classes and analyze only the pinned source delta."""

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as XML
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5391_f03_storage_current_two_junit.py")))
ROOT, TOOLS, JAVA, REPO, OPS, PLAN = (H[key] for key in ("ROOT", "TOOLS", "JAVA", "REPO", "OPS", "PLAN"))
pin, checked, read, write, run = (H[key] for key in ("pin", "checked", "read", "write", "run"))
MODULE = Path("src/schubert-nk-storage")
TARGETS = {"ServiceCredentialId.java", "ServiceCredentialLocation.java", "StorageIoException.java"}
NS = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=20)


def main():
    start = read(next(PLAN.glob("1704_*.json")))["values"]
    _, prior, current, test, xml_return = map(checked, start["oracleReferences"])
    assert git("rev-parse", "HEAD").decode().strip() == start["source"]
    past = read(prior)
    old = read(checked(past["compile"]))
    assert past["actualExit"] == 0 and past["mainCount"] == 25 and past["physicalClassStats"] == 80
    assert past["spotbugs"] == dict(bugs=0, missingClasses=0, errors=0, all80ClassStats=True)
    assert past["pmdRaw"] == past["pmdClassified"] == 18
    assert past["pmdApplicable"] == past["pmdUnclassified"] == 0
    assert old["qa056HeldClassfilesAbsent"] and old["noTestSources"] and old["productClassesInitialized"] == 0
    package = read(current)
    artifact = checked(package["packagedBuild"]["storage"]["artifact"])
    assert package["actualExit"] == 0 and package["recoveredCompileTerminal"]["compile"]["buildSuccessMessage"]
    assert not git("diff", "--name-only", package["source"], start["productionCoreMain"], "--",
                   str(MODULE / "src/main"), str(MODULE / "pom.xml"), "pom.xml")
    start_source = start["productionCoreMain"]
    sources = git("ls-tree", "-rz", "--name-only", start_source, "--", str(MODULE / "src/main/java")).decode().split("\0")[:-1]
    assert all(Path(path).suffix == ".java" for path in sources) and len(sources) == 25
    inputs = {p: hashlib.sha256(git("show", f"{start_source}:{p}")).hexdigest() for p in sources}
    changed = [p for p, digest in inputs.items() if old["inputHashes"][p] != digest]
    assert {Path(path).name for path in changed} == TARGETS and len(changed) == 3
    assert old["inputHashes"]["pom.xml"] == pin(Path("pom.xml"))["sha256"]
    assert old["inputHashes"][str(MODULE / "pom.xml")] == pin(MODULE / "pom.xml")["sha256"]
    with ZipFile(artifact) as jar:
        listing = [n for n in jar.namelist() if n.endswith(".class")]
        assert len(listing) == 79 and len(set(listing)) == len(listing)
        raw = {n: jar.read(n) for n in listing}
    exact = {n: hashlib.sha256(body).hexdigest() for n, body in raw.items()}
    old_binary = old["physicalClassHashes"]
    lost = set(old_binary) - set(exact)
    assert lost == {"dev/codex/schubert/nk/storage/ServiceCredentialId$1.class"}
    changed_binary = {n for n in exact if exact[n] != old_binary[n]}
    assert len(changed_binary) == 5 and len(exact) - len(changed_binary) == 74
    old_id = next(path for path in changed if Path(path).name == "ServiceCredentialId.java")
    assert b"return switch" in git("show", f"{old['sourceCore']}:{old_id}")
    text = git("show", f"{start_source}:{old_id}")
    assert b"BY_SERVICE.get(service)" in text and b"return switch" not in text
    current_static = read(test)
    assert current_static["core"] in (start_source, read(next(PLAN.glob("1696_*.json")))["productionCoreMain"])
    assert read(xml_return)["actualExit"] == 0
    original_static = read(checked(past["static"]))
    assert original_static["fullRulesetSha256"] == pin(ROOT / "tools/quality/static/pmd.xml")["sha256"]
    prep = read(next(OPS.glob("PG41264-*/manifest.json")))["stages"]
    out = OPS / start["run"]
    out.mkdir()
    output = out.resolve()
    stages = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-storage-static-closure-") as work:
        room = Path(work)
        physical = room / "classes"
        for name, data in raw.items():
            path = physical / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        source_files = []
        for name in changed:
            code = room / Path(name).name
            code.write_bytes(git("show", f"{start_source}:{name}"))
            assert pin(code)["sha256"] == inputs[name]
            source_files.append(code)
        jspecify = REPO / "org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
        cp = os.pathsep.join(map(str, (physical, jspecify)))
        style = run([JAVA, "-jar", TOOLS / "static-gates-20261015/checkstyle-14.3.0-all.jar",
                     "-c", ROOT / "tools/quality/static/checkstyle.xml", "-f", "xml", *source_files],
                    ROOT, out, "checkstyle")
        stages["style"] = style
        checkstyle = XML.parse(style["stdout"]["path"]).getroot()
        assert style["actualExit"] == 0 and len(checkstyle.findall("file")) == 3
        assert not checkstyle.findall(".//error")
        d = prep["spotbugs"]["command"][:13]
        d[10] = cp
        d[12] = str(output / "spotbugs.xml")
        stages["spotbugs"] = run([*d, *[physical / n for n in sorted(changed_binary)]], ROOT, out, "spotbugs")
        paths = room / "pmd-source-list.txt"
        paths.write_text("\n".join(map(str, source_files)) + "\n")
        d = prep["pmd"]["command"][:6]
        stages["pmd"] = run([*d, paths, "--rulesets", ROOT / "tools/quality/static/pmd.xml",
                             "--use-version", "java-25", "--aux-classpath", f"{JAVA.parents[1]}/lib/jrt-fs.jar:{cp}",
                             "--no-cache", "--format", "xml", "--report-file", output / "pmd.xml"],
                            ROOT, out, "pmd")
    spot = XML.parse(output / "spotbugs.xml").getroot()
    defects = {k: len(spot.findall(".//" + tag)) for k, tag in
               (("bug", "BugInstance"), ("missing", "MissingClass"), ("error", "Error"))}
    assert stages["spotbugs"]["actualExit"] in (0, 1)
    pmd = XML.parse(output / "pmd.xml").getroot()
    assert stages["pmd"]["actualExit"] in (0, 4)
    assert not pmd.findall("p:error", NS) + pmd.findall("p:configerror", NS) + pmd.findall("p:suppressedviolation", NS)
    raw_findings = [dict(rule=item.attrib["rule"], source=Path(file.attrib["name"]).name, line=item.attrib["beginline"])
                    for file in pmd.findall("p:file", NS) for item in file.findall("p:violation", NS)]
    result = dict(actualExit=int(bool(defects["bug"] or defects["missing"] or defects["error"] or raw_findings)),
        run=out.name, source=start["source"], core=start_source, inputCore=package["source"], currentMain=25,
        immutableMain=22, currentPhysical=79, sameClassBytes=74, changedClassBytes=sorted(changed_binary),
        retiredGenerated=sorted(lost), staticCheckstyle=0, spotbugs=defects, rawPmd=raw_findings,
        fullPriorRawPmd=18, oldPmdAndSpotbugs=pin(prior), oldInputCompiled=pin(checked(past["compile"])),
        currentJar=pin(artifact), currentMainSha=inputs, priorPmdRulesVerified=True,
        noTestsRerun=True, nativeServiceOperations=0, noHeldClassesOpened=True,
        formalDelta=0, whole451=False, wholeF03=False, stages=stages,
        terminalAtUTC=datetime.now(timezone.utc).isoformat())
    write(out / "manifest.json", result)
    print(len(exact), len(changed), defects, raw_findings)


if __name__ == "__main__":
    main()
