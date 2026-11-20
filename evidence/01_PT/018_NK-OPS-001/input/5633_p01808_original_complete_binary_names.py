"""Prove original-stream binary name uniqueness independent of target selection."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
DECODER = Path("tools/quality/jacoco_readonly_exec_subset.py")
HEAD = bytes.fromhex("01c0c01007")
SESSION = bytes.fromhex("10000352554e00000000000000010000000000000002")
FIRST = "fixture/Target"
OTHER = "fixture/Other"


def pin(path):
    return {"path":str(path), "sha256":sha256(path.read_bytes()).hexdigest()}


def read(path):
    return json.loads(path.read_bytes())


def show(source, path):
    return subprocess.check_output(["git", "show", f"{source}:{path}"], timeout=15)


def numbered(identity, name):
    encoded = name.encode("ascii")
    return b"\x11" + identity.to_bytes(8, "big") + len(encoded).to_bytes(2, "big") + encoded + b"\x01\x01"


def fixtures():
    first, other, repeat = numbered(17, FIRST), numbered(18, OTHER), numbered(19, OTHER)
    return (
        ("canonical-selected", HEAD+SESSION+first+other, {FIRST}, "accept"),
        ("same-name-selected", HEAD+SESSION+first+numbered(20, FIRST), {FIRST}, "duplicate-name"),
        ("duplicate-id-different-name", HEAD+SESSION+first+numbered(17, OTHER), {FIRST}, "duplicate-id"),
        ("unselected-same-name", HEAD+SESSION+first+other+repeat, {FIRST}, "duplicate-name"),
        ("unselected-same-name-reverse-order", HEAD+SESSION+repeat+first+other, {FIRST}, "duplicate-name"),
        ("empty-selection-still-enforces-unique-names", HEAD+SESSION+other+repeat, set(), "duplicate-name"),
        ("case-sensitive-different-names", HEAD+SESSION+first+other+numbered(20, "fixture/other"), {FIRST}, "accept"),
        ("canonical-no-production-classes", HEAD+SESSION, set(), "accept"),
    )


def decoder(revision):
    body = show(revision, DECODER)
    module = {}
    exec(compile(body, DECODER.as_posix(), "exec"), module)
    return body, module


def observe(decode, body, selected):
    try:
        result = decode(body, selected)
    except ValueError as error:
        message = str(error)
        if "identity" in message or "binary name" in message:
            status = "duplicate-name"
        elif "duplicate class record" in message:
            status = "duplicate-id"
        else:
            raise
        return status, None
    assert result["sessions"][0]["labelBytesHex"] == "52554e"
    assert set(result["classes"]) == selected
    if FIRST in selected:
        assert result["classes"][FIRST]["hitProbeIds"] == [0]
        assert result["classes"][FIRST]["crc64"] == "11"
    return "accept", result["totalClassRecords"]


def main(after):
    group, = Path("documents/400_PGPT/470_PMO").glob("601_*/1655_*.json")
    plan = read(group)["values"]
    for row in plan["oracleReferences"]:
        p = Path(row["path"])
        assert (sha256(show(plan["source"], p)).hexdigest() == row["sha256"] if p == DECODER else pin(p) == row)
    tested = subprocess.check_output(["git","rev-parse","HEAD"], text=True, timeout=12).strip() if after else plan["source"]
    original, old = decoder(plan["source"])
    body, new = decoder(tested)
    assert (original != body) == after
    assert not subprocess.check_output(["git","diff","--name-only",plan["source"],tested,"--","src"],timeout=12)
    cases = []
    for index, (label, raw, names, expected) in enumerate(fixtures(), 1):
        actual, count = observe(new["decode"], raw, names)
        cases.append(dict(testId=f"PT-OPS-EXEC-NAMES-{index:03}", label=label, expected=expected,
                          actual=actual, sha256=sha256(raw).hexdigest(), selected=sorted(names),
                          actualRecords=count))
    mismatches = [row["label"] for row in cases if row["expected"] != row["actual"]]
    assert mismatches == ([] if after else ["unselected-same-name", "unselected-same-name-reverse-order",
                                            "empty-selection-still-enforces-unique-names"])
    previous_count = new["selftest"]()
    assert previous_count == 12
    prior_java = read(Path(plan["oracleReferences"][1]["path"]))
    assert prior_java["actualExit"] == 0
    out = OPS/("PG41238-p01808-independent-global-names-fixed-v1" if after else
               "PG41236-p01808-independent-global-names-baseline-v1")
    out.mkdir()
    result = out/"manifest.json"
    receipt = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), source=tested,
        productionCore=plan["productionCoreMain"], exactDecoderSha256=sha256(body).hexdigest(),
        priorDecoderSha256=sha256(original).hexdigest(), group=pin(group), declaredVectors=8, priorSelftest=12,
        observations=cases, unexpectedAccepts=len(mismatches), intendedBaseReproduced=not after,
        actualProductOrExternalOperations=0, whole451=False, formalDelta=0)
    with result.open("x") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(result), mismatches)


if __name__ == "__main__":
    main({"before":False, "after":True}[sys.argv[1]])
