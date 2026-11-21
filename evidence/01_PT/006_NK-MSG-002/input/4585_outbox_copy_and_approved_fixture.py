"""Qualify the corrected fixture using the original, unchanged Outbox Main build."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET
from pgpt_public_unit_xml import copy_public_evidence

R = Path.cwd()
E = R / "evidence/01_PT/018_NK-OPS-001/evidence"
TC = R.parent / "toolchain"
JDK = TC / "jdk-25.0.4"
RUN = "PG41404-outbox-copy-and-approved-fixture-v1"
BASE = R.parent / "pgpt-runs/PG379"
WORK = BASE / RUN
OUT = E / RUN
PKG = "dev.codex.schubert.nk.api.messaging.outbound"
ADDED = (
    "requestRejectsEmptyBodyBeforeProfileAndRetainsBorrowedBytesOnFailure()",
    "entryRejectsLeaseBeforeProfileAndRetainsBorrowedBytesOnFailure()",
)

def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())

def dump(path, value):
    with path.open("x") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")

def main():
    prior = next(E.glob("PG38278*/manifest.json"))
    scope = json.loads(prior.read_bytes())
    original = next(E.glob("PG41402*/failure.json"))
    failure = json.loads(original.read_bytes())
    old = BASE/failure["run"]
    assert failure["actualExit"]==1 and failure["failures"]==2
    source = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    mains = [Path(path) for path in scope["apiMainSources"]]
    mains.append(mains[0].with_name("package-info.java"))
    tests = [Path(path) for path in scope["apiTestSources"]]
    changed = subprocess.check_output(["git","diff","--name-only",failure["source"],source,"--","src"],text=True).splitlines()
    assert changed == [str(tests[0])]
    for path in mains:
        assert path.read_bytes()==(old/Path(*path.parts[2:])).read_bytes()
    old_fixture=subprocess.check_output(["git","show",f'{failure["source"]}:{tests[0]}'],text=True)
    expected_fixture=old_fixture.replace('import static org.junit.jupiter.api.Assertions.assertTrue;\n','')
    for name in ("entry","request"):
        before=f'assertTrue({name}.toString().contains("body=<redacted>"));'
        after=f'assertEquals("Outbox{name.title()}[<redacted>]", {name}.toString());'
        assert expected_fixture.count(before)==1
        expected_fixture=expected_fixture.replace(before,after)
    assert tests[0].read_text()==expected_fixture
    assert all(path.read_bytes()==subprocess.check_output(["git","show",f"{source}:{path}"]) for path in mains+tests)
    deps = [Path(p) for p, digest in scope["dependencies"].items() if pin(Path(p))["sha256"]==digest]
    assert len(deps)==2
    classes = old/"target/classes"
    actual=sorted(classes.rglob("*.class"))
    assert {p.relative_to(classes).as_posix() for p in actual} == set(scope["physicalClassHashes"])|{PKG.replace(".","/")+"/package-info.class"}
    assert len(actual)==8
    assert json.loads((original.parent/"compile-exit.json").read_bytes())["actualExit"]==0
    WORK.mkdir(mode=0o700)
    OUT.mkdir()
    env = dict(PATH=str(JDK / "bin") + ":/usr/bin:/bin", JAVA_HOME=str(JDK), LANG="C.UTF-8",
               TZ="Asia/Tokyo", HOME=os.environ["HOME"])
    steps = {}
    def execute(name, args, acceptable=(0,)):
        args = list(map(str, args))
        result = subprocess.run(args, cwd=WORK, env=env, capture_output=True, timeout=90, check=False)
        out, err = WORK/(name+".stdout"), WORK/(name+".stderr")
        out.write_bytes(result.stdout)
        err.write_bytes(result.stderr)
        steps[name] = dict(argv=args, actualExit=result.returncode, stdout=pin(out), stderr=pin(err))
        dump(OUT/(name+"-exit.json"), steps[name])
        assert result.returncode in acceptable, (name, result.returncode, result.stderr.decode()[-400:])
        return result.stdout
    test_classes=WORK/"test-classes"
    test_classes.mkdir()
    cp=os.pathsep.join(map(str,[classes,*deps]))
    execute("test-compile",[JDK/"bin/javac","--release","25","-g","-proc:none","-implicit:none","-encoding","UTF-8",
        "-Xlint:all","-Werror","-cp",cp,"-d",test_classes,*(R/path for path in tests)])
    java=JDK/"bin/java"
    changed_test=R/tests[0]
    execute("format",[java,"-jar",TC/"google-java-format-1.36.1-all-deps.jar","--dry-run","--set-exit-if-changed",changed_test])
    style=execute("checkstyle",[java,"-jar",TC/"static-gates-20261015/checkstyle-14.3.0-all.jar",
        "-c",R/"tools/quality/static/checkstyle.xml","-f","xml",changed_test])
    assert all(not list(n) for n in ET.fromstring(style).findall("file"))
    agent=TC/"m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    exec_file=WORK/"unit.exec"
    report_dir=WORK/"reports"
    execute("ordinary",[java,f"-javaagent:{agent}=destfile={exec_file},sessionid={RUN}","-cp",str(test_classes)+os.pathsep+cp,
        "org.junit.platform.console.ConsoleLauncher","execute","--disable-ansi-colors","--fail-if-no-tests",
        *[arg for test in scope["selectedClasses"] for arg in ("--select-class",test)],"--reports-dir",report_dir])
    jupiter=report_dir/"TEST-junit-jupiter.xml"
    xml=ET.parse(jupiter).getroot()
    expected={(v["classname"],v["name"]) for v in scope["expectedCases"]}
    expected.update((PKG+".OutboxRetainedValueContractTest",n) for n in ADDED)
    rows=xml.findall("testcase")
    observed={(n.attrib["classname"],n.attrib["name"]) for n in rows}
    assert len(expected)==len(rows)==len(observed)==10 and observed==expected
    assert all(int(xml.attrib[k])==0 for k in ("errors","failures","skipped"))
    public_xml=OUT/"jupiter.xml"
    redaction=copy_public_evidence(jupiter,public_xml)
    static_sources=[R/p for p in mains if p.stem in ("OutboxEntry","OutboxRequest")]
    static_sources.extend((R/tests[0],R/tests[-1]))
    report=WORK/"pmd.xml"
    execute("pmd",[TC/"static-gates-20261015/pmd-bin-7.28.0/bin/pmd","check","--dir",
         ",".join(map(str,static_sources)),"--rulesets",R/"tools/quality/static/pmd.xml",
         "--aux-classpath",cp+os.pathsep+str(JDK/"lib/jrt-fs.jar"),"--use-version","java-25",
         "--no-cache","--format","xml","--report-file",report],(0,4))
    pmd=ET.parse(report)
    findings=[dict(file=Path(f.attrib["name"]).name,rule=v.attrib["rule"],line=int(v.attrib["beginline"]))
        for f in pmd.findall(".//{*}file") for v in f.findall("{*}violation")]
    assert not pmd.findall(".//{*}error")
    maven=TC/"m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
    execute("spotbugs",[maven,"-o","-B","-ntp","-f",old/"pom.xml","-Dmaven.repo.local="+str(TC/"m2/repository"),
        "-Dmaven.test.skip=true","spotbugs:spotbugs"])
    sb=old/"target/spotbugsXml.xml"
    sb_tree=ET.parse(sb)
    assert not sb_tree.findall(".//BugInstance") and not sb_tree.findall(".//MissingClass")
    assert not sb_tree.findall(".//Error")
    dump(OUT/"manifest.json",dict(run=RUN,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        source=source,originalFailure=pin(original),originalMainCompile=pin(original.parent/"compile-exit.json"),
        originalConstructors=[pin(p) for p in sorted(original.parent.glob("*.constructor.txt"))],
        productMainInputs=[pin(p) for p in mains],productMainClasses=[pin(p) for p in actual],testInputs=[pin(p) for p in tests],
        productRebuilds=0,reusedProductCompileOnly=True,originalFailedExecMerged=False,formalDelta=0,whole451=False,
        tests=10,newTests=2,originalTests=8,firstAttemptSuccess=8,failures=0,errors=0,skipped=0,notRun=0,
        backendOperations=0,heldTypesOpened=0,spotbugsFindings=0,pmdRaw=findings,
        staticReports=dict(pmd=pin(report),spotbugs=pin(sb)),unitExec=pin(exec_file),jupiter=pin(public_xml),redaction=redaction,
        steps=steps))
    print(RUN,len(rows),findings)

if __name__ == "__main__":
    main()
