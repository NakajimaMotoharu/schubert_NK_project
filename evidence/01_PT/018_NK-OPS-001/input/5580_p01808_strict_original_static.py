"""Analyze only the four physical shapes of the locally built coverage reader."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
SOURCE = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def read(path):
    return json.loads(path.read_bytes())


def main():
    qualified, = OPS.glob("PG41084-*/manifest.json")
    previous, = OPS.glob("PG41058-*/manifest.json")
    libs, = OPS.glob("PG31432-*/compile.json")
    tested = read(qualified)
    assert tested["toolSourceSha256"] == pin(SOURCE)["sha256"]
    assert tested["observedUnderRejection"] == 0
    assert all(pin(Path(ref["path"])) == ref for ref in read(previous)["terminals"])
    commands = {
        stage: read(previous.with_name(stage+"-terminal.json"))["command"]
        for stage in ("format", "checkstyle", "pmd", "spotbugs")
    }
    assert all(pin(Path(dep["path"])) == dep for dep in read(libs)["dependencies"])
    deps = os.pathsep.join(d["path"] for d in read(libs)["dependencies"])
    out = OPS / "PG41086-p01808-strict-original-static-v1"
    out.mkdir()
    stages = {}

    def run(label, cmd):
        args = list(map(str, cmd))
        p = subprocess.run(args, capture_output=True, timeout=75)
        stages[label] = dict(command=args, actualExit=p.returncode,
                             stdoutSha256=sha256(p.stdout).hexdigest(), stderrSha256=sha256(p.stderr).hexdigest())
        return p

    for stage in ("format", "checkstyle"):
        res = run(stage, commands[stage])
        assert res.returncode == 0
        if stage == "checkstyle":
            assert not ET.fromstring(res.stdout).findall(".//error")
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-strict-original-static-") as temp:
        classes = Path(temp) / "output"
        java = Path(commands["format"][0])
        assert run("compile", [java.with_name("javac"), "--release", "25", "-proc:none",
                              "-Werror", "-Xlint:all", "-cp", deps, "-d", classes, SOURCE]).returncode == 0
        members = sorted(classes.rglob("*.class"))
        expected = {"UnfilteredCodeMeasurement"+suffix+".class" for suffix in (
            "", "$Measurement", "$Measurement$1", "$OriginalExecutionReader")}
        assert {file.name for file in members} == expected
        pmd_path, sb_path = out/"pmd.xml", out/"spotbugs.xml"
        pmd = list(commands["pmd"])
        pmd[pmd.index("--aux-classpath")+1] = os.pathsep.join(map(str, (classes, deps, java.parent.parent/"lib/jrt-fs.jar")))
        pmd[pmd.index("--report-file")+1] = pmd_path
        pmd_exit = run("pmd", pmd).returncode
        spotbugs = list(commands["spotbugs"][:13])
        spotbugs[spotbugs.index("-auxclasspath")+1] = f"{classes}:{deps}"
        spotbugs[spotbugs.index("-output")+1] = sb_path
        sb_exit = run("spotbugs", [*spotbugs, *members]).returncode
        measurements = [dict(className=p.name, sha256=pin(p)["sha256"]) for p in members]
    pmd_root = ET.parse(pmd_path).getroot()
    ns = {"r": pmd_root.tag.partition("}")[0].removeprefix("{")}
    raw = [dict(line=int(r.attrib["beginline"]), rule=r.attrib["rule"], message=(r.text or "").strip())
           for r in pmd_root.findall("r:file/r:violation", ns)]
    sb_root = ET.parse(sb_path).getroot()
    findings = [r.attrib["type"] for r in sb_root.findall("BugInstance")]
    errors = len(sb_root.findall(".//MissingClass")) + len(sb_root.findall(".//Error"))
    assert pmd_exit in (0, 4) and not pmd_root.findall("r:error", ns)
    assert sb_exit in (0,1) and errors == 0
    result = dict(actualExit=sb_exit, source=tested["toolSource"], stagedStatic=stages,
                  currentMeasuredPhysical=measurements, formatAndCheckstyle=0,
                  pmdExit=pmd_exit, pmdRaw=raw, pmdReport=pin(pmd_path),
                  spotBugsExit=sb_exit, spotBugsFindings=findings, spotBugsReport=pin(sb_path),
                  spotBugsErrorOrMissing=errors, originalTest=pin(qualified), priorStatic=pin(previous),
                  productClassesInspected=0, productPt=0, nativeOperations=0, whole451=False,
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    dest = out / "manifest.json"
    with dest.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(dest), "pmd", raw, "spotbugs", findings)
    return sb_exit


if __name__ == "__main__":
    raise SystemExit(main())
