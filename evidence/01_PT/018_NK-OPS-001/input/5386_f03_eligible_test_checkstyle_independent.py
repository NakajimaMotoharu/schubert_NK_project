"""Verify current ordinary Checkstyle coverage from source and the saved XML."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from xml.etree import ElementTree


def pin(p):
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def verify(ref):
    path = Path(ref["path"])
    assert pin(path) == ref
    return path


def main():
    ops = Path("evidence/01_PT/018_NK-OPS-001/evidence")
    record = next(ops.glob("PG40592-*/manifest.json"))
    doc = json.loads(record.read_bytes())
    raw = json.loads(verify(doc["sourceEvidence"]).read_bytes())
    held = set(json.loads(verify(raw["priorProtections"]).read_bytes())["protectedPathsMetadataOnly"])
    unchanged, prior, fresh = (set(raw[k]) for k in ("unchangedGitBlobIds", "priorExactDelta", "newInputs"))
    assert all(not (x & y) for x, y in ((unchanged, prior), (unchanged, fresh), (prior, fresh),
                                       (held, unchanged | prior | fresh)))
    current = doc["currentSource"]
    tree = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", current, "--", "src"], text=True)
    modules = {"schubert-nk-" + name for name in ("api", "web", "batch", "bootstrap", "protocol", "storage")}
    project = {p for p in tree.splitlines()
               if p.split("/")[1] in modules and "/src/test/java/" in p and p.endswith(".java")}
    assert unchanged | prior | fresh | held == project
    assert (len(unchanged), len(prior), len(fresh), len(held)) == (1070, 23, 17, 32)

    def source_digest(path):
        assert path in (prior | fresh)
        source = subprocess.check_output(["git", "show", f"{current}:{path}"])
        return hashlib.sha256(source).hexdigest()

    for path, row in raw["priorExactDelta"].items():
        verify(row["receipt"])
        xml = ElementTree.parse(verify(row["checkstyleXml"])).getroot()
        assert not xml.findall(".//error")
        assert any(Path(element.get("name")).name == Path(path).name for element in xml.findall("file"))
        assert source_digest(path) == row["sourceSha256"]
    assert all(source_digest(path) == digest for path, digest in raw["newInputs"].items())
    live = doc["currentExecution"]
    assert live["actualExit"] == doc["actualExit"] == 0
    assert set(live["command"][-len(fresh):]) == fresh
    assert verify(live["stdout"]).stat().st_size == verify(live["stderr"]).stat().st_size == 0
    xml = ElementTree.parse(verify(live["xml"])).getroot()
    asserted_names = {str(Path(element.get("name")).resolve().relative_to(Path.cwd()))
                      for element in xml.findall("file")}
    assert asserted_names == fresh and not xml.findall(".//error")
    output = ops / "PG40594-f03-eligible-test-checkstyle-independent-v1" / "manifest.json"
    output.parent.mkdir()
    independently_matched = dict(
        actualExit=0, productionCore=doc["productionCore"], testSource=current, original=pin(record),
        total=len(project), checkstyleConfirmed=len(unchanged | prior | fresh), retainedExisting=len(unchanged | prior),
        newCheckstyleInputs=len(fresh), freshCheckstyleFindings=0, heldMetadataOnly=len(held), heldSourcesOpened=0,
        firstVerification=dict(actualExit=1, cause="absolute XML path compared to a relative input path",
                               childJobsStarted=0),
        compilerOrProductTestExecutions=0, wholeF03Accepted=False, whole451Accepted=False,
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),
    )
    with output.open("x") as fp:
        json.dump(independently_matched, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
    print(pin(output))


if __name__ == "__main__":
    main()
