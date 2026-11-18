"""Prove scanner hit provenance without exporting candidate values."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path.cwd()
EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
OUT = EVIDENCE / "PG39196-g07-current-published-delta-v1"
OLD = EVIDENCE / "PG38950-g07-new-published-blobs"
WORK = ROOT.parent / "pgpt-runs/PG379/pg39196-g07-current-published-delta-v1"
TC = ROOT.parent / "toolchain"
HEX = re.compile(rb"(?<![0-9A-Fa-f])[0-9a-f]{40,64}(?![0-9A-Fa-f])")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def ref(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def git(*args):
    return subprocess.check_output(["git", *args], timeout=90)


def write(path, value):
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def binary_evidence(rows, head):
    tool = TC / "org.jacoco.cli-0.8.15-nodeps.jar"
    java = TC / "jdk-25.0.4/bin/java"
    outcomes = []
    for row in rows:
        if row["treatment"] != "binary":
            continue
        path = Path(row["path"])
        local = WORK / row["relativeProjection"]
        pending = dict(path=str(path), blob=row["blobOid"], status="UNQUALIFIED")
        witness = path.with_name("manifest.json")
        if path.name != "jacoco.exec" or "post" not in path.parent.name:
            outcomes.append(pending)
            continue
        actual = json.loads(git("show", f"{head}:{witness}"))
        expected = actual.get("files", {}).get("jacoco.exec")
        if expected != row["blobSha256"] or sha(local.read_bytes()) != expected or actual.get("actualExit") != 0:
            outcomes.append(pending)
            continue
        proc = subprocess.run([str(java), "-jar", str(tool), "execinfo", str(local)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        output = proc.stdout.decode().splitlines()
        sessions = [line for line in output if line.startswith("Session ")]
        probes = [line for line in output if re.fullmatch(r"[0-9a-f]{16}\s+\d+ of\s+\d+\s+\S+", line)]
        if proc.returncode or proc.stderr or len(sessions) != 1 or actual["run"] not in sessions[0] or not probes:
            outcomes.append(pending)
            continue
        outcomes.append(dict(path=str(path), blob=row["blobOid"], role="standard JaCoCo exec",
                       derivedRows=len(probes), samePost=ref(witness), session=actual["run"],
                       actualExit=0, onlyCoverageProbeClassData=True, tool=ref(tool)))
    return outcomes


def main():
    scan = load(OUT / "scan-terminal.json")
    head = scan["throughCommit"]
    rows = load(WORK / "projection.json")
    assert sha((WORK / "projection.json").read_bytes()) == scan["projectionSha256"]
    prior = {(r["rule"], r["lineSha256"]): r["ground"] for r in load(OLD / "classified-findings.json")}
    reachable = set(git("rev-list", "--objects", "--no-object-names", head, "origin/main").splitlines())
    by_version = {(r["path"], r["blobOid"]): r for r in rows}
    verified_hashes = {}
    for r in rows:
        if r["treatment"] in {"text", "binary"}:
            for h in (r["blobSha256"], r["decodedSha256"]):
                verified_hashes[h.encode()] = dict(kind="exact published content digest", path=r["path"], object=r["blobOid"])
    result = []
    for hit in scan["findings"]:
        meta = by_version[hit["path"], hit["blob"]]
        line = (WORK / meta["relativeProjection"]).read_bytes().splitlines()[hit["line"] - 1]
        assert sha(line) == hit["lineSha256"]
        ground = prior.get((hit["rule"], hit["lineSha256"]))
        if ground:
            decision = dict(kind="exact previous adjudicated public line", prior=ref(OLD / "classified-findings.json"))
        else:
            tokens = set(HEX.findall(line))
            known = {t: (dict(kind="reachable Git object identity") if t in reachable else verified_hashes.get(t)) for t in tokens}
            decision = None
            if tokens and all(known.values()):
                decision = dict(kind="all line candidates are proved Git or content identities",
                                origins=list(known.values()))
        result.append(dict(**hit, ground=decision))
    binary = binary_evidence(rows, head)
    counts = Counter(r["ground"]["kind"] for r in result if r["ground"])
    unknown = sum(r["ground"] is None for r in result)
    write(OUT / "adjudication-first.json", result)
    write(OUT / "binary-qualification.json", binary)
    print(dict(classified=dict(counts), unresolved=unknown,
               binaryQualified=sum(x.get("actualExit") == 0 for x in binary)))
    print(Counter(Path(r["path"]).name for r in result if r["ground"] is None).most_common(12))


if __name__ == "__main__":
    main()
