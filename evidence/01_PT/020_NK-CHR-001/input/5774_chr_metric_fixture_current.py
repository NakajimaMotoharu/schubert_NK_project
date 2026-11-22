"""Analyze and exercise only the in-memory CHR gate metric projection."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path.cwd()
OPS = (ROOT.parent / "pgpt-runs/PG379").resolve()
PROGRAM = Path("program/characterization")
RECEIPTS = Path("evidence/01_PT/020_NK-CHR-001/evidence")
NAME = "dev.codex.schubert.characterization.GateMetricsCountTest"
CASE = Path(*NAME.split("."))
TEST = PROGRAM / "tests/java" / CASE.with_suffix(".java")


def sha(content):
    return hashlib.sha256(content).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(path.read_bytes())


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=45)


def main(changed):
    run = "PG43108-chr-metric-direct-values-v1" if changed else "PG43106-chr-metric-fixture-current-static-v1"
    out = OPS/run
    out.mkdir(mode=0o700)
    (out/"test").mkdir()
    (out/"xml").mkdir()
    previous, = RECEIPTS.glob("PG43030*/manifest.json")
    baseline = read(previous)
    start = read(Path(baseline["inputProof"]["path"]))
    assert pin(Path(baseline["inputProof"]["path"]))==baseline["inputProof"]
    current=git("rev-parse","HEAD").decode().strip()
    assert not git("diff","--name-only",baseline["source"],current,"--",str(PROGRAM/"src/main"),str(PROGRAM/"pom.xml"))
    assert git("rev-parse","HEAD:program/characterization/baseline/current").decode().strip()==baseline["currentBaselineTree"]
    assert git("show",f"{current}:{TEST}")==TEST.read_bytes()
    assert (git("show",f'{baseline["source"]}:{TEST}')!=TEST.read_bytes())==changed
    jar=Path(baseline["normalJar"]["path"])
    assert pin(jar)==baseline["normalJar"]
    previous_compile=start["commands"]["compile-tests"]
    dependencies=[
        Path(s) for s in previous_compile[previous_compile.index("-cp")+1].split(os.pathsep)
        if Path(s).name.startswith(("junit-platform-console-", "jackson-", "jspecify-"))
    ]
    assert len(dependencies)==5
    previous_local=Path(baseline["inputProof"]["path"]).parent
    common=[str(jar),*map(str,dependencies)]
    auxiliary=[]
    if not changed:
        target=CASE.with_name("GateDefinitionDocumentsTest").with_suffix(".class")
        path=previous_local/"tests"/target
        assert path.is_file()
        local=out/"compiled-aux"
        (local/target).parent.mkdir(parents=True)
        (local/target).write_bytes(path.read_bytes())
        assert (local/target).read_bytes()==path.read_bytes()
        auxiliary=[str(local)]
    classpath=os.pathsep.join([*common,*auxiliary])
    sdk=ROOT.parent/"toolchain/jdk-25.0.4/bin"
    steps={"compile":[str(sdk/"javac"),"--release","25","-g","-proc:none","-implicit:none",
                      "-Xlint:all","-Werror","-cp",classpath,"-d",str(out/"test"),str(TEST)]}
    tooling=OPS/"PG43064-transfer-test-checked-declaration-v1"
    frozen=read(tooling/"begin.json")["commands"]
    (out/"current-static-sources.txt").write_text(str(TEST)+"\n")
    for key in ("style","pmd","spotbugs"):
        if key=="style":
            steps[key]=[*frozen[key][:-2],str(TEST)]
            continue
        adjusted=[arg.replace(str(tooling),str(out)) for arg in frozen[key]]
        cp=adjusted.index("--aux-classpath" if key=="pmd" else "-auxclasspath")+1
        adjusted[cp]=classpath
        if key=="spotbugs":
            assert adjusted[-2:]==[str(out/"target/classes"),str(out/"test")]
            adjusted.pop(-2)
        steps[key]=adjusted
    if changed:
        steps["junit"]=[
            str(sdk/"java"),"-Djunit.jupiter.extensions.autodetection.enabled=false",
            "-Djunit.jupiter.execution.parallel.enabled=false","-Djunit.jupiter.execution.timeout.default=15 s",
            "-Dfile.encoding=UTF-8","-Duser.timezone=Asia/Tokyo",
            "-cp",os.pathsep.join([str(out/"test"),*common]),"org.junit.platform.console.ConsoleLauncher",
            "execute","--disable-ansi-colors","--fail-if-no-tests","--reports-dir",str(out/"xml"),
            "--select-class",NAME,
        ]
    begin=dict(run=run,source=current,toolMainSource=baseline["source"],sourceFixture=pin(TEST),
               courseScope="provided synthetic integer counts and JSON from JVM memory",
               originTool=pin(previous),normalToolPin=pin(jar), dependencies=list(map(pin,dependencies)),
               previousFixtureAuxiliary=auxiliary,commands=steps,startedAtUTC=now())
    (out/"begin.json").write_text(json.dumps(begin,indent=2)+"\n")
    state={}
    for key, args in steps.items():
        process=subprocess.run(args,cwd=ROOT,capture_output=True,timeout=120)
        (out/f"{key}.stdout").write_bytes(process.stdout)
        (out/f"{key}.stderr").write_bytes(process.stderr)
        state[key]=dict(exit=process.returncode,terminalAtUTC=now())
        print(key,process.returncode,flush=True)
        allowed={"pmd":{0,4},"spotbugs":{0,1}}.get(key,{0})
        if process.returncode not in allowed:
            raise SystemExit(process.returncode)
        if key=="compile":
            assert {p.relative_to(out/"test") for p in (out/"test").rglob("*.class")}=={CASE.with_suffix(".class")}
    cases=[]
    if changed:
        report=out/"xml/TEST-junit-jupiter.xml"
        suite=ET.parse(report).getroot()
        assert suite.get("tests")=="6" and all(suite.get(k)=="0" for k in ("errors","failures","skipped"))
        cases=[x.get("name").removesuffix("()") for x in suite if x.tag=="testcase"]
        expected=Path(baseline["originalJUnit"]["path"])
        assert pin(expected)==baseline["originalJUnit"]
        fixture_rows=[x.get("name").removesuffix("()") for x in ET.parse(expected).getroot().iter("testcase")
                      if x.get("classname")==NAME]
        assert len(cases)==len(fixture_rows)==6 and set(cases)==set(fixture_rows)
    terminal=dict(source=current,actualExit=0,tools=state,selectedCases=cases,terminalAtUTC=now(),
                  realChrRuns=0,baselineAccessByFixture=0)
    (out/"terminal.json").write_text(json.dumps(terminal,indent=2)+"\n")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-values",action="store_true")
    options=parser.parse_args()
    main(options.direct_values)
