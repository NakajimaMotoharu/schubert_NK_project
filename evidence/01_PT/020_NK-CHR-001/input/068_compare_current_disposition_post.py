"""Qualify the shared comparator disposition from original local evidence only."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
import xml.etree.ElementTree as ET


H = runpy.run_path(str(Path(__file__).with_name("061_compare_definition_contract.py")))
ROOT, WORK, EVIDENCE, MODULE, PACKAGE, TEST = (
    H[k] for k in ("ROOT", "WORK", "EVIDENCE", "MODULE", "PACKAGE", "TEST")
)
TOOLS = H["TOOLS"]
RUN = "PG41338-p020-current-role-quality-v1"
MAIN_NAMES = ("ArtifactComparator", "GateContractValidator")
RAW = "PG41336-p020-current-role-qualified-v1"
NS = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    with path.open("x") as output:
        json.dump(value, output, indent=2, ensure_ascii=False)
        output.write("\n")


def main():
    result_path = EVIDENCE / RAW / "manifest.json"
    result = read(result_path)
    assert result["testExit"] == 0 and result["tests"] == {
        "tests": 77, "failures": 0, "errors": 0, "skipped": 0
    }
    original = WORK / RAW
    classes = original / "classes"
    product_dir = classes / PACKAGE.replace(".", "/")
    original_exec = original / "jacoco.exec"
    xml_path = original / "reports/TEST-junit-jupiter.xml"
    assert digest(original_exec) == result["rawExecSha256"]
    assert digest(xml_path) == result["rawXmlSha256"]
    assert all(digest(classes / rel) == expected for rel, expected in result["physical"].items())
    rows = [item.attrib["name"] for item in ET.parse(xml_path).getroot().findall("testcase")]
    for method in ("rejectsCurrentRunCaseReportedAsNkOnly", "rejectsNkOnlyCaseReportedAsCurrentRun"):
        assert rows.count(method + "()") == 1
    source = original / "snapshot" / MODULE / "src/main/java" / PACKAGE.replace(".", "/")
    production = [source / (name + ".java") for name in MAIN_NAMES]
    test = original / "snapshot" / TEST
    for p in [*production, test]:
        assert digest(p) == result["inputSha256"][str(p.relative_to(original / "snapshot"))]
    precedent_path = EVIDENCE / "PG41272-p020-comparison-definitions-independent-v1/manifest.json"
    precedent = read(precedent_path)
    work = WORK / RUN
    work.mkdir(mode=0o700, exist_ok=True)
    records = {}
    repo = TOOLS / "m2/repository"
    java = TOOLS / "jdk-25.0.4/bin"
    jre = java / "java"
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}

    def execute(key, arguments, expected=frozenset({0})):
        argv = list(map(str, arguments))
        log = work / (key + ".stdout")
        err = work / (key + ".stderr")
        terminal = work / (key + "-terminal.json")
        if terminal.is_file():
            original_step = read(terminal)
            assert original_step["command"] == argv and original_step["actualExit"] in expected
            assert original_step["stdoutSha256"] == digest(log)
            assert original_step["stderrSha256"] == digest(err)
            records[key] = dict(original_step, reusedOriginal=True)
            return log
        run = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, check=False, timeout=120)
        log.write_bytes(run.stdout)
        err.write_bytes(run.stderr)
        records[key] = {
            "command": argv, "actualExit": run.returncode,
            "stdoutSha256": digest(log), "stderrSha256": digest(err),
        }
        write(work / (key + "-terminal.json"), records[key])
        assert run.returncode in expected, key
        return log

    physical = sorted(p for p in product_dir.glob("*.class")
                      if any(p.name == n + ".class" or p.name.startswith(n + "$") for n in MAIN_NAMES))
    assert len(physical) == 4
    crc = runpy.run_path(str(ROOT / "evidence/01_PT/018_NK-OPS-001/input/5593_p01808_original_name_binding.py"))["class_id"]
    decoder = runpy.run_path(str(ROOT / "tools/quality/jacoco_readonly_exec_subset.py"))["decode"]
    targets = [str(p.relative_to(classes)).removesuffix(".class") for p in physical]
    raw_classes = decoder(original_exec.read_bytes(), set(targets) - {x for x in targets if x.endswith("$ValidationResult")})
    for binary, item in raw_classes["classes"].items():
        assert crc((classes / (binary + ".class")).read_bytes()) == int(item["crc64"], 16)

    deps = [repo / "org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"]
    deps += [repo / "org/ow2/asm" / name / "9.10.1" / (name + "-9.10.1.jar")
             for name in ("asm", "asm-commons", "asm-tree")]
    cp = os.pathsep.join(map(str, deps))
    analyzer = work / "analyzer"
    analyzer.mkdir(exist_ok=True)
    execute("strict-reader-compile", [java / "javac", "--release", "25", "-proc:none",
            "-cp", cp, "-d", analyzer, ROOT / "tools/quality/jacoco/UnfilteredCodeMeasurement.java"])
    coverage = execute("raw", [jre, "-cp", str(analyzer) + os.pathsep + cp,
        "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
        "--strict-original-exec", "--line-deficits", original_exec, *physical])
    coverage_rows = coverage.read_text().splitlines()
    helper, = [line for line in coverage_rows if line.startswith("METHOD\t")
               and "\tmatchesCurrentDisposition\t" in line]
    assert all(next(s for s in helper.split("\t") if s.startswith(c + ":")).split(":")[1] == "0"
               for c in ("LINE", "BRANCH", "INSTRUCTION"))
    compare_classes = [line for line in coverage_rows if line.startswith("CLASS\t")
                       and "ArtifactComparator" in line.split("\t")[1]]
    assert len(compare_classes) == 2
    outer, = [line for line in compare_classes if line.split("\t")[1].endswith("/ArtifactComparator")]
    assert all(next(s for s in outer.split("\t") if s.startswith(c + ":")).split(":")[1] == "0"
               for c in ("LINE", "BRANCH", "INSTRUCTION", "METHOD", "CLASS"))

    fmt = TOOLS / "google-java-format-1.36.1-all-deps.jar"
    execute("format", [jre, "-jar", fmt, "--dry-run", "--set-exit-if-changed", *production, test])
    style = execute("checkstyle", [*precedent["steps"]["checkstyle"]["argv"][:7], *production, test])
    assert len(ET.parse(style).getroot().findall("file")) == 3
    assert not ET.parse(style).getroot().findall("file/error")
    prior_work = str(WORK / "PG41270-p020-comparison-definitions-green-v1")
    spot = [arg.replace(prior_work, str(original)) for arg in precedent["steps"]["spotbugs"]["argv"]]
    spot_index = spot.index("-output")
    spot_xml = work / "spotbugs.xml"
    execute("spotbugs", [*spot[:spot_index + 1], spot_xml, *physical], frozenset({0, 1}))
    spot_root = ET.parse(spot_xml).getroot()
    assert not spot_root.findall(".//Error") + spot_root.findall(".//MissingClass")
    spots = Counter(row.attrib["type"] for row in spot_root.findall(".//BugInstance"))
    pmd_counts = {}
    for file in production:
        pmd = [arg.replace(prior_work, str(original)) for arg in precedent["steps"]["pmd"]["argv"]]
        out = work / (file.stem + "-pmd.xml")
        pmd[pmd.index("--dir") + 1] = str(file)
        pmd[pmd.index("--report-file") + 1] = str(out)
        execute("pmd-" + file.stem, pmd, frozenset({0, 4}))
        report = ET.parse(out).getroot()
        assert not report.findall("p:error", NS) + report.findall("p:configerror", NS)
        pmd_counts[file.stem] = Counter(row.get("rule") for row in report.findall("p:file/p:violation", NS))
    public = EVIDENCE / RUN
    public.mkdir()
    write(public / "manifest.json", {
        "run": RUN, "actualExit": 0, "source": result["source"],
        "terminalAtUTC": datetime.now(timezone.utc).isoformat(),
        "originalResult": {"path": str(result_path.relative_to(ROOT)), "sha256": digest(result_path)},
        "originalExecSha256": digest(original_exec), "originalXmlSha256": digest(xml_path),
        "sameCrcPhysicalWithOriginalRecord": len(raw_classes["classes"]),
        "localOriginalSessionCount": len(raw_classes["sessions"]),
        "measuredBranchHelper": helper, "comparatorRawClasses": compare_classes,
        "firstPostWrapperExit": 1,
        "firstPostWrapperCause": "Initial assertion expected 77 selected tests to reach existing ComparisonResult object methods. Original selection and raw result are retained.",
        "gateOtherMethodsWholeCoverageMeasured": False,
        "checkstyleFindings": 0, "spotbugsByRule": spots, "pmdByTypeAndRule": pmd_counts,
        "rootPolicy": {p: digest(ROOT / p) for p in ("tools/quality/static/pmd.xml", "tools/quality/static/checkstyle.xml")},
        "commands": records, "productPtRuns": 0, "toolTestReruns": 0,
        "actualChr": False, "whole451": False, "formalDelta": 0,
    })
    print("Qualified comparator coverage, helper, and static scope.")


if __name__ == "__main__":
    main()
