"""Bind the only unresolved detector candidate to the unchanged Current baseline tree."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess


EVIDENCE = Path("evidence/01_PT/018_NK-OPS-001/evidence")
BASELINE = "program/characterization/baseline/current"


def git(*argv):
    return subprocess.check_output(["git", *argv], timeout=20)


def pin(path):
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest())


def main():
    raw, = EVIDENCE.glob("PG41242-*/manifest.json")
    m = json.loads(raw.read_bytes())
    [candidate] = m["unresolved"]
    assert candidate["rule"] == "sourcegraph-access-token" and candidate["inScope"] == "combined"
    assert candidate["meaning"] is None
    initial = m["commitTrace"][0]["commit"]
    paths = git("diff", "--name-only", "-z", initial+"^", initial).decode().split("\0")[:-1]
    patch = b"\n".join(git("diff", "--no-renames", "--no-ext-diff", "--unified=0",
                       initial+"^", initial, "--", name) for name in paths if not name.endswith(".exec"))
    assert sha256(patch).hexdigest() == m["commitTrace"][0]["textPatchSha256"]
    lines = patch.splitlines()
    index = candidate["streamLine"] - 1
    prior = Path(m["previousScan"]["path"])
    owner = next(line for line in reversed(lines[:index]) if line.startswith(b"+++ b/"))
    assert owner == b"+++ b/"+str(prior).encode()
    content = re.fullmatch(rb'^\+\s*"baselineTree": "([0-9a-f]{40})",\s*$', lines[index])
    assert content
    identifier = content[1].decode()
    assert git("cat-file","-t",identifier).strip() == b"tree"
    assert m["baselineTree"] == identifier == json.loads(prior.read_bytes())["baselineTree"]
    assert git("rev-parse", f'{m["baseExclusive"]}:{BASELINE}',
               f'{m["headInclusive"]}:{BASELINE}').decode().splitlines() == [identifier, identifier]
    assert all(row["meaning"] for row in m["perPathReports"])
    result = dict(actualExit=0, terminalAtUTC=datetime.now(timezone.utc).isoformat(), source=m["source"],
                  firstScannerResult=pin(raw), priorScannerCursor=pin(prior), exactFinding=candidate,
                  verifiedObjectType="tree", classification="Exact Current characterization baseline Git tree ID",
                  currentBaselineTree=identifier, protectedBaselineMatches=True,
                  wholeRangeClassified=True, aggregateCandidates=len(m["combinedReport"]),
                  individualPathCandidates=len(m["perPathReports"]), confirmedSecrets=0, unresolved=0,
                  commits=m["commits"], uniquePaths=m["uniquePaths"],
                  syntheticPublicExecs=len(m["verifiedSyntheticExec"]),
                  reranGitleaks=False, editedScannerRules=False, privateObjectsRead=0, formalDelta=0)
    out = EVIDENCE/"PG41244-g07-current-baseline-candidate-resolved-v1"
    out.mkdir()
    target = out/"manifest.json"
    with target.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(target), result["commits"], result["uniquePaths"], result["confirmedSecrets"])


if __name__ == "__main__":
    main()
