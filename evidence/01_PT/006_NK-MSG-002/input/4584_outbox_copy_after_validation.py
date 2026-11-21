"""Qualify the closed Outbox value constructors and their original fixture set."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
from xml.etree import ElementTree as ET

R = Path.cwd()
E = R / "evidence/01_PT/018_NK-OPS-001/evidence"
TC = R.parent / "toolchain"
JDK = TC / "jdk-25.0.4"
RUN = "PG41402-outbox-copy-after-validation-v1"
WORK = R.parent / "pgpt-runs/PG379" / RUN
OUT = E / RUN
PKG = "dev.codex.schubert.nk.api.messaging.outbound"
TARGETS = ("OutboxEntry", "OutboxRequest")
ADDED = (
    "requestRejectsEmptyBodyBeforeProfileAndRetainsBorrowedBytesOnFailure()",
    "entryRejectsLeaseBeforeProfileAndRetainsBorrowedBytesOnFailure()",
)

def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())

def git(*args):
    return subprocess.check_output(["git", *args])

def dump(path, value):
    with path.open("x") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")

def main():
    prior = next(E.glob("PG38278*/manifest.json"))
    scope = json.loads(prior.read_bytes())
    baseline = next(E.glob("PG41400*/manifest.json"))
    before = json.loads(baseline.read_bytes())
    source = git("rev-parse", "HEAD").decode().strip()
    mains = [Path(p) for p in scope["apiMainSources"]]
    mains.append(mains[0].with_name("package-info.java"))
    tests = [Path(p) for p in scope["apiTestSources"]]
    changed = set(git("diff", "--name-only", before["source"], source, "--", "src", "pom.xml").decode().splitlines())
    changed_main = [p for p in mains if p.stem in TARGETS]
    changed_test = tests[-1]
    assert changed == set(map(str, [*changed_main, changed_test])) and before["observedEarlyClone"] == 2
    for path in mains + tests:
        assert path.read_bytes() == git("show", f"{source}:{path}")
    deps = [Path(path) for path, digest in scope["dependencies"].items() if pin(Path(path))["sha256"] == digest]
    assert len(deps) == 2 and {path.name for path in deps} == {
        "jspecify-1.0.1.jar", "junit-platform-console-standalone-1.13.4.jar"}
    pom = R.parent / "pgpt-runs/PG379/pg38278-outbox-retained-value-prepare-v1/pom.xml"
    assert pin(pom)["sha256"] == scope["subsetPomSha256"]
    artifact_id = "{http://maven.apache.org/POM/4.0.0}artifactId"
    plugin = "{http://maven.apache.org/POM/4.0.0}plugin"
    def compiler(path):
        return next(ET.tostring(p) for p in ET.parse(path).iter(plugin)
                    if p.findtext(artifact_id) == "maven-compiler-plugin")
    assert compiler(pom) == compiler(R/"pom.xml")
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
    shutil.copyfile(pom, WORK / "pom.xml")
    for rel in mains:
        relative = Path(*rel.parts[2:])
        dest = WORK / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(rel, dest)
        assert pin(rel)["sha256"] == pin(dest)["sha256"]
    common = [TC/"m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn", "-o", "-B", "-ntp",
              "-f", WORK/"pom.xml", "-Dmaven.repo.local="+str(TC/"m2/repository"), "-Dmaven.test.skip=true"]
    execute("compile", [*common, "compile"])
    classes = WORK/"target/classes"
    actual = sorted(classes.rglob("*.class"))
    allowed = set(scope["physicalClassHashes"]) | {PKG.replace(".","/")+"/package-info.class"}
    assert len(actual)==len(allowed)==8 and {p.relative_to(classes).as_posix() for p in actual}==allowed
    test_classes = WORK/"test-classes"
    test_classes.mkdir()
    cp = os.pathsep.join(map(str,[classes,*deps]))
    execute("test-compile", [JDK/"bin/javac","--release","25","-g","-proc:none","-implicit:none",
                             "-encoding","UTF-8","-Xlint:all","-Werror","-cp",cp,"-d",test_classes,
                             *(R/path for path in tests)])
    java=JDK/"bin/java"
    scope_checks=[R/p for p in [*changed_main,changed_test]]
    execute("format", [java,"-jar",TC/"google-java-format-1.36.1-all-deps.jar",
                       "--dry-run","--set-exit-if-changed",*scope_checks])
    style=execute("checkstyle", [java,"-jar",TC/"static-gates-20261015/checkstyle-14.3.0-all.jar",
                                 "-c",R/"tools/quality/static/checkstyle.xml","-f","xml",*scope_checks])
    nodes=ET.fromstring(style).findall("file")
    assert {Path(n.attrib["name"]) for n in nodes}==set(scope_checks) and not any(list(n) for n in nodes)
    receipts=[]
    for path in actual:
        if path.stem not in TARGETS:
            continue
        body=execute("javap-"+path.stem,[JDK/"bin/javap","-p","-c",path]).decode()
        block=next(m for m in body.split("\n\n") if "java.util.Optional<"+PKG+".OutboxDlqMetadata>);" in m and "requireProfile" in m)
        def offset(line):
            return int(line.split(":",1)[0].strip())
        calls=[line for line in block.splitlines() if "invoke" in line]
        clones=[line for line in calls if "clone:()Ljava/lang/Object;" in line]
        assert len(clones)==1 and calls[-1]==clones[0]
        profile=next(line for line in calls if "requireProfile:" in line)
        assert offset(profile)<offset(clones[0])
        stores=[line for line in block.splitlines() if "putfield" in line and "retainedBody:" in line]
        assert len(stores)==1 and offset(clones[0])<offset(stores[0])
        report=OUT/(path.stem+".constructor.txt")
        report.write_text(block+"\n")
        receipts.append(dict(target=path.stem,bytecode=pin(path),profileOffset=offset(profile),
                             cloneOffset=offset(clones[0]),constructor=pin(report)))
    assert len(receipts)==2
    agent=TC/"m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar"
    exec_file=WORK/"unit.exec"
    report_dir=WORK/"reports"
    execute("ordinary", [java,f"-javaagent:{agent}=destfile={exec_file},sessionid={RUN}",
            "-cp",str(test_classes)+os.pathsep+cp,"org.junit.platform.console.ConsoleLauncher","execute",
            "--disable-ansi-colors","--fail-if-no-tests",
            *[arg for test in scope["selectedClasses"] for arg in ("--select-class",test)],
            "--reports-dir",report_dir])
    jupiter=report_dir/"TEST-junit-jupiter.xml"
    xml=ET.parse(jupiter).getroot()
    expected={(v["classname"],v["name"]) for v in scope["expectedCases"]}
    expected.update((PKG+".OutboxRetainedValueContractTest",name) for name in ADDED)
    rows=xml.findall("testcase")
    observed={(n.attrib["classname"],n.attrib["name"]) for n in rows}
    assert len(expected)==len(rows)==len(observed)==10 and observed==expected
    assert all(int(xml.attrib[k])==0 for k in ("errors","failures","skipped"))
    dump(OUT/"ordinary-cases.json",[dict(className=c,name=n,result="PASS") for c,n in sorted(observed)])
    pmd_report=WORK/"pmd.xml"
    execute("pmd",[TC/"static-gates-20261015/pmd-bin-7.28.0/bin/pmd","check","--dir",
                   ",".join(map(str,scope_checks)),"--rulesets",R/"tools/quality/static/pmd.xml",
                   "--aux-classpath",cp+os.pathsep+str(JDK/"lib/jrt-fs.jar"),"--use-version","java-25",
                   "--no-cache","--format","xml","--report-file",pmd_report],(0,4))
    pmd_tree=ET.parse(pmd_report)
    findings=[dict(file=Path(f.attrib["name"]).name,rule=v.attrib["rule"],line=int(v.attrib["beginline"]))
              for f in pmd_tree.findall(".//{*}file") for v in f.findall("{*}violation")]
    assert not pmd_tree.findall(".//{*}error")
    execute("spotbugs",[*common,"spotbugs:spotbugs"])
    sb=WORK/"target/spotbugsXml.xml"
    sb_tree=ET.parse(sb)
    assert not sb_tree.findall(".//BugInstance") and not sb_tree.findall(".//MissingClass")
    assert not sb_tree.findall(".//Error")
    dump(OUT/"manifest.json",dict(run=RUN,actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
        source=source,original=pin(baseline),exactCompilerPolicy=True,derivedPom=pin(pom),
        inputs=[pin(p) for p in mains+tests],allowedClasses=[pin(p) for p in actual],constructors=receipts,
        selectedTests=10,requiredOldCases=8,newCases=2,failures=0,errors=0,skipped=0,notRun=0,
        actualExternalOperations=0,heldClassfileAccess=0,productWhole=False,whole451=False,formalDelta=0,
        sourceOnlyFormat=0,checkstyleFindings=0,spotbugsFindings=0,pmdRaw=findings,
        staticReports=dict(pmd=pin(pmd_report),spotbugs=pin(sb)),oldReportsRerunForItsOwnSake=0,
        jupiter=pin(jupiter),unitExec=pin(exec_file),steps=steps))
    print(RUN,len(expected),findings)

if __name__ == "__main__":
    main()
