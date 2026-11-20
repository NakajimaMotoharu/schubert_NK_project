"""Measure the time-window type and its public state factories in one admitted JUnit scope."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
JDK = Path("../toolchain/jdk-25.0.4/bin").resolve()
CODE = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
NAMESPACE = "dev/codex/schubert/nk/batch/monitoring/"
CLI = "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement"
TARGETS = tuple(NAMESPACE + "ContinuousConditionWindow" + suffix + ".class"
                for suffix in ("","$State"))
DECODER = "dba164629c:tools/quality/jacoco_readonly_exec_subset.py"


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return sha256(data).hexdigest()


def pin(p):
    return dict(path=str(p), sha256=sha(p.read_bytes()))


def read(p):
    return json.loads(p.read_bytes())


def git(*items):
    return subprocess.check_output(["git", *items], timeout=30)


def parse_measurement(raw):
    entries = []
    for line in raw.decode().splitlines():
        cells = line.split("\t")
        if cells[0] == "CLASS":
            assert cells[3] == "true"
            counters = {name: {"missed": int(miss), "covered": int(hit)}
                        for name, miss, hit in (part.split(":") for part in cells[6:])}
            entries.append(dict(className=cells[1],crc64=cells[2],counters=counters))
    assert {row["className"]+".class" for row in entries} == set(TARGETS)
    return entries


def tally(entries, key):
    return sum(item["counters"][key]["missed"] for item in entries)


def main():
    checkpoint, = Path("documents/400_PGPT/470_PMO").glob("601_*/1549_*")
    scope = read(checkpoint)["values"]
    refs = [Path(ref["path"]) for ref in scope["oracleReferences"]]
    assert [pin(p) for p in refs] == scope["oracleReferences"]
    old, prior_post, preserved, package, new_tool = map(read, refs[1:])
    core = scope["productionCoreMain"]
    assert package["source"] == core
    assert (old["productTestsExecuted"],prior_post["tests"]) == (23,23)
    assert old["stages"]["unit"]["actualExit"] == 0
    args = old["stages"]["unit"]["command"]
    probe = next(w for w in args if w.startswith("-javaagent:"))
    agent, init = probe.removeprefix("-javaagent:").split("=",1)
    original_exec = Path(re.search(r"destfile=([^,]*)",init).group(1))
    session_old = re.search(r"sessionid=([^,]*)",init).group(1)
    assert (original_exec.parent/"manifest.json").read_bytes() == refs[1].read_bytes()
    published_window = [c["name"].removesuffix("()") for c in old["cases"]
                        if c["className"].endswith(".ContinuousConditionWindowTest")]
    assert len(published_window)==8 and len(set(published_window))==8
    artifact = Path(package["batchArtifact"]["path"])
    assert pin(artifact) == package["batchArtifact"]
    files = [Path(r["path"]) for r in preserved["sourceInputs"] if "/src/main/" in r["path"]]
    assert len(files)==22 and all(f.suffix==".java" for f in files)
    main_exact = {str(x).split("/src/main/java/")[1].removesuffix(".java") for x in files}
    assert all(git("show",f"{core}:{p}")==p.read_bytes() for p in files)
    domain = Path("src/schubert-nk-batch/src/test/java") / NAMESPACE
    tests = [domain/(name+"Test.java") for name in ("ContinuousConditionWindow","GeneratedBatchValueContract")]
    assert old["begin"]["inputHashes"][str(tests[0])] == pin(tests[0])["sha256"]
    assert any(pin(tests[1])==p for p in preserved["sourceInputs"])
    assert all(git("show",f"{scope['source']}:{p}")==p.read_bytes() for p in tests)
    assert new_tool["toolSourceSha256"] == pin(CODE)["sha256"]
    dep_report, = OPS.glob("PG31432-*/compile.json")
    raw_deps = read(dep_report)["dependencies"]
    program = preserved["dependencyInputs"]
    assert all(pin(Path(p["path"])) == p for p in [*raw_deps,*program])
    cp = os.pathsep.join(item["path"] for item in raw_deps)
    libs = os.pathsep.join(item["path"] for item in program)
    junit = Path("../toolchain/junit-platform-console-standalone-1.13.4.jar").resolve()
    dcode = git("show",DECODER)
    ns = {}
    exec(compile(dcode,DECODER,"exec"),ns)
    selectors = {n.removesuffix(".class") for n in TARGETS}
    saved_stream = ns["decode"](original_exec.read_bytes(),selectors)
    assert saved_stream["sessions"][0]["labelBytesHex"] == session_old.encode().hex()
    dest = OPS / scope["run"]
    dest.mkdir()
    private = Path.cwd().parent/"pgpt-runs/PG379"/scope["run"]
    private.mkdir(mode=0o700)
    steps = {}

    def run(label, cmd):
        command = list(map(str,cmd))
        p = subprocess.run(command,capture_output=True,timeout=75,
                           env={"PATH":os.defpath,"LANG":"C.UTF-8","TZ":"Asia/Tokyo"})
        (private/(label+".stdout")).write_bytes(p.stdout)
        (private/(label+".stderr")).write_bytes(p.stderr)
        steps[label] = dict(command=command,exit=p.returncode,terminalAtUTC=utc(),
                            stdoutSha256=sha(p.stdout),stderrSha256=sha(p.stderr))
        assert p.returncode==0,label
        return p.stdout

    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-window-class-proof-") as d:
        root = Path(d)
        raw_bin, base_classes, compiled_tests = [root/p for p in ("raw","product","fixtures")]
        with ZipFile(artifact) as jar:
            names = [name for name in jar.namelist() if name.endswith(".class") and
                     name.removesuffix(".class").split("$",1)[0] in main_exact]
            assert len(names)==len(set(names))
            assert {name.removesuffix(".class").split("$",1)[0] for name in names}==main_exact
            for name in names:
                target = base_classes/name
                target.parent.mkdir(exist_ok=True,parents=True)
                target.write_bytes(jar.read(name))
        for name in TARGETS:
            assert pin(base_classes/name)["sha256"] == old["begin"]["targetClassHashes"][name]
        javac = JDK/"javac"
        options = [javac,"--release",25,"-Werror","-Xlint:all","-proc:none","-implicit:none"]
        run("raw-compile",[*options,"-cp",cp,"-d",raw_bin,CODE])
        raw_cmd = [JDK/"java","-cp",f"{raw_bin}:{cp}",CLI,"--strict-original-exec"]
        target_paths = [base_classes/name for name in TARGETS]
        old_raw = run("historical-unfiltered",[*raw_cmd,original_exec,*target_paths])
        (dest/"original-unfiltered.tsv").write_bytes(old_raw)
        old_rows = parse_measurement(old_raw)
        assert tally(old_rows,"METHOD")>0
        expected = {
            (NAMESPACE.replace("/",".")+path.stem,name)
            for path in tests for name in re.findall(r"@Test\s+void (\w+)\(",path.read_text())
        }
        assert len(expected)==15 and {name for cls,name in expected
                                     if cls.endswith(".ContinuousConditionWindowTest")}==set(published_window)
        run("fixtures",[*options,"-cp",f"{base_classes}:{junit}:{libs}","-d",compiled_tests,*tests])
        exec_data = private/"current.exec"
        xml = private/"junit"
        session = "PG41108"
        run("unit",[JDK/"java",f"-javaagent:{agent}=destfile={exec_data},append=false,sessionid={session}",
                    "-jar",junit,"execute","--disable-ansi-colors","--fail-if-no-tests",
                    "--class-path",f"{base_classes}:{compiled_tests}:{libs}","--reports-dir",xml,
                    *[p for path in tests for p in ("--select-class",NAMESPACE.replace("/",".")+path.stem)]])
        xml = xml/"TEST-junit-jupiter.xml"
        document = ET.parse(xml).getroot()
        assert [int(document.attrib[key]) for key in ("tests","failures","errors","skipped")]==[15,0,0,0]
        assert {(c.attrib["classname"],c.attrib["name"].removesuffix("()")) for c in document.findall("testcase")}==expected
        after = run("current-unfiltered",[*raw_cmd,exec_data,*target_paths])
        (dest/"current-unfiltered.tsv").write_bytes(after)
        rows = parse_measurement(after)
        stream = ns["decode"](exec_data.read_bytes(),selectors)
        assert stream["sessions"][0]["labelBytesHex"] == session.encode().hex()
        for i in rows:
            assert int(i["crc64"],16)==int(stream["classes"][i["className"]]["crc64"],16)
            assert all(v["missed"]==0 for v in i["counters"].values())
        final = {name:sum(i["counters"][name]["covered"] for i in rows) for name in rows[0]["counters"]}
        source_refs = [dict(classPath=name,sha256=pin(base_classes/name)["sha256"]) for name in TARGETS]
    whole = dest/"manifest.json"
    with whole.open("x") as out:
        json.dump(dict(actualExit=0,productionCore=core,fixtureSource=scope["source"],
                       measurementSource=new_tool["toolSource"],testCount=15,suites=2,
                       failures=0,errors=0,skips=0,notRun=0,sourceFilesUnchanged=True,
                       generatedFixtureSeven=7,originalWindowEight=8,extractedAuthorizedPhysical=len(names),
                       measuredPhysical=source_refs,oldWindowFixture23Proof=pin(refs[1]),
                       sourceAndTypeSame=True,productTestsReplayedForConfirmation=0,
                       priorMisses={name:tally(old_rows,name) for name in final},rawCurrent=final,
                       observedCrcs=rows,oldExecNoMerge=pin(original_exec),currentSession=session,
                       currentExec=pin(exec_data),originalJunitXml=pin(xml),oracleSourceRefs=scope["oracleReferences"],
                       steps=steps,nativeOrBackendActions=0,whole451=False,formalDelta=0,
                       terminalAtUTC=utc()),out,indent=2,ensure_ascii=False)
        out.write("\n")
    print(pin(whole),final,{name:tally(old_rows,name) for name in final})


if __name__=="__main__":
    main()
