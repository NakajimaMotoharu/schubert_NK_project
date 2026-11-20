"""Compare the raw Java loader to independently constructed single-stream controls."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from struct import pack
import subprocess
import sys
from tempfile import TemporaryDirectory


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
METER = Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
BIN = Path("../toolchain/jdk-25.0.4/bin").resolve()
HEADER = bytes.fromhex("01c0c01007")
FLAG = "--strict-original-exec"
NAME = "originalfixture/One"
DECODE = "dba164629c:tools/quality/jacoco_readonly_exec_subset.py"
CLASS = "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement"


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return sha256(raw).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args], timeout=15)


def read(path):
    return json.loads(path.read_bytes())


def class_id(data):
    assert data.startswith(bytes.fromhex("cafebabe")) and data[6:8] == bytes.fromhex("0045")
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xd800000000000000 if crc & 1 else 0)
    return crc


def session(label, start, end):
    return b"\x10" + pack(">H", len(label)) + label + pack(">qq", start, end)


def entry(checksum, hit):
    name = NAME.encode()
    return b"\x11" + pack(">QH", checksum, len(name)) + name + bytes((1, hit))


def main(after):
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1531_*")
    proposed = read(start)
    context = proposed["values"]
    source = git("rev-parse", "HEAD").decode().strip() if after else context["source"]
    contents = git("show", f"{source}:{METER}")
    assert (pin(METER) == context["oracleReferences"][-1]) is (not after)
    assert all(pin(Path(r["path"])) == r for r in context["oracleReferences"][:-1])
    assert not git("diff", "--name-only", context["source"], source, "--", "src")
    assert not git("diff", "--name-only", context["productionCoreMain"], source, "--",
                   ":(glob)src/**/src/main/**")
    expected_libs, = OPS.glob("PG31432-*/compile.json")
    dependencies = read(expected_libs)["dependencies"]
    assert all(pin(Path(d["path"])) == d for d in dependencies)
    cp = os.pathsep.join(r["path"] for r in dependencies)
    decoded = git("show", DECODE)
    library = {}
    exec(compile(decoded, DECODE, "exec"), library)
    decode = library["decode"]
    run_id = "PG41084-p01808-original-exec-strict-after-v1" if after else context["run"]
    out = OPS / run_id
    out.mkdir()
    results = []
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-original-exec-fixture-") as tmp:
        base = Path(tmp)
        artifact = base / METER.name
        artifact.write_bytes(contents)
        java_file = base / "One.java"
        java_file.write_text("package originalfixture; public interface One { default int value() { return 7; } }\n")
        built = base / "built"
        compiler = [BIN/"javac", "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                    "-cp", cp, "-d", built, artifact, java_file]
        r = subprocess.run(compiler,capture_output=True,timeout=30)
        assert r.returncode == 0, r.stderr
        target = built / (NAME + ".class")
        checksum = class_id(target.read_bytes())
        one = session(b"RUN", 1, 2)
        other = session(b"OTHER", 2, 3)
        covered, uncovered = entry(checksum, 1), entry(checksum, 0)
        original = HEADER + one + covered
        shapes = (
            ("valid-original", original, {NAME}, None),
            ("valid-original-unmatched", HEADER + one, set(), None),
            ("repeated-id", HEADER + one + uncovered + covered, {NAME}, b"duplicate execution class ID"),
            ("multiple-sessions", HEADER + one + other + covered, {NAME}, b"single ordered execution session"),
            ("header-appended", original + HEADER, {NAME}, b"duplicate execution header"),
            ("session-missing", HEADER + covered, {NAME}, b"single ordered execution session"),
            ("negative-epoch", HEADER + session(b"RUN", -1, 2) + covered, {NAME}, b"single ordered execution session"),
            ("reversed-time", HEADER + session(b"RUN", 4, 2) + covered, {NAME}, b"single ordered execution session"),
        )
        for tag, raw, want, rejection in shapes:
            stream = base / (tag+".exec")
            stream.write_bytes(raw)
            decoded_ok = True
            try:
                decode(raw, want)
            except ValueError:
                decoded_ok = False
            assert decoded_ok is (rejection is None)
            flags = [FLAG] if after else []
            if after and tag == "valid-original-unmatched":
                flags.append("--line-deficits")
            cmd = [BIN/"java", "-cp", f"{built}:{cp}", CLASS, *flags, stream, target]
            result = subprocess.run(cmd,capture_output=True,timeout=30)
            visible = [line.split("\t") for line in result.stdout.decode().splitlines()
                       if line.startswith("CLASS\t")]
            if after and rejection is not None:
                assert result.returncode == 1 and not visible and rejection in result.stderr
            else:
                hit = tag != "valid-original-unmatched"
                assert result.returncode == 0 and len(visible) == 1
                assert visible[0][1:4] == [NAME, f"{checksum:016x}", str(hit).lower()]
                if after and not hit:
                    assert b"DEFICIT\t" in result.stdout
            compatibility = None
            if after and rejection is not None:
                prior = subprocess.run([BIN/"java", "-cp", f"{built}:{cp}", CLASS, stream, target],
                                       capture_output=True,timeout=30)
                assert prior.returncode == 0
                compatibility = dict(exit=prior.returncode, stdoutSha256=sha(prior.stdout))
            results.append(dict(case=tag, requiredOriginalExit=int(rejection is not None),
                                actualExit=result.returncode, emittedClassRows=len(visible),
                                independentDecoderValid=decoded_ok, optionalLegacyResult=compatibility,
                                diagnostic=(rejection.decode() if after and rejection else None),
                                command=list(map(str,cmd)), inputSha256=sha(raw),
                                fixtureClassSha256=sha(target.read_bytes()), crc64=f"{checksum:016x}",
                                stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr)))
    receipt = out / "manifest.json"
    with receipt.open("x") as stream:
        json.dump(dict(actualExit=0, toolSource=source, toolSourceSha256=sha(contents),
                       productionCore=context["productionCoreMain"], run=run_id,
                       originalMode=after, caseCount=len(results), cases=results,
                       previousPublishedRule=context["oracleReferences"][1],
                       byteFixturesOnly=True, observedUnderRejection=sum(
                           c["actualExit"] != c["requiredOriginalExit"] for c in results),
                       independentDecoderSourceSha256=sha(decoded), admissionOrNativeActions=0,
                       productTests=0, countedCoverage=None, formalDelta=0, terminalAtUTC=utc()), stream,
                  indent=2,ensure_ascii=False)
        stream.write("\n")
    print(pin(receipt), [(i["case"], i["actualExit"]) for i in results])


if __name__ == "__main__":
    main({"before": False, "after": True}[sys.argv[1]])
