"""Reconcile the exact green run and measure the comparison guard changes."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import xml.etree.ElementTree as ET


H = runpy.run_path(str(Path(__file__).with_name("061_compare_definition_contract.py")))
ROOT, TOOLS, MODULE, PACKAGE, TEST, WORK, EVIDENCE = (H[name] for name in
    ("ROOT", "TOOLS", "MODULE", "PACKAGE", "TEST", "WORK", "EVIDENCE"))
dump, git, pin, utc = (H[name] for name in ("dump", "git", "pin", "utc"))
MAIN = MODULE / "src/main/java" / PACKAGE.replace(".", "/") / "ArtifactComparator.java"
GREEN = "PG41270-p020-comparison-definitions-green-v1"
RED = "PG41268-p020-comparison-definitions-red-v2"
PRIOR = (ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
         / "PG41030-p020-three-json-readers-static-v1")
PRIOR_WORK = WORK / "PG41028-p020-duplicate-json-green-v1"
NS = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def entries(xml, source_lines):
    root = ET.parse(xml).getroot()
    assert not root.findall("p:error", NS) + root.findall("p:configerror", NS)
    return Counter((row.attrib["rule"], row.attrib.get("method", ""),
                    source_lines[int(row.attrib["beginline"]) - 1].strip())
                   for row in root.findall("p:file/p:violation", NS))


def main():
    green = json.loads((EVIDENCE / GREEN / "manifest.json").read_bytes())
    red = json.loads((EVIDENCE / RED / "manifest.json").read_bytes())
    prior = json.loads((PRIOR / "manifest.json").read_bytes())
    assert git("rev-parse", "HEAD").decode().strip() == green["source"]
    assert green["currentTree"] == red["currentTree"]
    assert green["productionSrcTree"] == red["productionSrcTree"]
    assert {key for key, value in green["inputSha256"].items()
            if red["inputSha256"][key] != value} == {str(MAIN)}
    assert set(green["physical"]) == set(red["physical"])
    physical_changes = {key for key, value in green["physical"].items()
                        if red["physical"][key] != value}
    comparator = PACKAGE.replace(".", "/") + "/ArtifactComparator"
    record = comparator + "$ComparisonResult.class"
    assert physical_changes == {comparator + ".class", record}
    work = WORK / GREEN
    assert pin(work / "jacoco.exec") == green["rawExecSha256"]
    assert pin(work / "reports/TEST-junit-jupiter.xml") == green["rawXmlSha256"]
    classes = work / "classes"
    assert {str(file.relative_to(classes)): pin(file) for file in classes.rglob("*.class")} == green["physical"]
    source = work / "snapshot" / MAIN
    test = work / "snapshot" / TEST
    assert pin(source) == green["inputSha256"][str(MAIN)]
    assert pin(test) == green["inputSha256"][str(TEST)]
    product = sorted((classes / PACKAGE.replace(".", "/")).glob("ArtifactComparator*.class"))
    fixtures = [item for item in product if item.stem.startswith("ArtifactComparatorTest")]
    product = [item for item in product if item not in fixtures]
    assert product and fixtures
    out = EVIDENCE / "PG41272-p020-comparison-definitions-independent-v1"
    out.mkdir()
    results = {}

    def execute(step, command, expected=(0,)):
        args = list(map(str, command))
        result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=100, check=False)
        results[step] = dict(argv=args, exitCode=result.returncode,
                             stderrSha256=hashlib.sha256(result.stderr).hexdigest())
        assert result.returncode in expected, step
        return result.stdout

    def previous(name):
        item, = [step for step in prior["steps"] if step["name"] == name]
        return [arg.replace(str(PRIOR_WORK / "snapshot" / MODULE / "target/classes"), str(classes))
                for arg in item["command"]]

    javap = TOOLS / "jdk-25.0.4/bin/javap"
    before_record = execute("recordBefore", [javap, "-p", "-c", "-s", WORK / RED / "classes" / record])
    after_record = execute("recordAfter", [javap, "-p", "-c", "-s", classes / record])
    assert before_record == after_record

    raw = out / "jacoco.xml"
    execute("coverage", [TOOLS / "jdk-25.0.4/bin/java", "-jar",
                         TOOLS / "org.jacoco.cli-0.8.15-nodeps.jar", "report", work / "jacoco.exec",
                         *[arg for path in product for arg in ("--classfiles", path)],
                         "--sourcefiles", (work / "snapshot" / MODULE / "src/main/java"), "--xml", raw])
    root = ET.parse(raw).getroot()
    report, = root.findall(".//sourcefile")
    found = {int(row.attrib["nr"]): row.attrib for row in report.findall("line")}
    lines = source.read_text().splitlines()
    first, = [i for i, value in enumerate(lines, 1) if "// SS355 fixes the versions" in value]
    last, = [i for i, value in enumerate(lines, 1) if 'require(differences.isArray()' in value]
    covered_guards = [row for n, row in found.items() if first < n <= last]
    assert covered_guards and all(int(row["mi"]) == 0 and int(row["mb"]) == 0 for row in covered_guards)
    coverage = {row.attrib["type"]: dict(covered=int(row.attrib["covered"]), missed=int(row.attrib["missed"]))
                for row in root.findall("counter")}

    style = out / "checkstyle.xml"
    style.write_bytes(execute("checkstyle", [*previous("checkstyle")[:7], source, test]))
    style_root = ET.parse(style).getroot()
    assert len(style_root.findall("file")) == 2 and not style_root.findall("file/error")

    pmd_command = previous("pmd-ArtifactComparator")
    pmd_report = out / "pmd.xml"
    pmd_command[pmd_command.index("--dir") + 1] = str(source)
    pmd_command[pmd_command.index("--report-file") + 1] = str(pmd_report)
    execute("pmd", pmd_command, (0, 4))
    pmd = entries(pmd_report, lines)
    prior_pmd = entries(PRIOR / "ArtifactComparator-pmd.xml",
                        git("show", f"{prior['source']}:{MAIN}").decode().splitlines())
    novel = pmd - prior_pmd

    spot_report = out / "spotbugs.xml"
    spot = previous("spotbugs")
    execute("spotbugs", [*spot[:spot.index("-output") + 1], spot_report, *product], (0, 1))
    spot_root = ET.parse(spot_report).getroot()
    assert not spot_root.findall(".//Error") + spot_root.findall(".//MissingClass")
    spot_findings = [row.attrib["type"] for row in spot_root.findall(".//BugInstance")]
    dump(out / "manifest.json", dict(
        run=out.name, source=green["source"], greenManifestSha256=pin(EVIDENCE / GREEN / "manifest.json"),
        redManifestSha256=pin(EVIDENCE / RED / "manifest.json"), priorPmdSha256=pin(PRIOR / "ArtifactComparator-pmd.xml"),
        greenExecSha256=green["rawExecSha256"], takenAtUTC=utc(), scopeCoverage=coverage,
        changedPhysical=sorted(physical_changes), recordExecutableAndAbiUnchanged=True,
        addedGuardLines=covered_guards, comparedPhysical=[str(p.relative_to(classes)) for p in product],
        checkstyleFindings=0, pmdRaw=sum(pmd.values()), pmdNew=[list(site) + [n] for site, n in novel.items()],
        spotbugsFindings=spot_findings, jUnitRerun=0, outputSha256={p.name: pin(p) for p in out.iterdir()},
        steps=results, whole451=False, actualChr=False, formalDelta=0))
    print(json.dumps(dict(coverage=coverage, guards=len(covered_guards), pmd=sum(pmd.values()),
                          pmdNew=sum(novel.values()), spotbugs=spot_findings)))


if __name__ == "__main__":
    main()
