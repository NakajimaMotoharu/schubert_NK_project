"""Confirm the shared decoder's old test contract and three original archived streams."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys


t = runpy.run_path(str(Path(__file__).with_name("5633_p01808_original_complete_binary_names.py")))
OPS, DECODER, pin, read, decoder = (t[k] for k in ("OPS", "DECODER", "pin", "read", "decoder"))


def main():
    red, = OPS.glob("PG41236-*/manifest.json")
    green, = OPS.glob("PG41238-*/manifest.json")
    old_m, fixed_m = read(red), read(green)
    assert old_m["unexpectedAccepts"] == 3 and fixed_m["unexpectedAccepts"] == 0
    old_body, old = decoder(old_m["source"])
    cur_body, current = decoder(fixed_m["source"])
    assert pin(DECODER)["sha256"] == fixed_m["exactDecoderSha256"] == sha256(cur_body).hexdigest()
    assert sha256(old_body).hexdigest() == old_m["exactDecoderSha256"]
    prior, = OPS.glob("PG41160-*/manifest.json")
    streams = [record["originalExec"] for record in read(prior)["results"]]
    range_unit, = OPS.glob("PG41204-*/manifest.json")
    unit = read(range_unit)
    source_exec, = [row for row in unit["originals"] if row["path"].endswith("/unit.exec")]
    public_exec = range_unit.parent/"unit.exec"
    assert pin(public_exec)["sha256"] == source_exec["sha256"]
    streams.append(pin(public_exec))
    equal = []
    for index, reference in enumerate(streams):
        stream = Path(reference["path"])
        assert pin(stream) == reference
        selection = {"dev/codex/schubert/nk/web/media/HttpByteRangeParser"} if index == 2 else set()
        blob = stream.read_bytes()
        before = old["decode"](blob, selection)
        after = current["decode"](blob, selection)
        assert after == before and after["totalClassRecords"] > 0 and len(after["sessions"]) == 1
        assert pin(stream) == reference
        equal.append(dict(original=reference, selected=sorted(selection),
                          exactCountersAndSessionsMatch=True, classRecords=after["totalClassRecords"]))
    prefixes = ["tools/**/*.py", "evidence/01_PT/018_NK-OPS-001/input/*.py"]
    reference_cmd = ["git","grep","-l","-F","jacoco_readonly_exec_subset",fixed_m["source"],"--",*prefixes]
    tracked = subprocess.check_output(reference_cmd, text=True, timeout=20).splitlines()
    consumers = [path.split(":",1)[1] for path in tracked]
    assert len(consumers) == len(set(consumers))
    assert str(DECODER.with_name("jacoco_readonly_exec_subset_presence_test.py")) in consumers
    test_cmd = [sys.executable,"-B","-m","unittest","discover","-s","tools/quality",
                "-p","jacoco_readonly_exec_subset*_test.py"]
    unit_p = subprocess.run(test_cmd, capture_output=True, check=True, timeout=25)
    summary = [line for line in unit_p.stderr.decode().splitlines() if line.startswith("Ran ")]
    assert len(summary)==1 and unit_p.stderr.decode().strip().endswith("OK")
    count = int(summary[0].split()[1])
    assert count > 8
    pyflakes = Path("../toolchain/pyflakes-3.4.0/runtime").resolve()
    static_cmd = [sys.executable,"-B","-m","pyflakes",str(DECODER),str(Path(__file__)),
                  str(Path(__file__).with_name("5633_p01808_original_complete_binary_names.py"))]
    lint = subprocess.run(static_cmd,env=dict(os.environ,PYTHONPATH=str(pyflakes)),
                          capture_output=True,check=True,timeout=20)
    assert not lint.stdout and not lint.stderr
    out = OPS/"PG41240-p01808-independent-global-names-post-v1"
    out.mkdir()
    refs = out/"tracked-reference-scope.txt"
    refs.write_text("\n".join(consumers)+"\n")
    data = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                source=fixed_m["source"], core=fixed_m["productionCore"], tool=pin(DECODER),
                baseline=pin(red), corrected=pin(green), oldStrictJavaAndGenuineInputs=pin(prior),
                exactGenuinePasses=equal, explicitScope=pin(refs), referenceCommand=reference_cmd,
                referencingPythonInputs=len(consumers), oldReadonlyToolTests=count,
                toolJUnitOrProductOperations=0, actualProcessOrArchiveStateChanges=0,
                commands=[dict(command=test_cmd,exit=unit_p.returncode,
                               summary=summary[0],stderrSha256=sha256(unit_p.stderr).hexdigest()),
                          dict(command=static_cmd,exit=lint.returncode,findings=0)],
                whole451=False, independentOriginalStreamOnly=True, formalDelta=0)
    path = out/"manifest.json"
    with path.open("x") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(pin(path), count, len(consumers), [row["classRecords"] for row in equal])


if __name__ == "__main__":
    main()
