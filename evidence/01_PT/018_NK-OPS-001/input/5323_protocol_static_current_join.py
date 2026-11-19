"""Join the published Protocol static receipts to the current production inputs and JAR."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import stat
import subprocess
from zipfile import ZipFile


OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
PROTOCOL = "src/schubert-nk-protocol"
CONFIG = ["pom.xml", PROTOCOL + "/pom.xml", ".mvn", "tools/quality/static"]


def git(*arguments):
    return subprocess.check_output(["git", *arguments], timeout=30)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    path = Path(path)
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*/754_*"))
    start = read(plan)
    work = start["values"]
    assert all(pin(item["path"]) == item for item in work["oracleReferences"])
    (prior, raw_ref, judge_ref, setup_ref, old_compile_ref, typed_ref, compile_ref,
     jar_ref, prior_scope_ref) = work["oracleReferences"]
    raw, judge, setup, old_compile, typed, current, jar_set, previous = (
        read(ref["path"]) for ref in (raw_ref, judge_ref, setup_ref, old_compile_ref, typed_ref,
                                      compile_ref, jar_ref, prior_scope_ref)
    )
    core = work["productionCoreMain"]
    source = work["source"]
    assert not git("diff", "--name-only", core, source, "--",
                   "src", ":(exclude)src/**/src/test/**")
    assert core == current["sourceCore"] == jar_set["sourceCore"]
    assert current["actualExit"] == current["maven"]["actualExit"] == jar_set["execution"]["actualExit"] == 0
    assert raw["source"] == judge["source"] == setup["source"] == previous["source"] == old_compile["sourceCore"]
    assert not git("diff", "--name-only", raw["source"], core, "--", *CONFIG)
    assert current["tools"] == old_compile["tools"]

    main_dir = PROTOCOL + "/src/main"
    raw_paths = git("ls-tree", "-r", "-z", "--name-only", core, "--", main_dir).decode().split("\0")
    module_sources = sorted(path for path in raw_paths if path.endswith(".java"))
    assert len(module_sources) == raw["protocolMainInputs"] == current["mainCounts"]["protocol"] == 169
    sources = {path: current["sourceInputs"][path] for path in module_sources}
    assert sources == setup["inputs"] == {path: old_compile["sourceInputs"][path] for path in sources}
    assert not git("diff", "--name-only", raw["source"], core, "--", main_dir)
    assert all(sha(git("show", f"{core}:{name}")) == expected for name, expected in sources.items())

    terminal = read(raw["toolTerminal"]["path"])
    assert pin(raw["toolTerminal"]["path"]) == raw["toolTerminal"]
    assert raw["actualToolExit"] == judge["originalToolExit"] == 4
    assert raw["rawFindings"] == judge["rawFindings"] == judge["individualNotApplicable"] == 3
    assert raw["processingErrors"] == judge["applicable"] == judge["unclassified"] == 0
    assert judge["exactReportXmlMatched"] and judge["suppressionAndRuleEdits"] == 0
    assert pin(raw["rawFindingsEvidence"]["path"]) == raw["rawFindingsEvidence"]
    assert pin(raw["appliedRuleset"]["path"]) == raw["appliedRuleset"]
    assert pin(setup["jdkRuntimeImageJar"]["path"]) == setup["jdkRuntimeImageJar"]
    retained_tools = setup["unmodifiedToolSha256"]
    assert all(pin(path)["sha256"] == expected for path, expected in retained_tools.items())

    assert typed["spotbugsViaExactBytes"] == 176 and typed["spotbugsBugs0"]
    assert typed["currentMavenAndNullAway"] and typed["checkstyleErrors"] == 0
    typed_compile = read(typed["build"]["path"])
    assert pin(typed["build"]["path"]) == typed["build"]
    expected_classes = current["physicalClassHashes"]["protocol"]
    assert expected_classes == old_compile["physicalClassHashes"]["protocol"]
    assert expected_classes == typed_compile["physicalClassHashes"]["protocol"]
    assert len(expected_classes) == raw["protocolCompiledPhysical"] == 176
    artifact = jar_set["jars"]["protocol"]["artifact"]
    archive = Path(artifact["path"])
    owner = archive.lstat()
    assert stat.S_ISREG(owner.st_mode) and archive.resolve() == archive and pin(archive) == artifact
    with ZipFile(archive) as jar:
        entries = [entry for entry in jar.namelist() if entry.endswith(".class")]
        assert len(entries) == len(set(entries)) == 176
        assert {entry: sha(jar.read(entry)) for entry in entries} == expected_classes
    assert archive.lstat() == owner and pin(archive) == artifact

    new_test_paths = git("diff", "--name-only", previous["historicalUnitSource"], source,
                         "--", PROTOCOL + "/src/test").decode().splitlines()
    result = dict(actualExit=0, source=source, productionCoreMain=core, originalPmdSource=raw["source"],
                  currentInputInventory=dict(count=len(sources), allSha256Match=True),
                  currentPhysical=dict(count=len(expected_classes), allSha256Match=True, jar=artifact),
                  originalStaticPmd=dict(exit=4, raw=3, notApplicable=3, applicable=0, unclassified=0,
                                         processingErrors=0, terminal=raw["toolTerminal"],
                                         terminalKeys=sorted(terminal), toolArchivesVerified=len(retained_tools)),
                  reusedStaticScope=dict(module="Protocol", exactSpotBugsPhysical=176,
                                          checkstyleErrors=0, nullAwayMavenTerminal="PG39862"),
                  changedPathsSinceHistoricalProtocolPt=new_test_paths, unitAndCoverageRequalified=False,
                  newStaticExecution=0, newProductTests=0, actualBackendActions=0,
                  wholeF03Accepted=False, whole451Accepted=False, newFormalAcceptance=0,
                  sourceReferences=work["oracleReferences"],
                  terminalAtUTC=datetime.now(timezone.utc).isoformat())
    out = OPS / work["run"]
    out.mkdir()
    path = out / "manifest.json"
    with path.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(pin(path))


if __name__ == "__main__":
    main()
