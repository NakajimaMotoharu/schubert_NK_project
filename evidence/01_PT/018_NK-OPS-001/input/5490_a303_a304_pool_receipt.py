"""Relate retained memory-pool tests to the unchanged source and declared dependencies."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def at(commit, path):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], timeout=10)


ns = {"m": "http://maven.apache.org/POM/4.0.0"}


def profile(revision, module):
    parent = ET.fromstring(at(revision, Path("pom.xml")))
    pom_path = Path("src") / f"schubert-nk-{module}" / "pom.xml"
    pom = ET.fromstring(at(revision, pom_path))
    return dict(
        java=parent.findtext("m:properties/m:maven.compiler.release", namespaces=ns),
        jspecify=parent.findtext("m:properties/m:jspecify.version", namespaces=ns),
        hikari=pom.findtext("m:properties/m:hikaricp.version", namespaces=ns),
        slf4j=parent.findtext("m:dependencyManagement/m:dependencies/m:dependency"
                              "[m:artifactId='slf4j-api']/m:version", namespaces=ns))


pmo = Path("documents/400_PGPT/470_PMO")
group = json.loads(next(pmo.glob("601_*/1346_*")).read_bytes())
ctx = group["values"]
refs = ctx["oracleReferences"]
assert all(pin(Path(ref["path"])) == ref for ref in refs)
original = json.loads(Path(refs[1]["path"]).read_bytes())
method_join = json.loads(Path(refs[2]["path"]).read_bytes())
assert original["actualExit"] == 0 and original["tests"] == 2
assert original["branchRatio"] is None
assert method_join["actualExit"] == 0 and not method_join["originalRunRepeated"]
assert not method_join["actualDatabaseOrLiveHttpQualified"]
core = ctx["productionCoreMain"]
roles = [("api", "Api", "A3-03", "WBS-P004-05", "OPS-POOL-OWN-001"),
         ("web", "Web", "A3-04", "WBS-P018-06", "OPS-POOL-OWN-002")]
selected = []
for module, title, work, owner, test_id in roles:
    declared = profile(core, module)
    assert declared == profile(original["source"], module)
    assert declared == dict(java="25", jspecify="1.0.1", hikari="7.1.0", slf4j="2.0.18")
    main, = (Path(path) for path in original["inputHashes"] if path.endswith(f"/{title}JdbcPool.java"))
    fixture, = (Path(path) for path in original["inputHashes"]
                if path.endswith(f"/{title}PoolSourceOwnershipPortTest.java"))
    assert sha(at(core, main)) == original["inputHashes"][str(main)] == pin(main)["sha256"]
    assert sha(at(ctx["source"], fixture)) == original["inputHashes"][str(fixture)] == pin(fixture)["sha256"]
    name, = (name for name in original["physical"] if name.endswith(f"/{title}JdbcPool"))
    selected.append(dict(workId=work, owner=owner, testId=test_id, main=pin(main), fixture=pin(fixture),
                         sameDeclaredDependencies=declared, originalBinarySha256=original["physical"][name],
                         currentBinaryCompared=False, originalRecordsReused=1, currentRuns=0))
out = Path(refs[1]["path"]).parent.parent / ctx["run"]
out.mkdir()
result = dict(actualExit=0, source=core, originalSource=original["source"], startEvent=group["eventId"],
              terminalAtUTC=datetime.now(timezone.utc).isoformat(),
              originalUnit=refs[1], originalMethodOracle=refs[2], selected=selected,
              originalPricePp=0, priceCompletedPp=0, oldTestsRerun=0, newTestsRun=0,
              realDatabaseQualified=False, entireEffectiveDependencyGraphQualified=False,
              wholeF02=False, whole451=False, formalDelta=0)
(out / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
