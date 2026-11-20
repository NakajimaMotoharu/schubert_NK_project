"""Verify both sides of the documented final-byte decimal boundary."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


r = runpy.run_path(str(Path(__file__).with_name("5619_range_unit_ascii.py")))
BIN, OPS, WEB, DIR, MAIN, read, pin, check, successful_case = (
    r[key] for key in ("BIN", "OPS", "WEB", "DIR", "MAIN", "read", "pin", "check", "successful_case")
)
INITIAL = "PG41246-media-range-bounded-decimal-end-v1"
CORRECTED = "PG41248-media-range-decimal-corrected-catalog-v1"
CLASS = "HttpByteRangeDecimalLimitTest"
TEST = WEB/"test/java"/DIR/(CLASS+".java")


def main(corrected):
    group, = Path("documents/400_PGPT/470_PMO").glob("601_*/1661_*.json")
    context = read(group)["values"]
    for item in context["oracleReferences"]:
        path = Path(item["path"])
        if str(path).startswith("documents/300_SS/"):
            canonical = subprocess.check_output(
                ["git","show",f'{context["canonicalDesignSource"]}:{path}'],timeout=12)
            assert r["helpers"]["sha"](canonical)==item["sha256"]
        else:
            assert pin(path) == item
    design = Path(context["oracleReferences"][-2]["path"])
    active_design = None
    if corrected:
        active_design = subprocess.check_output(["git","rev-parse","origin/main"],text=True,timeout=12).strip()
        current = subprocess.check_output(["git","show",f"{active_design}:{design}"],timeout=12)
        assert "（SSC-476）。" in current.decode() and "9,223,372,036,854,775,807" in current.decode()
        earlier = read(OPS/INITIAL/"manifest.json")
        fixture = TEST.read_text()
        assert fixture.count("SSC-476") == 1 and "SSC-475" not in fixture
        assert r["helpers"]["sha"](fixture.replace("SSC-476","SSC-475").encode())==earlier["source"]["sha256"]
    run_name = CORRECTED if corrected else INITIAL
    old_path = Path(context["oracleReferences"][-1]["path"])
    prior = read(old_path)
    assert prior["actualExit"] == 0
    assert subprocess.check_output(["git","show",f'{context["productionCoreMain"]}:{MAIN}'],
                                   timeout=10) == MAIN.read_bytes()
    assert pin(MAIN) == prior["main"]
    original = {Path(row["path"]).name:row["sha256"] for row in prior["physical"]}
    console, agent = [Path(prior[name]["path"]) for name in ("junit","agent")]
    assert pin(console) == prior["junit"] and pin(agent) == prior["agent"]
    stage = {}
    style = Path("../toolchain/static-gates-20261015/checkstyle-14.3.0-all.jar")
    fmt = Path("../toolchain/google-java-format-1.36.1-all-deps.jar")
    stage["format"], norm = check([BIN/"java","-jar",fmt,"--dry-run","--set-exit-if-changed",TEST])
    stage["checkstyle"], cs = check([BIN/"java","-jar",style,"-c","tools/quality/static/checkstyle.xml","-f","xml",TEST])
    assert norm.returncode == cs.returncode == 0 and not ET.fromstring(cs.stdout).findall(".//error")
    local = (Path("../pgpt-runs/PG379")/run_name).resolve()
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-range-decimal-limit-") as temp:
        types = Path(temp)/"classes"
        types.mkdir()
        stage["compile"], compiled = check([BIN/"javac","--release","25","-g","-Xlint:all",
            "-Werror","-proc:none","-cp",console,"-d",types,MAIN,TEST])
        assert compiled.returncode == 0, compiled.stderr
        measured = {path.name:pin(path)["sha256"] for path in (types/DIR).glob("HttpByteRangeParser*.class")}
        assert len(measured) == 5 and measured == original
        local.mkdir()
        track, xml = local/"unit.exec", local/"xml"
        package = r["PACKAGE"]+"."+CLASS
        cp = os.pathsep.join(map(str,(types,console)))
        stage["junit"], run = check([BIN/"java","-Dfile.encoding=UTF-8",
            f"-javaagent:{agent}=destfile={track},append=false,sessionid={run_name}",
            "-cp",cp,"org.junit.platform.console.ConsoleLauncher","execute","--disable-banner",
            "--details=summary","--fail-if-no-tests","--reports-dir",xml,"--select-class",package])
        terminal = local/"terminal.json"
        terminal.write_text(json.dumps(stage["junit"],indent=2)+"\n")
        raw = xml/"TEST-junit-jupiter.xml"
        suite = ET.parse(raw).getroot()
        [case] = suite.findall("testcase")
        assert [suite.get(key) for key in ("tests","failures","errors","skipped")]==["1","0","0","0"]
        assert run.returncode == 0 and case.get("classname")==package and successful_case(case)
        assert case.get("name")=="acceptsTheMaximumDecimalEndAndRejectsTheNextInsteadOfClampingIt()"
        names = {DIR.as_posix()+"/HttpByteRangeParser", DIR.as_posix()+"/"+CLASS}
        probes = runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"](
            track.read_bytes(), names)["classes"]
        crc = runpy.run_path(str(Path(__file__).with_name("5593_p01808_original_name_binding.py")))["class_id"]
        for name, row in probes.items():
            assert int(row["crc64"],16)==crc((types/(name+".class")).read_bytes())
    limit = (1 << 63) - 1
    assert int("9223372036854775807")==limit and int("9223372036854775808")==limit+1
    bound = dict(maximum=limit, next=limit+1, total=3, begin=0, end=2, inclusiveLength=3)
    out = OPS/run_name
    out.mkdir()
    for name, p in (("unit.exec", track),("jupiter.xml", raw)):
        (out/name).write_bytes(p.read_bytes())
    d = dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
             productionCore=context["productionCoreMain"],run=run_name,
             ssc="SSC-476" if corrected else "SSC-475",correctedCanonicalDesign=active_design,
             testId="PT-MED-RANGE-BOUND-001",cases=1,failed=0,errors=0,skipped=0,notRun=0,
             source=pin(TEST),stages=stage,prior=pin(old_path),productionPhysicalSameAsEarlier=5,
             originalProbeBinding=probes,oracle=bound,originals=list(map(pin,(track,raw,terminal))),
             oldProductTestsRepeated=0,actualMediaOperations=0,whole451=False,formalDelta=0)
    result = out/"manifest.json"
    with result.open("x") as f:
        json.dump(d,f,indent=2)
        f.write("\n")
    print(pin(result),len(probes))


if __name__ == "__main__":
    assert sys.argv[1:] in ([],["--corrected"])
    main(bool(sys.argv[1:]))
