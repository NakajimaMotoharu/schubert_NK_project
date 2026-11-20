"""Verify the identical input classfiles and the four added direct dependency findings."""

from pathlib import Path
import runpy


RUNNER = runpy.run_path(str(Path(__file__).with_name("5347_f02_nested_controller_canaries.py")))
H, STORE, WEB = (RUNNER[name] for name in ("H", "OPS", "WEB"))
NEW_TYPES = {
    "ReportController", "ReportController$Loader", "ReportController$Holder", "ReportController$Holder$Deep",
    "DisplayEndpoint", "DisplayEndpoint$Dispatcher", "JsonHandler", "JsonHandler$1",
    "AppController", "AppController$Presenter", "BusinessFacade", "BusinessFacade$Adapter",
}
EXPECTED = {
    ("ReportController$Loader", "java.sql.Connection"),
    ("ReportController$Holder$Deep", "java.nio.channels.FileChannel"),
    ("DisplayEndpoint$Dispatcher", "jakarta.jms.Message"),
    ("JsonHandler$1", "java.nio.file.Files"),
}


def main():
    before_path, after_path, first_post = [next(STORE.glob(glob)) for glob in (
        "PG40402-*/manifest.json", "PG40404-*/manifest.json", "PG40405-*/manifest.json")]
    import json
    before, after, initial = (json.loads(path.read_bytes()) for path in (before_path, after_path, first_post))
    assert before["productionCore"] == after["productionCore"]
    assert before["sameProduction"] and after["sameProduction"]
    assert before["fixtureClassHashes"] == after["fixtureClassHashes"]
    declared = {H["P"] + module + ".KnownValue" for module in H["MODULES"]}
    declared.update(H["STUBS"])
    declared.update(WEB + name for _, name, _, _, _ in H["CASES"])
    declared.update(WEB + name for name in NEW_TYPES)
    assert len(declared) == before["analyzedPhysical"] == after["analyzedPhysical"]
    assert set(before["fixtureClassHashes"]) == declared
    assert initial["actualExit"] == 1 and initial["observedInBothOriginalOutputs"] == len(declared)
    assert len(before["cases"]) == len(after["cases"]) == 18 and after["missing"] == []
    assert before["missing"] == [f"PT-F02-NEST-{i:03}" for i in range(1, 5)]
    for run in (before, after):
        assert run["realProductJarInputs"] == run["allFixtureInitializations"] == run["productTests"] == 0
        assert all(H["pin"](Path(row[k]["path"])) == row[k]
                   for row in run["stages"].values() for k in ("stdout", "stderr"))
        assert run["analyzerReport"]["actualExit"] == 1
        data = Path(run["analyzerReport"]["stdout"]["path"]).read_text()
        rules = [row.split("\t") for row in data.splitlines() if row.startswith("RULE\t")]
        assert [r[1] for r in rules if r[2] != "0"] == ["CONTROLLER_BOUNDARY"]
    first, second = [set(map(tuple, run["findings"])) for run in (before, after)]
    assert second - first == {(WEB + name, target) for name, target in EXPECTED} and first <= second
    assert not H["git"]("diff", "--name-only", before["source"], after["source"], "--", "src")
    out = STORE / "PG40406-f02-controller-nested-independent-v1"
    out.mkdir()
    data = dict(actualExit=0, source=after["source"], productionCore=after["productionCore"],
                rootDesign=after["rootDesign"], identicalFixtureClassfiles=len(declared),
                originalDirectStillCorrect=12, forbiddenNestedFixed=4, allowedNestedPreserved=2,
                wholeSynthetic=18, twoRunsNotRepeated=True, toolOnly=True,
                actualProductTests=0, actualProductJarInputs=0, oldFailureHeld=True,
                firstAnalyzerExit=1, correctedAnalyzerExit=1, formalDelta=0,
                wholeF02Accepted=False, whole451Accepted=False,
                sourceEvidence=list(map(H["pin"], (before_path, after_path, first_post))),
                terminalAtUTC=H["timestamp"]())
    H["dump"](out / "manifest.json", data)
    print(H["pin"](out / "manifest.json"))


if __name__ == "__main__":
    main()
