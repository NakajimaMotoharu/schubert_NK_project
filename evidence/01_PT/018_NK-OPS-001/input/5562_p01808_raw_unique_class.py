"""Test raw metric input uniqueness with owned synthetic class files and independent CRCs."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from struct import pack
import json
import runpy
import subprocess
import sys


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
METER = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
HEADER = bytes.fromhex("01c0c01007 10 0003 52554e 0000000000000001 0000000000000002")
MAIN = "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement"
A = "physicalfixture/First"
B = "physicalfixture/Second"


def digest(blob):
    return sha256(blob).hexdigest()


def pin(p):
    return dict(path=str(p), sha256=digest(p.read_bytes()))


def read(p):
    return json.loads(p.read_bytes())


def utc():
    return datetime.now(timezone.utc).isoformat()


def main(phase):
    assert phase in ("red", "green")
    red = phase == "red"
    start = read(next(Path("documents/400_PGPT/470_PMO").glob("601_*/1510_*")))
    context = start["values"]
    refs = context["oracleReferences"]
    assert all(pin(Path(r["path"])) == r for r in refs[:-1])
    old_crc, old_readonly = (read(Path(r["path"])) for r in refs[1:3])
    assert old_crc["actualExit"] == old_readonly["actualExit"] == 0
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    fixed_body = subprocess.check_output(["git", "show", f"{source}:{METER}"])
    assert fixed_body == METER.read_bytes()
    assert (pin(METER)==refs[-1]) is red
    assert bool(subprocess.check_output(["git", "diff", "--name-only", context["source"], source, "--", "src"])) is False
    old_fixture = runpy.run_path(str(Path(old_crc["verifier"]["path"])))
    assert pin(Path(old_crc["verifier"]["path"])) == old_crc["verifier"]
    calc = old_fixture["crc64_java25"]
    decode_path = Path(old_readonly["tool"]["path"])
    assert pin(decode_path) == old_readonly["tool"]
    decode = runpy.run_path(str(decode_path))["decode"]
    deps = [Path(r["path"]) for r in old_crc["dependencies"]]
    assert [pin(p) for p in deps] == old_crc["dependencies"] and len(deps) == 4
    java, javac = [Path(old_crc[tool]["path"]) for tool in ("java", "javac")]
    assert pin(java)==old_crc["java"] and pin(javac)==old_crc["javac"]
    run = (context["run"] if red else "PG41052-p01808-raw-duplicate-class-green-v1")
    private = Path("../pgpt-runs/PG379").resolve() / run
    private.mkdir(mode=0o700)
    deps_cp = ":".join(map(str, deps))
    steps = []

    def call(label, argv):
        start_at = utc()
        cmd = list(map(str, argv))
        result = subprocess.run(cmd, cwd=private, capture_output=True, timeout=30, check=False)
        stdout, stderr = (private / f"{label}.{suffix}" for suffix in ("stdout", "stderr"))
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        steps.append(dict(name=label, argv=cmd, exitCode=result.returncode, startedAtUTC=start_at,
                          terminalAtUTC=utc(), stdout=pin(stdout), stderr=pin(stderr)))
        return result

    classes, changed_classes = private / "classes", private / "changed"
    fixed_first, fixed_second, alternative = [
        private / folder / name for folder, name in (
        ("fixture", "First.java"), ("fixture", "Second.java"), ("alternative", "First.java"))]
    for index, path in enumerate((fixed_first, fixed_second, alternative), 1):
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"package physicalfixture; public interface {path.stem} {{"
                        f" default int mark() {{ return {index}; }} }}\n")
    normal_compile = [javac, "--release", "25", "-proc:none", "-Xlint:all", "-Werror",
                      "-cp", deps_cp]
    assert call("compile-fixed", [*normal_compile, "-d", classes, METER.resolve(), fixed_first, fixed_second]).returncode==0
    assert call("compile-distinct", [*normal_compile, "-d", changed_classes, alternative]).returncode==0
    first, second, other = classes / f"{A}.class", classes / f"{B}.class", changed_classes / f"{A}.class"
    alias = private / "first-copy.class"
    alias.write_bytes(first.read_bytes())
    crc_a, crc_b, crc_other = [calc(p.read_bytes()) for p in (first, second, other)]
    assert crc_a!=crc_other and len({crc_a,crc_b,crc_other})==3

    def record(name, crc):
        encoded = name.encode("ascii")
        return b"\x11" + pack(">QH", crc, len(encoded)) + encoded + b"\x01\x01"

    exact = HEADER + record(A,crc_a) + record(B,crc_b)
    mismatch = HEADER + record(A,crc_a) + record(B,crc_b ^ 1)
    assert set(decode(exact, {A,B})["classes"])=={A,B}
    assert decode(HEADER,set())["totalClassRecords"]==0
    outcomes = []
    for label, payload, paths, unseen, problem in (
        ("distinct",exact,(first,second),False,None),
        ("crc-late",mismatch,(first,second),False,b"execution/class CRC mismatch"),
        ("same-path",exact,(first,first),False,b"duplicate class input"),
        ("same-bytes-different-path",exact,(first,alias),False,b"duplicate class input"),
        ("same-name-different-bytes",HEADER,(first,other),True,b"duplicate class input"),
    ):
        stream = private / f"{label}.exec"
        stream.write_bytes(payload)
        result = call(label,[java,"-cp",f"{classes}:{deps_cp}",MAIN,stream,*paths])
        rows = [r.split("\t") for r in result.stdout.decode().splitlines() if r.startswith("CLASS\t")]
        visible = [r[1] for r in rows]
        expected = 0 if problem is None else 1
        assert all((r[3]=="false")==unseen for r in rows)
        if problem is None:
            assert visible==[A,B] and result.returncode==0 and not result.stderr
            assert [r[2] for r in rows]==[f"{crc_a:016x}",f"{crc_b:016x}"]
        elif red and label!="crc-late":
            assert visible==[A,A] and result.returncode==0
            assert [r[2] for r in rows]==[f"{crc_a:016x}",f"{(crc_other if unseen else crc_a):016x}"]
        else:
            assert result.returncode==1 and visible==[A] and problem in result.stderr
        outcomes.append(dict(case=label,expectedExit=expected,actualExit=result.returncode,
                             completeMeasurementCredit=(expected==0 and result.returncode==0),
                             visible=visible,orderedClassCRC=[r[2] for r in rows],
                             stream=pin(stream),selectedClassPaths=[pin(f) for f in paths]))
    out = OPS / run
    out.mkdir()
    receipt = dict(actualExit=0,phase=phase,source=source,productionCore=context["productionCoreMain"],
        run=run,startEvent=start["eventId"],terminalAtUTC=utc(),testId="PT-OPS-EXEC-CRC-002",
        inputTool=pin(METER),standaloneSyntheticFixtures=True,cases=outcomes,steps=steps,
        reproducedDefects=sum(x["expectedExit"]!=x["actualExit"] for x in outcomes),
        callerUnionAllowed=False,productPt=0,realNative=0,coverage=None,formalDelta=0)
    (out / "manifest.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(phase,[(x["case"],x["actualExit"]) for x in outcomes])


if __name__ == "__main__":
    main(sys.argv[1])
