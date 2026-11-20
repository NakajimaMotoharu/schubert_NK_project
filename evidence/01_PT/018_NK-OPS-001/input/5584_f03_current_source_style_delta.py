"""Bind the six changed Java source files to their existing exact formatting receipts."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
POLICY = ("pom.xml", ".mvn", "tools/quality/static/checkstyle.xml")
STYLE_PATHS = {
    "MonitoringModePolicy.java": (1, "retained", "checkstyle"),
    "WebDbPoolMetricRecorder.java": (2, "steps", "checkstyle"),
    "WebResultMapper.java": (3, "steps", "style"),
    "AlertLifecycle.java": (4, "steps", "checkstyle"),
    "AlertLifecycleTest.java": (4, "steps", "checkstyle"),
    "MonitoringPolicyEngineTest.java": (5, "steps", "checkstyle"),
}


def pin(p):
    return dict(path=str(p), sha256=sha256(p.read_bytes()).hexdigest())


def read(p):
    return json.loads(p.read_bytes())


def git(*items):
    return subprocess.check_output(["git", *items], timeout=30)


def trees(ref):
    out = {"main": {}, "test": {}}
    for row in git("ls-tree", "-rz", ref,"--","src").split(b"\0"):
        if not row:
            continue
        meta, path = row.decode().split("\t", 1)
        for key in out:
            if "/src/"+key+"/java/" in path and path.endswith(".java"):
                out[key][path] = meta.split()[-1]
    return out


def check_entries(proof, shape, check):
    use = {"format", check}
    if shape == "retained":
        out = {}
        for decision in proof["retainedSuccessfulPreparation"]:
            key = decision["step"]
            if key in use:
                ref = decision["receipt"]
                p = Path(ref["path"])
                assert pin(p) == ref
                out[key] = read(p)
    elif isinstance(proof["steps"],dict):
        out = {key: proof["steps"][key] for key in use}
    else:
        out = {row.get("stage", row.get("step", row.get("name"))): row
               for row in proof["steps"]
               if row.get("stage", row.get("step", row.get("name"))) in use}
    assert set(out) == use
    for item in out.values():
        assert item.get("actualExit", item.get("exitCode", item.get("exit"))) == 0
    return out


def main():
    s, = Path("documents/400_PGPT/470_PMO").glob("601_*/1543_*")
    start = read(s)["values"]
    head, core = start["source"], start["productionCoreMain"]
    assert git("rev-parse","HEAD","origin/dev-foundation").decode().splitlines() == [head,head]
    rows = start["oracleReferences"]
    assert [pin(Path(ref["path"])) for ref in rows] == rows
    records = [read(Path(ref["path"])) for ref in rows[1:]]
    base = records[0]
    assert all(record["actualExit"] == 0 for record in records)
    assert not git("diff", "--name-only", base["source"], head, "--", *POLICY)
    fresh = trees(head)
    old = {"main": trees(base["source"])["main"],"test": trees(base["testTree"])["test"]}
    assert fresh["main"] == trees(core)["main"]
    changes = {}
    for kind in ("main","test"):
        assert fresh[kind].keys() == old[kind].keys()
        for path, oid in fresh[kind].items():
            if oid != old[kind][path]:
                changes[path] = kind
    assert len(changes) == len(STYLE_PATHS) == 6
    checked = []
    categories = {"main": 0, "test": 0}
    for rel, mode in sorted(changes.items()):
        p = Path(rel)
        index, shape, label = STYLE_PATHS[p.name]
        record = records[index]
        commands = check_entries(record,shape,label)
        for aspect, operation in commands.items():
            args = operation["command"]
            assert any(Path(arg).name == p.name for arg in args)
            if aspect == "format":
                assert "--dry-run" in args and "--set-exit-if-changed" in args
            else:
                config = Path(args[args.index("-c") + 1])
                assert config.resolve() == Path(POLICY[-1]).resolve()
        base_commit = ((record.get("fixtureSource") or record.get("source"))
                       if mode=="test" else (record.get("source") or record.get("productionCore")))
        assert p.read_bytes() == git("show",f"{base_commit}:{rel}") == git("show",f"{head}:{rel}")
        checked.append(dict(input=pin(p), type=mode, evidence=rows[index+1],
                            exactFixtureSource=base_commit))
        categories[mode] += 1
    assert categories == {"main":4,"test":2}
    assert len(fresh["main"])==base["mainCount"]==1027
    assert len(fresh["test"])==base["testCount"]==1151
    assert base["testCheckedCount"]==1119 and base["heldTestCount"]==32
    out = OPS / start["run"]
    out.mkdir()
    m = out/"manifest.json"
    with m.open("x") as f:
        json.dump(dict(actualExit=0,source=head,productionCore=core,originalMatrix=rows[1],
                       verifiedDelta=checked,sourceTotals=dict(main=1027,tests=1151,
                                                              testCheckstyleConfirmed=1119,heldTests=32),
                       unchangedMain=1023,unchangedTests=1149,heldFileContentsRead=0,
                       staticScope="source style only",changedMain=4,changedTest=2,
                       newFormatterRuns=0,newCheckstyleRuns=0,newTestRuns=0,
                       wholeF03=False,whole451=False,formalDelta=0,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(pin(m),categories)


if __name__=="__main__":
    main()
