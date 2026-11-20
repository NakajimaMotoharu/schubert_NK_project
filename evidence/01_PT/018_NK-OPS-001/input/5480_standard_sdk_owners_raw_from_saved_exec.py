"""Read the retained exact exec from PG40904 using the pinned positional raw tool."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import subprocess
import tempfile


def sha(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


evidence = Path("evidence/01_PT/018_NK-OPS-001/evidence")
prior_path = next(evidence.glob("PG40904-*/manifest.json"))
prior = json.loads(prior_path.read_bytes())
assert prior["actualExit"] == prior["steps"]["unfiltered"]["exit"] == 1
assert prior["steps"]["unit"]["exit"] == prior["steps"]["default"]["exit"] == 0
assert len(prior["tests"]) == 51 and all(case["outcome"] == "passed" for case in prior["tests"])
assert prior["productBuildByteMatched"] and prior["ownSyntheticExecPrivate"]
exec_file = Path(prior["ownSyntheticExecPrivate"]["path"])
assert pin(exec_file) == prior["ownSyntheticExecPrivate"]
typed_path = next(evidence.glob("PG40880-*/public-manifest.json"))
typed = json.loads(typed_path.read_bytes())
assert typed["source"] == prior["source"]
paths = [exec_file.parent / Path(name).name for name in typed["changedClasses"]]
typed_hashes = {row["classPath"]: row["sha256"] for row in typed["physicalInventory"]}
assert len(paths) == 3 and all(pin(path)["sha256"] == typed_hashes[name]
                               for path, name in zip(paths, typed["changedClasses"], strict=True))
default_report = Path(prior["defaultCoverage"]["path"])
assert pin(default_report) == prior["defaultCoverage"]
default_root = ET.parse(default_report).getroot()
expected_session = "PG40904-CURRENT-THREE-STANDARD-SDK-OWNERS"
assert [node.attrib["id"] for node in default_root.findall("sessioninfo")] == [expected_session]

before_args = prior["steps"]["unfiltered"]["command"]
assert before_args[4] == "--line-deficits"
raw_tool = "tools/quality/jacoco/UnfilteredCodeMeasurement.java"
raw_bytes = subprocess.check_output(["git", "show", "c5674055a6:" + raw_tool], timeout=20)
assert sha(raw_bytes) == prior["unfilteredToolSha256"]
assert b"--line-deficits" not in raw_bytes
compile_prior = prior["steps"]["rawCompile"]["command"]
libs = compile_prior[compile_prior.index("-cp") + 1]
assert all(Path(path).is_file() for path in libs.split(":"))
out = evidence / "PG40906-f03-standard-sdk-owners-saved-unfiltered-v1"
out.mkdir()
with tempfile.TemporaryDirectory(dir="/dev/shm", prefix="pg40906-") as temp:
    place = Path(temp)
    source = place / "UnfilteredCodeMeasurement.java"
    source.write_bytes(raw_bytes)
    compiler = [*compile_prior[:compile_prior.index("-d")], "-d", str(place), str(source)]
    prep = subprocess.run(compiler, capture_output=True, timeout=40, check=True)
    command = [before_args[0], "-cp", f"{place}:{libs}", before_args[3], str(exec_file), *map(str, paths)]
    raw = subprocess.run(command, capture_output=True, timeout=60, check=True)
    table = out / "unfiltered.tsv"
    table.write_bytes(raw.stdout)
    row_classes = []
    for line in raw.stdout.decode().splitlines():
        fields = line.split("\t")
        if fields[0] != "CLASS":
            continue
        assert fields[3] == "true"
        counters = {}
        for token in fields[6:]:
            key, missed, covered = token.split(":")
            counters[key] = {"missed": int(missed), "covered": int(covered)}
        row_classes.append(dict(className=fields[1], crc64=fields[2], probes=int(fields[4]), counters=counters))
    assert {row["className"] + ".class" for row in row_classes} == set(typed["changedClasses"])
manifest = out / "manifest.json"
record = dict(actualExit=0, currentCore=prior["source"], before=pin(prior_path), sameExactExec=pin(exec_file),
              session=expected_session, measuredClasses=row_classes, allRawMissedZero=all(
                  item["missed"] == 0 for row in row_classes for item in row["counters"].values()),
              compileCommand=compiler, compileExit=prep.returncode, rawCommand=command, rawExit=raw.returncode,
              rawOutput=pin(table), defaultReport=pin(default_report), chosenClassFiles=[pin(path) for path in paths],
              actualProductReruns=0, existingUnitTests=51, actualExternalActions=0, whole451=False,
              formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat())
manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(pin(manifest), record["allRawMissedZero"], len(row_classes))
