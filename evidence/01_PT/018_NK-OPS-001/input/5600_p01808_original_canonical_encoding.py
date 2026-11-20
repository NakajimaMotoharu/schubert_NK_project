"""Pin strict execution-data encoding to literal fixtures and an independent decoder."""

from datetime import datetime, timezone
from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory
import json
import os
import runpy
import subprocess
import sys


helper = runpy.run_path(str(Path(__file__).with_name("5593_p01808_original_name_binding.py")))
OPS, METER, BIN, HEADER, FLAG, NAME, CLASS = (
    helper[name] for name in ("OPS", "METER", "BIN", "HEADER", "FLAG", "NAME", "CLASS")
)
pin, read, sha, git, class_id, session = (
    helper[name] for name in ("pin", "read", "sha", "git", "class_id", "session")
)


def main(after):
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1585_*.json")
    context = read(start)["values"]
    source = git("rev-parse", "HEAD").decode().strip() if after else context["source"]
    before = context["oracleReferences"][-1]["sha256"]
    tool = git("show", f"{source}:{METER}")
    assert (sha(tool) != before) is after
    assert not git("diff", "--name-only", context["source"], source, "--", "src")
    oracle_path = Path("tools/quality/jacoco_readonly_exec_subset.py")
    assert pin(oracle_path) == context["oracleReferences"][-2]
    decode = runpy.run_path(str(oracle_path))["decode"]
    expected_libs, = OPS.glob("PG31432-*/compile.json")
    dependencies = read(expected_libs)["dependencies"]
    assert all(pin(Path(row["path"])) == row for row in dependencies)
    classpath = os.pathsep.join(row["path"] for row in dependencies)
    run_name = "PG41158-p01808-canonical-original-green-v1" if after else context["run"]
    output = OPS / run_name
    output.mkdir()
    results = []
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-canonical-exec-fixture-") as directory:
        work = Path(directory)
        tool_file = work / METER.name
        tool_file.write_bytes(tool)
        fixture = work / "One.java"
        fixture.write_text("package originalfixture; public interface One { default int value() { return 7; } }\n")
        classes = work / "classes"
        compile_command = [BIN / "javac", "--release", "25", "-Xlint:all", "-Werror", "-proc:none",
                           "-cp", classpath, "-d", classes, tool_file, fixture]
        compiler = subprocess.run(compile_command, capture_output=True, timeout=30, check=True)
        target = classes / f"{NAME}.class"
        crc = class_id(target.read_bytes())
        name = NAME.encode("ascii")
        record = b"\x11" + pack(">QH", crc, len(name)) + name
        valid_session = session(b"RUN\xc0\x80", 1, 2)
        prefix = HEADER + valid_session + record
        shapes = (
            ("canonical", prefix + b"\x01\x01", True, True),
            ("canonical-session-only", HEADER + valid_session, True, False),
            ("overlong-probe-count", prefix + b"\x81\x00\x01", False, True),
            ("nonzero-probe-padding", prefix + b"\x01\x81", False, True),
            ("literal-nul-in-session-label", HEADER + session(b"RUN\x00", 1, 2) + record + b"\x01\x01", False, True),
        )
        for key, original, expected_acceptance, recorded_class in shapes:
            try:
                summary = decode(original, {NAME} if recorded_class else set())
            except ValueError:
                assert not expected_acceptance
            else:
                assert expected_acceptance
                if recorded_class:
                    assert summary["classes"][NAME]["hitProbeIds"] == [0]
            stream = work / (key + ".exec")
            stream.write_bytes(original)
            base = [BIN / "java", "-cp", f"{classes}:{classpath}", CLASS]
            cmd = [*base, FLAG, stream, target]
            executed = subprocess.run(cmd, capture_output=True, timeout=30, check=False)
            class_rows = [row.split(b"\t") for row in executed.stdout.splitlines() if row.startswith(b"CLASS\t")]
            if after and not expected_acceptance:
                assert executed.returncode == 1 and executed.stdout == b""
                assert b"noncanonical original execution stream" in executed.stderr
                legacy = subprocess.run([*base, stream, target], capture_output=True, timeout=30, check=True)
                assert legacy.stdout.startswith(b"CLASS\t" + name + b"\t")
                compatibility_exit = legacy.returncode
            else:
                assert executed.returncode == 0 and len(class_rows) == 1
                assert class_rows[0][1:4] == [name, f"{crc:016x}".encode(), str(recorded_class).lower().encode()]
                compatibility_exit = None
            results.append(dict(case=key, sha256=sha(original), independentAccepts=expected_acceptance,
                                expectedExit=int(not expected_acceptance), actualExit=executed.returncode,
                                emittedClassRows=len(class_rows), legacyExit=compatibility_exit,
                                stdoutSha256=sha(executed.stdout), stderrSha256=sha(executed.stderr),
                                command=list(map(str,cmd))))
        assert len(results) == 5
        receipt = output / "manifest.json"
        with receipt.open("x") as handle:
            json.dump(dict(run=run_name, actualExit=0 if after else 1, toolSource=source,
                           toolSourceSha256=sha(tool), fixturesOnly=True, oracle=pin(oracle_path),
                           compiledFixtureSha256=sha(target.read_bytes()), compileExit=compiler.returncode,
                           compiler=list(map(str,compile_command)), cases=results,
                           unexpected=sum(r["expectedExit"] != r["actualExit"] for r in results),
                           productTests=0, nativeProcesses=0, countedCoverage=None, formalDelta=0,
                           terminalAtUTC=datetime.now(timezone.utc).isoformat(), testId="PT-OPS-EXEC-CRC-005"),
                      handle, indent=2)
            handle.write("\n")
    print(pin(receipt), [(r["case"],r["actualExit"]) for r in results])


if __name__ == "__main__":
    main({"before": False, "after": True}[sys.argv[1]])
