"""Run the two reviewed JDBC port fixtures against normal, current compiled product classes."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from xml.etree import ElementTree as ET

import pg9666_pagination_static as receipt
from pgpt_closed_host_stages import classify_source_findings, findings
from pgpt_public_unit_xml import copy_public_evidence

ROOT = Path.cwd()
B = Path("evidence/01_PT/018_NK-OPS-001")
E = B / "evidence"
BUILD = E / "PG39462-admission-single-cleanup-four-build-v2/compile/manifest.json"
PRIOR = E / "PG39434-service-jdbc-four-module-build-v1/compile/manifest.json"
OUT = E / "PG39463-ssc468-admission-ports-static-v2"
PUBLIC = E / "PG39464-ssc468-admission-ports-unit-v1"
RUNS = ROOT.parent / "pgpt-runs/PG379"
UNIT = RUNS / PUBLIC.name.lower()
TC = ROOT.parent / "toolchain"
JAVA = TC / "jdk-25.0.4/bin/java"
MAVEN = TC / "m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
JSPECIFY = TC / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
JUNIT = TC / "junit-platform-console-standalone-1.13.4.jar"
AGENT = TC / "m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
CLI = TC / "org.jacoco.cli-0.8.15-nodeps.jar"
PKG = "dev/codex/schubert/nk/api/bootstrap"
MODULE = "src/schubert-nk-bootstrap"
NAMES = ("ServiceDatabaseAdmission", "ServiceDatabaseSource")
MAIN = [f"{MODULE}/src/main/java/{PKG}/{n}.java" for n in (*NAMES, "JdbcAdmissionFailures", "JdbcFailureGraph")]
TESTS = [f"{MODULE}/src/test/java/{PKG}/{n}PortTest.java" for n in NAMES]
SCOPE = "PG39464-SSC468-SERVICE-JDBC-PORT31"
ADMISSION = B / "input/5158_ssc468_admission_source_applicability.json"
STATIC_REFERENCE = E / "PG39436-service-jdbc-ports-static-v1/manifest.json"
TOOL_RUNTIME = E / "provisional/PG13218-spotbugs-fresh-aux-plan-recovery-v1/manifest.json"
TOOL_RUNTIME_SHA = "a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564"
DESIGN = "0c1ed4c1d3cf12af6fcb715d9b8ce4d43db5c13c"
HOLDS = {
    "dev/codex/schubert/nk/storage/ServiceConfigFiles",
    "dev/codex/schubert/nk/storage/ServiceConfigFiles$NioIo",
    "dev/codex/schubert/nk/storage/LinuxDirectoryCalls",
    "dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseAdmissionTest",
    "dev/codex/schubert/nk/api/bootstrap/ServiceDatabaseSourceTest",
    "org/postgresql/Driver",
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(path.read_bytes())


def write(path, data):
    with path.open("x") as at:
        at.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=digest(path))


def git_source(source, p):
    return sha256(subprocess.check_output(["git", "show", f"{source}:{p}"], timeout=15)).hexdigest()


def boards(build):
    return {n:Path(build["cwd"]) / f"src/schubert-nk-{n}/target/classes" for n in ("storage", "bootstrap")}


def checked_build(build):
    assert build["actualExit"] == 0 and build["inputHashesReverified"] and not build["productTestsExecuted"]
    physical = {}
    for module, expected in build["physicalClassHashes"].items():
        directory = Path(build["cwd"]) / f"src/schubert-nk-{module}/target/classes"
        physical[module] = {str(p.relative_to(directory)): digest(p) for p in directory.rglob("*.class")}
        assert physical[module] == expected
    old = load(PRIOR)
    assert build["deltas"]["bootstrap"]["removed"] == [PKG + "/ServiceDatabaseAdmission$1.class"]
    assert all(not build["deltas"][name]["added"] for name in build["deltas"])
    assert all(old["physicalClassHashes"][m] == physical[m] for m in ("protocol", "storage", "batch"))
    assert {p for p, h in physical["bootstrap"].items() if old["physicalClassHashes"]["bootstrap"].get(p) != h} <= {
        f"{PKG}/{n}.class" for n in (*NAMES, *(n + "$1" for n in NAMES))
    }
    sha = {p:digest(Path(p)) for p in MAIN+TESTS}
    assert all(h == git_source(build["sourceCore"], p) for p,h in sha.items())
    return sha


def pom_components():
    return ",".join("src/schubert-nk-" + n for n in ("protocol","storage","bootstrap","batch"))


def static():
    build = load(BUILD)
    hashes = checked_build(build)
    OUT.mkdir()
    receipt.SLOT = OUT
    paths = [str((ROOT / p).resolve()) for p in MAIN+TESTS]
    listing = (OUT / "sources.txt").resolve()
    listing.write_text("\n".join(paths) + "\n")
    gm = TC / "google-java-format-1.36.1-all-deps.jar"
    tree = boards(build)
    cp = os.pathsep.join(map(str,[*tree.values(), JSPECIFY, JUNIT]))
    sg = TC / "static-gates-20261015"
    jars = [sg / "record-fix-v1/pmd-record-1298.jar", *sorted((sg / "pmd-bin-7.28.0/lib").glob("*.jar"))]
    stages = {}
    stages["format"] = receipt.step("format", [str(JAVA), "-jar", str(gm), "--skip-reflowing-long-strings",
        "--dry-run", "--set-exit-if-changed", *paths], ROOT)
    cs_xml = (OUT / "checkstyle.xml").resolve()
    stages["checkstyle"] = receipt.step("checkstyle", [str(JAVA), "-jar", str(sg / "checkstyle-14.3.0-all.jar"),
        "-c", str(ROOT / "tools/quality/static/checkstyle.xml"), "-f", "xml", "-o", str(cs_xml), "@"+str(listing)], ROOT)
    pmd_xml = (OUT / "pmd.xml").resolve()
    stages["pmd"] = receipt.step("pmd", [str(JAVA), "-cp", os.pathsep.join(map(str,jars)), "net.sourceforge.pmd.cli.PmdCli",
        "check", "--file-list", str(listing), "--rulesets", str(ROOT / "tools/quality/static/pmd.xml"), "--use-version", "java-25",
        "--aux-classpath", str(TC / "jdk-25.0.4/lib/jrt-fs.jar") + ":" + cp, "--no-cache", "--format", "xml", "--report-file", str(pmd_xml)], ROOT)
    assert digest(TOOL_RUNTIME) == TOOL_RUNTIME_SHA
    runtime = load(TOOL_RUNTIME)
    external = {p:h for p,h in runtime["auxiliaryClasspathHashes"].items() if p not in runtime["currentJarHashes"]}
    all_tools = {**runtime["toolRuntimeHashes"], **external}
    assert all(Path(p).is_relative_to(TC) and digest(Path(p)) == h for p,h in all_tools.items())
    trees = {module:Path(build["cwd"]) / f"src/schubert-nk-{module}/target/classes"
             for module in build["physicalClassHashes"]}
    baseline = load(STATIC_REFERENCE)
    assert baseline["source"] == load(PRIOR)["sourceCore"]
    reports = {}
    for module in ("protocol","storage"):
        prior_row = baseline["reports"][module]
        assert ref(Path(prior_row["xml"]["path"])) == prior_row["xml"]
        assert prior_row["exactScope"] and not any(prior_row[k] for k in ("bugs","errors","missing"))
        assert build["physicalClassHashes"][module] == load(PRIOR)["physicalClassHashes"][module]
        reports[module] = dict(prior_row, identicalUnchangedModuleBytes=True, productAnalyzerRepeated=False)
    aux = (OUT / "fresh-aux.txt").resolve()
    aux.write_text("\n".join(sorted([*external,*map(str,trees.values())])) + "\n")
    for module in ("bootstrap","batch"):
        local = (OUT / (module + "-spotbugs.xml")).resolve()
        cli = [str(JAVA),"-Xmx2g","-cp",os.pathsep.join(runtime["toolClasspath"]),"edu.umd.cs.findbugs.FindBugs2",
            "-effort:max","-low","-xml:withMessages","-exitcode","-auxclasspathFromFile",str(aux),
            "-output",str(local),str(trees[module])]
        label = module+"-spotbugs"
        stages[label] = receipt.step(label,cli,ROOT,timeout=230)
        root=ET.parse(local).getroot()
        reports[module]=dict(xml=ref(OUT/local.name), bugs=len(root.findall(".//BugInstance")),
            missing=len(root.findall(".//MissingClass")),errors=len(root.findall(".//Error")),
            exactScope={x.get("class").replace(".","/") + ".class" for x in root.findall(".//ClassStats")}
                == set(build["physicalClassHashes"][module]), productAnalyzerRepeated=False)
    raw, errors = findings(pmd_xml)
    abi = []
    javap = JAVA.with_name("javap")
    old = boards(load(PRIOR))
    for n in NAMES:
        fqn = PKG.replace("/", ".") + "." + n
        a, b = [subprocess.check_output([str(javap), "-public", "-s", "-cp", str(table["bootstrap"]), fqn], timeout=20)
                for table in (old, tree)]
        same = a == b
        abi.append(dict(type=fqn, unchanged=same, priorDigest=sha256(a).hexdigest(), currentDigest=sha256(b).hexdigest()))
    valid = all(r["actualExit"] == (4 if name=="pmd" and raw else 0) and not r["timedOut"] for name,r in stages.items())
    valid = valid and not errors and not ET.parse(cs_xml).findall(".//error") and all(x["unchanged"] for x in abi)
    valid = valid and all(x["exactScope"] and not any(x[k] for k in ("bugs","missing","errors")) for x in reports.values())
    assert all(digest(Path(p)) == h for p,h in all_tools.items())
    assert subprocess.run(["git","merge-base","--is-ancestor",DESIGN,"origin/main"]).returncode==0
    write(OUT / "manifest.json", dict(canonicalDesign=DESIGN, designPr=435, actualExit=0 if valid else 1, source=build["sourceCore"], terminalAtUTC=utc(),
        compile=ref(BUILD), inputHashes=hashes, stages=stages, pmdRaw=raw, pmdProcessingErrors=errors, abi=abi,
        reports=reports, runtimeReference=ref(TOOL_RUNTIME), toolHashes=all_tools, productTests=0))
    print({k:v["actualExit"] for k,v in stages.items()}, "PMD",len(raw),"reports",list(reports))


def unit():
    build = load(BUILD)
    hashes = checked_build(build)
    static_path = OUT / "manifest.json"
    static_result = load(static_path)
    a = load(ADMISSION)
    assert static_result["actualExit"] == 0 and a["static"] == ref(static_path)
    assert static_result["inputHashes"] == hashes
    manifests = static_result["reports"]
    assert set(manifests)==set(build["physicalClassHashes"])
    assert all(not v[k] for v in manifests.values() for k in ("bugs","missing","errors"))
    assert all(v["exactScope"] and ref(Path(v["xml"]["path"]))==v["xml"] for v in manifests.values())
    classified = classify_source_findings(MAIN+TESTS,a["sourceAnchors"],static_result["pmdRaw"],lambda p:Path(p).read_text())
    assert len(classified)==len(static_result["pmdRaw"])
    tool_receipt = {str(p):digest(p) for p in (JAVA,JUNIT,JSPECIFY,AGENT,CLI)}
    tree = boards(build)
    UNIT.mkdir()
    (UNIT / "classes").mkdir()
    (UNIT / "tmp").mkdir()
    receipt.SLOT = UNIT
    cp = os.pathsep.join(map(str,[*tree.values(), JSPECIFY]))
    stages = {}
    cases = []
    for test in TESTS:
        text=Path(test).read_text()
        methods = re.findall(r"(?m)^  @Test\s+void (\w+)\(",text)
        cases.extend((PKG.replace("/",".")+"."+Path(test).stem,n+"()") for n in methods)
    assert len(cases)==len(set(cases))==31
    stages["test-compile"] = receipt.step("test-compile", [str(JAVA.with_name("javac")), "--release", "25", "-g", "-proc:none",
        "-implicit:none", "-encoding", "UTF-8", "-Xlint:all", "-Werror", "-cp", cp+":"+str(JUNIT),
        "-d", str(UNIT/"classes"),*[str(ROOT / p) for p in TESTS]], UNIT)
    assert stages["test-compile"]["actualExit"] == 0
    command=[str(JAVA),"-Djava.io.tmpdir="+str(UNIT/"tmp"),"-Dfile.encoding=UTF-8","-Duser.timezone=Asia/Tokyo",
        "-Djunit.jupiter.extensions.autodetection.enabled=false","-Djunit.jupiter.execution.parallel.enabled=false",
        "-javaagent:"+str(AGENT)+"=destfile="+str(UNIT/"jacoco.exec")+",sessionid="+SCOPE+",append=false",
        "-Xlog:class+init=info:file="+str(UNIT/"class-init.log"),"-jar",str(JUNIT),
        "execute","--disable-banner","--class-path",str(UNIT/"classes")+":"+cp,
        "--reports-dir",str(UNIT/"xml"),"--fail-if-no-tests","--details","summary"]
    for name in sorted({n for n, _ in cases}):
        command.extend(["--select-class",name])
    write(UNIT/"input.json",dict(build=ref(BUILD),source=build["sourceCore"],inputHashes=hashes,toolHashes=tool_receipt,
        static=ref(static_path),admission=ref(ADMISSION),registeredExpectedCases=cases,run=SCOPE,actualCommand=command))
    stages["unit"]=receipt.step("unit",command,UNIT,timeout=150)
    for key,args in (("execinfo",["execinfo",str(UNIT/"jacoco.exec")]),):
        stages[key]=receipt.step(key,[str(JAVA),"-jar",str(CLI),*args],UNIT)
    actual=[]; failures=0; errors=0; skipped=0
    xmls={}
    for path in sorted((UNIT/"xml").glob("TEST-*.xml")):
        root=ET.parse(path).getroot()
        for row in root.findall("testcase"):
            failures+=len(row.findall("failure"))
            errors+=len(row.findall("error"))
            skipped+=len(row.findall("skipped"))
            actual.append((row.get("classname"),row.get("name")))
        xmls[path.name]=digest(path)
    init = set(re.findall(r"Initializing '([^']+)'",(UNIT/"class-init.log").read_text()))
    protected = HOLDS & init
    assert not any(x.startswith("org/postgresql/") or x.startswith("dev/codex/schubert/nk/storage/Linux") for x in init)
    ok = not protected and not (failures or errors or skipped) and len(actual)==len(cases) and set(actual)==set(cases)
    ok = ok and all(x["actualExit"]==0 and not x["timedOut"] for x in stages.values())
    PUBLIC.mkdir()
    files={}
    for p in [*sorted(UNIT.glob("*.safe.json")),UNIT/"input.json",UNIT/"execinfo.stdout",UNIT/"execinfo.stderr",UNIT/"jacoco.exec"]:
        files[p.name] = copy_public_evidence(p, PUBLIC / p.name)["sha256"]
    if ok:
        for p in sorted((UNIT/"xml").glob("TEST-*.xml")):
            files[p.name]=copy_public_evidence(p,PUBLIC/p.name)["sha256"]
    write(PUBLIC/"manifest.json",dict(actualExit=0 if ok else 1, source=build["sourceCore"], terminalAtUTC=utc(), run=SCOPE,
        static=ref(static_path),  tests=len(actual), failures=failures, errors=errors, skipped=skipped, notRun=len(cases)-len(actual),
        initializationProhibited=list(sorted(HOLDS)), prohibitedObserved=list(sorted(protected)),
        selectedCases=actual, files=files, originalXmlSha256=xmls, staticApplicable=0,
        noRealBackendOrNativeAction=True, appliedCoverageFilters=[], historicalExecUsed=False,
        stages=stages, formalUpdated=False))
    print("Junit",len(actual),failures,errors,skipped,"accepted",ok)


if __name__ == "__main__":
    {"static": static, "unit": unit}[sys.argv[1]]()
