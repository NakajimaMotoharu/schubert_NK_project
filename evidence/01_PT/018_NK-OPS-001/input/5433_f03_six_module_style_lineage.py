"""Reconcile current six-module source formatting and Checkstyle without re-execution."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
PLAN = next((ROOT / "documents/400_PGPT/470_PMO").glob("601_*"))
OPS = ROOT / "evidence/01_PT/018_NK-OPS-001/evidence"
CHECKSTYLE = "tools/quality/static/checkstyle.xml"


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return {"path": str(path), "sha256": digest(Path(path).read_bytes())}


def read(ref):
    assert pin(ref["path"]) == ref
    return json.loads(Path(ref["path"]).read_bytes())


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=15)


def inventory(commit):
    result = {}
    for raw in git("ls-tree", "-rz", commit, "src").split(b"\0")[:-1]:
        fields, name = raw.decode().split("\t", 1)
        if "/src/main/java/" in name and name.endswith(".java"):
            result[name] = fields.split()[-1]
    return result


def main():
    start = json.loads(next(PLAN.glob("1126_F03現六*")).read_bytes())
    v = start["values"]
    refs = v["oracleReferences"]
    base, verified, expiry, cleanup = map(read, refs[1:])
    assert pin(refs[0]["path"]) == refs[0]
    assert verified["sourceOnlyProof"] == refs[1]
    previous = base["productionCore"]
    core = v["productionCoreMain"]
    assert git("rev-parse", "HEAD").decode().strip() == v["source"]
    assert not git("diff", "--name-only", core, "--", "src", "pom.xml", CHECKSTYLE)
    assert not git("diff", "--name-only", previous, core, "--", CHECKSTYLE)
    old, new = inventory(previous), inventory(core)
    assert set(old) == set(new) and len(new) == base["totalSources"] == 1027
    assert verified["checkstyleCurrentFilenames"] == verified["formatterCurrentFilenames"] == len(old)
    assert verified["sixSourceScopes"] == 6 and verified["actualExit"] == 0
    changed = {key for key in old if old[key] != new[key]}
    assert changed == {case["candidateMain"]["path"] for case in (expiry, cleanup)}
    counts = Counter(p.split("/")[1].removeprefix("schubert-nk-") for p in new)
    assert counts == base["countsByModule"]
    old_formatter = Path(next(arg for arg in base["formatCommand"] if arg.endswith("all-deps.jar")))
    records = []
    for case, static_key in [(expiry, "static"), (cleanup, "standaloneStatic")]:
        target = case["candidateMain"]
        path = target["path"]
        assert pin(path) == target and digest(git("show", f"{core}:{path}")) == target["sha256"]
        checks = case[static_key]
        formatter, checkstyle = checks["format"], checks["checkstyle"]
        assert formatter["actualExit"] == checkstyle["actualExit"] == 0
        assert str(old_formatter) in formatter["command"]
        assert {"--skip-reflowing-long-strings", "--dry-run", "--set-exit-if-changed", path}.issubset(
            formatter["command"])
        cmd = checkstyle["command"]
        assert Path(cmd[cmd.index("-c")+1]).resolve() == (ROOT / CHECKSTYLE).resolve()
        report = Path(cmd[cmd.index("-o")+1])
        xml = ET.parse(report)
        assert xml.getroot().get("version") == "14.3.0"
        names = {Path(item.get("name")).resolve() for item in xml.iter("file")}
        assert ROOT / path in names and not list(xml.iter("error"))
        records.append({"source": target, "formatterExit": 0, "checkstyleExit": 0,
                        "checkstyleReport": pin(report)})
    result = dict(actualExit=0, source=v["source"], productionCore=core, previousCore=previous,
                  startEvent=start["eventId"], terminalAtUTC=datetime.now(timezone.utc).isoformat(),
                  inputs=refs, runner=pin(Path(__file__)), currentProductMain=1027,
                  stableMain=len(new)-len(changed), moduleCounts=dict(counts), changedMain=records,
                  changedCheckstyleErrors=0, mainSourceStyleScopes=6, replayedAnalyzer=0,
                  productTestsStarted=0, heldClassfilesRead=0, fullClassfileStatic=False,
                  wholeF03=False, whole451=False, formalDelta=0)
    out = OPS / v["run"]
    out.mkdir()
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print("six scopes, 1025 identical source objects, two exact changed source style receipts")


if __name__ == "__main__":
    main()
