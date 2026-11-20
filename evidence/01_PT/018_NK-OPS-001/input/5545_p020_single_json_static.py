"""Run the existing static rules on the changed reader and its synthetic fixture."""
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
    green_path = next(evidence.glob("PG40998*/manifest.json"))
    green = json.loads(green_path.read_bytes())
    phase = next(Path("documents/400_PGPT/470_PMO").glob("601_*/1455_*.json"))
    group = json.loads(phase.read_bytes())
    assert green["testExit"] == 0 and green["testCounts"] == dict(tests=211, failures=0, errors=0, skipped=0)
    before = json.loads(Path(group["values"]["oracleReferences"][2]["path"]).read_bytes())
    assert pin(Path(group["values"]["oracleReferences"][2]["path"])) == group["values"]["oracleReferences"][2]
    source = green["source"]
    qualified = green_path.parent.name
    work = Path("../pgpt-runs/PG379").resolve() / qualified
    snapshot = work / "snapshot"
    module = snapshot / "program/characterization"
    package = Path("dev/codex/schubert/characterization")
    target = module / "src/main/java" / package / "GateContractValidator.java"
    fixture = module / "tests/java" / package / "GateSyntheticRunPortTest.java"
    classes = module / "target/classes"
    for file in (target, fixture):
        relative = file.relative_to(snapshot)
        assert pin(file)["sha256"] == green["inputSha256"][str(relative)]
        assert file.read_bytes() == subprocess.check_output(["git", "show", f"{source}:{relative}"])
    analyzable = [classes / package / name for name in (
        "GateContractValidator.class", "GateContractValidator$ValidationResult.class")]
    assert all(pin(path)["sha256"] == green["physical"][str(path.relative_to(classes))]
               for path in analyzable)
    sdk = [Path(item["path"]) for name, item in before["tools"].items() if "jackson" in name]
    assert len(sdk) == 3
    for artifact in sdk:
        assert pin(artifact) == before["tools"][artifact.name]

    toolchain = Path("../toolchain").resolve()
    java = toolchain / "jdk-25.0.4/bin/java"
    prior = json.loads(next(evidence.glob("PG40880*/manifest.json")).read_bytes())
    sbc = prior["steps"]["spotbugs"]["command"][3]
    pc = prior["steps"]["pmd"]["command"][2]
    aux = ":".join(map(str, (classes, *sdk)))
    out = evidence / "PG41000-p020-single-json-reader-static-v1"
    out.mkdir()
    spotbugs, pmd, style = [out / (name + ".xml") for name in ("spotbugs", "pmd", "checkstyle")]
    steps = []

    def run(name, argv, allowed=(0,)):
        command = list(map(str, argv))
        started = datetime.now(timezone.utc).isoformat()
        process = subprocess.run(command, capture_output=True, check=False, timeout=90)
        steps.append(dict(name=name, command=command, exitCode=process.returncode, startedAtUTC=started,
                          terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                          stdoutSha256=sha256(process.stdout).hexdigest(), stderrSha256=sha256(process.stderr).hexdigest()))
        assert process.returncode in allowed
        return process.stdout

    style.write_bytes(run("checkstyle", [java, "-jar", toolchain / "static-gates-20261015/checkstyle-14.3.0-all.jar",
                                        "-c", "tools/quality/static/checkstyle.xml", "-f", "xml", target, fixture]))
    run("spotbugs", [java, "-Xmx1g", "-cp", sbc, "edu.umd.cs.findbugs.FindBugs2",
                     "-effort:max", "-low", "-xml:withMessages", "-exitcode",
                     "-auxclasspath", aux, "-output", spotbugs, *analyzable], allowed=(0, 1))
    run("pmd", [java, "-cp", pc, "net.sourceforge.pmd.cli.PmdCli", "check", "--dir", target,
                "--rulesets", "tools/quality/static/pmd.xml", "--use-version", "java-25",
                "--aux-classpath", f"{aux}:{java.parents[1]}/lib/jrt-fs.jar", "--no-cache",
                "--format", "xml", "--report-file", pmd], allowed=(0, 4))
    sx, px, cx = [ET.parse(path).getroot() for path in (spotbugs, pmd, style)]
    s_rows = [row.attrib["class"] for row in sx.findall(".//ClassStats")]
    assert set(s_rows) == {"dev.codex.schubert.characterization." + path.stem for path in analyzable}
    s_findings = len(sx.findall(".//BugInstance"))
    s_errors = len(sx.findall(".//MissingClass")) + len(sx.findall(".//Error"))
    ns = {"p": "http://pmd.sourceforge.net/report/2.0.0"}
    lines = target.read_text().splitlines()
    warnings = [dict(rule=row.attrib["rule"], line=int(row.attrib["beginline"]),
                     sourceLine=lines[int(row.attrib["beginline"]) - 1].strip())
                for row in px.findall("p:file/p:violation", ns)]
    errors = len(px.findall("p:error", ns))
    style_count = len(cx.findall("file/error"))
    passed = not any((s_findings, s_errors, errors, style_count))
    summary = dict(input=pin(green_path), source=source, actualExit=0 if passed else 1,
                   terminalAtUTC=datetime.now(timezone.utc).isoformat(), steps=steps,
                   measuredPhysical=[pin(p) for p in analyzable], approvedJackson=[pin(p) for p in sdk],
                   spotBugsFindings=s_findings, spotBugsErrors=s_errors, pmdFindings=warnings, pmdErrors=errors,
                   checkstyleFindings=style_count, reports=[pin(p) for p in (spotbugs, pmd, style)],
                   productTestsRerun=0, productTypesRead=0, realChr=False)
    (out / "manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(passed, s_findings, s_errors, style_count, errors, warnings)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
