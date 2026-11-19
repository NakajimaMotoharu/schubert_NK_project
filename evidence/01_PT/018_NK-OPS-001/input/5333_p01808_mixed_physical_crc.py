"""A late CRC mismatch must leave a multi-class measurement unsuccessful."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
from struct import pack
import subprocess
from tempfile import TemporaryDirectory

EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
TOOLS = Path("tools/quality")
NAMES = ("physicalfixture/First", "physicalfixture/Second")
MAIN = "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def crc64_java25(blob):
    assert blob[:8] == bytes.fromhex("cafebabe00000045")
    value = 0
    for byte in blob:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0xd800000000000000 if value & 1 else 0)
    return value


def record(name, identity):
    raw = name.encode("ascii")
    return b"\x11" + pack(">QH", identity, len(raw)) + raw + b"\x01\x01"


def main():
    checkpoint = next(Path("documents/400_PGPT/470_PMO").glob("601*/718_*.json"))
    start = json.loads(checkpoint.read_bytes())
    values = start["values"]
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert source == values["source"]
    decoder, measurement = (Path(item["path"]) for item in values["toolReferences"])
    assert [ref(decoder), ref(measurement)] == values["toolReferences"]
    decode = runpy.run_path(str(decoder))["decode"]
    historical = json.loads(next(EVIDENCE.glob("PG31434-*/manifest.json")).read_bytes())
    compile_ref = historical["compile"]
    compile_evidence = Path(compile_ref["path"])
    assert ref(compile_evidence) == compile_ref
    dependencies = json.loads(compile_evidence.read_bytes())["dependencies"]
    assert len(dependencies) == 4 and [ref(Path(item["path"])) for item in dependencies] == dependencies
    build_manifest = json.loads(next(EVIDENCE.glob("PG39862-*/manifest.json")).read_bytes())
    java = Path(build_manifest["maven"]["command"][0]).parents[6] / "jdk-25.0.4/bin/java"
    assert java.is_file() and ref(java)["sha256"] == build_manifest["tools"]["javaSha256"]
    javac = java.with_name("javac")
    started = datetime.now(timezone.utc)
    source_bytes = {}
    with TemporaryDirectory(prefix="pg40268-crc-fixture-") as scratch:
        root = Path(scratch)
        classes = root / "classes"
        classes.mkdir()
        fixtures = []
        for index, name in enumerate(NAMES, 1):
            simple = name.split("/")[-1]
            p = root / (simple + ".java")
            p.write_text(f"package physicalfixture; public interface {simple} "
                         f"{{ default int mark() {{ return {index}; }} }}\n")
            source_bytes[name] = sha(p.read_bytes())
            fixtures.append(p)
        deps = ":".join(item["path"] for item in dependencies)
        command = [str(javac), "--release", "25", "-proc:none", "-Xlint:all", "-Werror",
                   "-cp", deps, "-d", str(classes), str(measurement), *map(str, fixtures)]
        compiled = subprocess.run(command, capture_output=True, check=True, timeout=40)
        assert not compiled.stdout and not compiled.stderr
        targets = [classes / (name + ".class") for name in NAMES]
        original_hashes = [ref(path)["sha256"] for path in targets]
        ids = dict(zip(NAMES, (crc64_java25(path.read_bytes()) for path in targets), strict=True))
        assert len(set(ids.values())) == 2
        header = bytes.fromhex("01c0c01007 10 0003 52554e 0000000000000001 0000000000000002")
        passes = header + b"".join(record(name, ids[name]) for name in NAMES)
        other_id = ids[NAMES[1]] ^ 1
        assert other_id not in ids.values()
        late_failure = header + record(NAMES[0], ids[NAMES[0]]) + record(NAMES[1], other_id)
        expected = {name: f"{value:016x}" for name, value in ids.items()}
        results = []
        for key, payload, expected_exit in (("two-exact", passes, 0), ("second-crc-mismatch", late_failure, 1)):
            stream = root / (key + ".exec")
            stream.write_bytes(payload)
            parsed = decode(payload, set(NAMES))
            observed = {name: value["crc64"].zfill(16) for name, value in parsed["classes"].items()}
            assert set(observed) == set(expected)
            assert (observed == expected) == (expected_exit == 0)
            argv = [str(java), "-cp", str(classes) + ":" + deps, MAIN, str(stream), *map(str, targets)]
            result = subprocess.run(argv, capture_output=True, timeout=20)
            assert result.returncode == expected_exit
            rows = [line.split("\t") for line in result.stdout.decode().splitlines()
                    if line.startswith("CLASS\t")]
            assert all(row[2] == expected[row[1]] and row[3:5] == ["true", "1"] for row in rows)
            visible = [row[1] for row in rows]
            if expected_exit == 0:
                assert not result.stderr and visible == list(NAMES)
            else:
                assert b"execution/class CRC mismatch" in result.stderr and visible == [NAMES[0]]
            results.append(dict(case=key, actualExit=result.returncode, expectedExit=expected_exit,
                                visibleClassRows=visible, wholeSyntheticMeasurement=(expected_exit == 0),
                                inputExecSha256=sha(payload), classIdsSeenByStrictReader=observed,
                                stdoutSha256=sha(result.stdout), stderrSha256=sha(result.stderr)))
        assert original_hashes == [sha(path.read_bytes()) for path in targets]
    out = EVIDENCE / "PG40268-p01808-mixed-physical-crc-v1"
    out.mkdir()
    report = dict(actualExit=0, source=source, productionCore=values["productionCoreMain"],
                  testId="PT-OPS-EXEC-CRC-001", compileExit=0, java=ref(java), javac=ref(javac),
                  dependencies=dependencies, tools=values["toolReferences"],
                  explicitClassNames=list(NAMES), expectedIndependentCrc=expected,
                  fixtureSourceHashes=source_bytes, fixtureClassHashes=dict(zip(NAMES, original_hashes, strict=True)),
                  executions=results, originalMeasurementCasesReexecuted=0,
                  productTests=0, actualNativeActions=0, codeCoverage=None, newFormalAcceptance=0,
                  command=f"python3 -B {__file__}", verifier=ref(Path(__file__)),
                  startedAtUTC=started.isoformat(), terminalAtUTC=datetime.now(timezone.utc).isoformat())
    result_path = out / "manifest.json"
    result_path.write_text(json.dumps(report, indent=2) + "\n")
    print(ref(result_path))


if __name__ == "__main__":
    main()
