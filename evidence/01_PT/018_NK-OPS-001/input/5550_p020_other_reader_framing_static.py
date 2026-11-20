"""Run the existing static rules on the two remaining changed readers and their synthetic fixtures."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def main():
    evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
    green_path = next(evidence.glob("PG41010*/manifest.json"))
    green = json.loads(green_path.read_bytes())
    phase = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1464_*.json"))
    group = json.loads(phase.read_bytes())
    assert green["testExit"] == 0 and green["testCounts"] == dict(tests=213, failures=0, errors=0, skipped=0)
    before = json.loads(Path(group["values"]["oracleReferences"][3]["path"]).read_bytes())
    assert pin(Path(group["values"]["oracleReferences"][3]["path"])) == group["values"]["oracleReferences"][3]
    source = green["source"]
    qualified = green_path.parent.name
    work = Path("../pgpt-runs/PG379").resolve() / qualified
    snapshot = work / "snapshot"
    module = snapshot / "program/characterization"
    package = Path("dev/codex/schubert/characterization")
    names = ("ArtifactComparator", "GateCli")
    targets = [module / "src/main/java" / package / (name + ".java") for name in names]
    fixtures = [module / "tests/java" / package / (name + "Test.java") for name in names]
    classes = module / "target/classes"
    for file in (*targets, *fixtures):
        relative = file.relative_to(snapshot)
        assert pin(file)["sha256"] == green["inputSha256"][str(relative)]
        assert file.read_bytes() == subprocess.check_output(["git", "show", f"{source}:{relative}"])
    class_names = {Path(name) for name in green["physical"] if
                   Path(name).stem.split("$", 1)[0] in names}
    analyzable = [classes / name for name in sorted(class_names)]
    assert len(analyzable) == 8
    assert all(pin(path)["sha256"] == green["physical"][str(path.relative_to(classes))]
               for path in analyzable)
    sdk = [Path(item["path"]) for name, item in before["tools"].items() if "jackson" in name]
    assert len(sdk) == 3
    for artifact in sdk:
        assert pin(artifact) == before["tools"][artifact.name]

    annotations = Path(before["tools"]["jspecify-1.0.1.jar"]["path"])
    assert pin(annotations) == before["tools"][annotations.name]

    toolchain = Path("../toolchain").resolve()
    java = toolchain / "jdk-25.0.4/bin/java"
    prior = json.loads(next(evidence.glob("PG40880*/manifest.json")).read_bytes())
    sbc = prior["steps"]["spotbugs"]["command"][3]
    pc = prior["steps"]["pmd"]["command"][2]
    aux = ":".join(map(str, (classes, *sdk, annotations)))
    previous_report = evidence / "PG41012-p020-two-json-readers-static-v1"
    assert set(e.text for e in ET.parse(previous_report / "spotbugs.xml").findall(".//MissingClass")) == {
        "org.jspecify.annotations.NullMarked", "org.jspecify.annotations.Nullable"}
    out = evidence / "PG41012-p020-two-json-readers-static-v2"
    out.mkdir()
    spotbugs, style = [out / (name + ".xml") for name in ("spotbugs", "checkstyle")]
    pmd_reports = [out / (name + "-pmd.xml") for name in names]
    steps = []

    def run(name, argv, allowed=(0,)):
        command = list(map(str, argv))
        started = datetime.now(timezone.utc).isoformat()
        process = subprocess.run(command, capture_output=True, check=False, timeout=90)
        terminal = dict(name=name, command=command, exitCode=process.returncode, startedAtUTC=started,
                        terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                        stdoutSha256=sha256(process.stdout).hexdigest(), stderrSha256=sha256(process.stderr).hexdigest())
        steps.append(terminal)
        (out / (name + "-terminal.json")).write_text(json.dumps(terminal, indent=2) + "\n")
        assert process.returncode in allowed
        return process.stdout

    prior_style = previous_report / "checkstyle.xml"
    prior_names = {item.attrib["name"] for item in ET.parse(prior_style).findall("file")}
    assert prior_names == set(map(str, (*targets, *fixtures)))
    style.write_bytes(prior_style.read_bytes())
    run("spotbugs", [java, "-Xmx1g", "-cp", sbc, "edu.umd.cs.findbugs.FindBugs2",
                     "-effort:max", "-low", "-xml:withMessages", "-exitcode",
                     "-auxclasspath", aux, "-output", spotbugs, *analyzable], allowed=(0, 1))
    warnings = []
    errors = 0
    ns = {"p": "http://pmd.sourceforge.net/report/2.0.0"}
    for target, pmd in zip(targets, pmd_reports, strict=True):
        run("pmd-" + target.stem, [java, "-cp", pc, "net.sourceforge.pmd.cli.PmdCli", "check",
            "--dir", target, "--rulesets", "tools/quality/static/pmd.xml", "--use-version", "java-25",
            "--aux-classpath", f"{aux}:{java.parents[1]}/lib/jrt-fs.jar", "--no-cache",
            "--format", "xml", "--report-file", pmd], allowed=(0, 4))
        px = ET.parse(pmd).getroot()
        lines = target.read_text().splitlines()
        warnings.extend(dict(file=target.name, rule=row.attrib["rule"], line=int(row.attrib["beginline"]),
                             sourceLine=lines[int(row.attrib["beginline"]) - 1].strip())
                        for row in px.findall("p:file/p:violation", ns))
        errors += len(px.findall("p:error", ns))
    sx, cx = (ET.parse(path).getroot() for path in (spotbugs, style))
    s_rows = [row.attrib["class"] for row in sx.findall(".//ClassStats")]
    assert set(s_rows) == {"dev.codex.schubert.characterization." + path.stem for path in analyzable}
    s_findings = len(sx.findall(".//BugInstance"))
    s_errors = len(sx.findall(".//MissingClass")) + len(sx.findall(".//Error"))
    style_count = len(cx.findall("file/error"))
    passed = not any((s_findings, s_errors, errors, style_count))
    summary = dict(input=pin(green_path), source=source, actualExit=0 if passed else 1,
                   terminalAtUTC=datetime.now(timezone.utc).isoformat(), steps=steps,
                   measuredPhysical=[pin(p) for p in analyzable], approvedJackson=[pin(p) for p in sdk], annotatedAuxInput=pin(annotations),
                   originalCheckstyle=pin(prior_style), originalFailure=pin(previous_report/"spotbugs.xml"),
                   spotBugsFindings=s_findings, spotBugsErrors=s_errors, pmdFindings=warnings, pmdErrors=errors,
                   checkstyleFindings=style_count, reports=[pin(p) for p in (spotbugs, *pmd_reports, style)],
                   productTestsRerun=0, productTypesRead=0, realChr=False)
    (out / "manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(passed, s_findings, s_errors, style_count, errors, warnings)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
