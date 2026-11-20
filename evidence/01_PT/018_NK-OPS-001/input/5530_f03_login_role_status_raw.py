"""Requalify the sole changed login projection with its original eleven-case fixture."""
import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def utc():
    return datetime.now(timezone.utc).isoformat()


def pin(p):
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def write(p, value):
    with p.open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


g = json.loads(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1422_*.json")).read_bytes())
v = g["values"]
assert sys.argv[1:] in ([], ["v2"])
run_name = v["run"] if not sys.argv[1:] else v["run"].removesuffix("-v1") + "-v2"
before_path = Path(v["oracleReferences"][1]["path"])
assert pin(before_path) == v["oracleReferences"][1]
before = json.loads(before_path.read_bytes())
assert before["source"] == v["productionCoreMain"] and before["testCounts"]["tests"] == 11
core = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
main, *rest = map(lambda row: Path(row["path"]), before["inputs"])
assert subprocess.check_output(["git", "diff", "--name-only", v["source"], core, "--", "src"],
                               text=True).splitlines() == [str(main)]
assert all(pin(Path(row["path"])) == row for row in before["inputs"][1:])
assert main.read_bytes() == subprocess.check_output(["git", "show", f"{core}:{main}"])
props_path = Path(before["schemaPOM"]["path"])
assert pin(props_path) == before["schemaPOM"]
prior_work = props_path.parents[1]
work = prior_work.parent / run_name
work.mkdir(mode=0o700)
(work / "scope").mkdir()
(work / "scope/pom.xml").write_bytes(props_path.read_bytes())
root = Path("pom.xml")
assert pin(root) == before["rootPom"]
(work / "pom.xml").write_bytes(root.read_bytes())
for p in [main, *rest[:-1]]:
    dest = work / "scope/src/main/java" / str(p).split("/src/main/java/", 1)[1]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(p.read_bytes())
tool_file = prior_work / "UnfilteredCodeMeasurement.java"
assert pin(tool_file)["sha256"] == "78c634d952e45498d7b9d26b4d0c620bcfc4ac0c56ae63020e40e203469cbaf6"
(work / tool_file.name).write_bytes(tool_file.read_bytes())

tc = Path("../toolchain").resolve()
jdk = tc / "jdk-25.0.4"
java = jdk / "bin/java"
env = {"JAVA_HOME": str(jdk), "PATH": f"{jdk}/bin:{os.defpath}", "LANG": "C.UTF-8", "TZ": "Asia/Tokyo"}
steps = []


def run(step, argv, allowed=(0,)):
    command = list(map(str, argv))
    start = utc()
    result = subprocess.run(command, capture_output=True, env=env, check=False, timeout=90)
    out, err = work / f"{step}.stdout", work / f"{step}.stderr"
    out.write_bytes(result.stdout)
    err.write_bytes(result.stderr)
    term = dict(step=step,command=command,exitCode=result.returncode,startedAtUTC=start,
                terminalAtUTC=utc(),stdout=pin(out),stderr=pin(err))
    steps.append(term)
    write(work / f"{step}-terminal.json", term)
    if result.returncode not in allowed:
        raise SystemExit(result.returncode)
    return result.stdout


expected_steps = {"format","checkstyle","typed","compile-test","unit","raw-compile","raw"}
assert {item["step"] for item in before["steps"]} == expected_steps
for item in before["steps"]:
    args = [arg.replace(str(prior_work), str(work))
            .replace(before["session"], "PG40974-LOGIN-CLOSED-VALUES-ELEVEN")
            for arg in item["command"]]
    out = run(item["step"],args)
    if item["step"] == "typed":
        assert all(flag in out for flag in (b"-Xep:NullAway:ERROR", b"-Werror", b"Compiling 13 source files"))
        assert b"[NullAway]" not in out

table = (work / "raw.stdout").read_bytes()
r, = [line.split("\t") for line in table.decode().splitlines() if line.startswith("CLASS\t")]
coverage = [dict(kind=k, missed=int(m), covered=int(c)) for k,m,c in (x.split(":") for x in r[6:])]
assert r[3] == "true"
test_xml = work / "reports/TEST-junit-jupiter.xml"
x = ET.parse(test_xml).getroot()
counts = {k:int(x.attrib[k]) for k in ("tests","errors","failures","skipped")}
names = {row.attrib["name"].removesuffix("()") for row in x.findall("testcase")}
assert counts == before["testCounts"] and names == set(before["exactMethods"])

previous_class = Path(before["physical"]["path"])
assert pin(previous_class) == before["physical"]
current_class = Path(str(previous_class).replace(str(prior_work), str(work)))
old_code = run("old-bytecode", [jdk / "bin/javap", "-c", "-p", previous_class])
current_code = run("new-bytecode", [jdk / "bin/javap", "-c", "-p", current_class])
def lock_method(data):
    return data.split(b" lockForAttempt(",1)[1].split(b" recordFailure(",1)[0]
assert lock_method(old_code).count(b"lookupswitch") == 4 and b"lookupswitch" not in lock_method(current_code)
old_api = run("old-public", [jdk / "bin/javap", "-public", "-s", previous_class])
new_api = run("new-public", [jdk / "bin/javap", "-public", "-s", current_class])
assert old_api == new_api

base = before_path.parent.parent
fixture_outputs = base / run_name
fixture_outputs.mkdir()
(fixture_outputs / "unfiltered.tsv").write_bytes(table)
known = json.loads(next(base.glob("PG40880*/manifest.json")).read_bytes())
sbc, pc = known["steps"]["spotbugs"]["command"][3], known["steps"]["pmd"]["command"][2]
assert all(Path(p).is_relative_to(tc) for p in (sbc+":"+pc).split(":"))
class_root = next(p for p in current_class.parents if p.name == "classes")
same_support = []
for row in before["supportPhysical"]:
    new_path = Path(row["path"].replace(str(prior_work),str(work)))
    assert pin(new_path)["sha256"] == row["sha256"]
    same_support.append(pin(new_path))
jspecify = tc / "m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
annotations = tc / "m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar"
aux = f"{class_root}:{jspecify}:{annotations}"
sb = fixture_outputs / "spotbugs.xml"
pmd = fixture_outputs / "pmd.xml"
run("spotbugs",[java,"-Xmx1g","-cp",sbc,"edu.umd.cs.findbugs.FindBugs2","-effort:max","-low",
                 "-xml:withMessages","-exitcode","-auxclasspath",aux,"-output",sb,current_class], allowed=(0,1))
run("pmd",[java,"-cp",pc,"net.sourceforge.pmd.cli.PmdCli","check","--dir",main,"--rulesets",
            "tools/quality/static/pmd.xml","--use-version","java-25","--aux-classpath",f"{aux}:{jdk}/lib/jrt-fs.jar",
            "--no-cache","--format","xml","--report-file",pmd],allowed=(0,4))
sb_report = ET.parse(sb).getroot()
pmd_report = ET.parse(pmd).getroot()
ns = {"p":"http://pmd.sourceforge.net/report/2.0.0"}
findings = [dict(rule=e.attrib["rule"],line=int(e.attrib["beginline"]))
            for e in pmd_report.findall("p:file/p:violation",ns)]
missing = len(sb_report.findall(".//Error")) + len(sb_report.findall(".//MissingClass"))
sb_findings = len(sb_report.findall(".//BugInstance"))
assert [e.attrib["class"] for e in sb_report.findall(".//ClassStats")] == [r[1].replace("/",".")]
passed = all(row["missed"]==0 for row in coverage) and not missing and not sb_findings
write(fixture_outputs / "manifest.json", dict(
    source=core,beforeSource=before["source"],run=run_name,startEvent=g["eventId"],
    terminalAtUTC=utc(),actualExit=0 if passed else 1,whole451=False,formalDelta=0,
    priorEvidence=pin(before_path),main=pin(main),fixture=pin(rest[-1]),testCounts=counts,
    affectedCasesRequalified=11,newTests=0,junitXml=pin(test_xml),execData=pin(work/"unit.exec"),
    unchangedPublicAbi=True,publicAbiSha256=hashlib.sha256(new_api).hexdigest(),
    staticScopeClass=pin(current_class),sameSupport=same_support,physicalClasses=len(same_support)+1,
    oldGeneratedLookupswitches=4,newGeneratedLookupswitches=0,crc64=r[2],unfilteredCounters=coverage,
    unfiltered=pin(fixture_outputs/"unfiltered.tsv"),spotBugs=dict(findings=sb_findings,errorsOrMissing=missing,report=pin(sb)),
    pmdOriginalDispositionPending=True,
    pmd=dict(rawFindings=findings,processingErrors=len(pmd_report.findall("p:error",ns)),report=pin(pmd)),
    steps=steps,novelExternalActions=0,
))
print(counts,coverage,sb_findings,missing,findings)
raise SystemExit(0 if passed else 1)
