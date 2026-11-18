"""Bind two original Storage fixture classes to the bounded-worker and raw-artifact evidence."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from xml.etree import ElementTree
import datetime as dt
import re

BASE = Path("evidence/01_PT/018_NK-OPS-001")
OUT = BASE / "evidence/PG39426-f03-storage-resource-finite-independent-v1"
SPEC = spec_from_file_location("original_helpers", BASE / "input/5139_bug3272_context_independent_checks.py")
helper = module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


def reverse_fixture_change(text, worker_names):
    for worker in worker_names:
        opening = (
            rf"(?m)^    var {worker} = (Executors\.[^\n]+);\n"
            rf"    try \{{$"
        )
        closing = (
            rf"(?m)^    \}} finally \{{\n      {worker}.shutdownNow\(\);\n"
            rf"      assertTrue\({worker}.awaitTermination\(10, TimeUnit.SECONDS\)\);\n    \}}$"
        )
        # Work left-to-right, pairing the nearest explicit exit with each changed executor.
        for opening_match in re.finditer(opening, text):
            closing_match = re.search(closing, text[opening_match.end():])
            if closing_match:
                end_start = opening_match.end() + closing_match.start()
                end_end = opening_match.end() + closing_match.end()
                text = (
                    text[:opening_match.start()] + f"    try (var {worker} = {opening_match[1]}) {{"
                    + text[opening_match.end():end_start] + "    }" + text[end_end:]
                )
                break
        else:
            raise ValueError(f"missing finite fixture for {worker}")
    return text


def main():
    config = helper.load(BASE / "input/5144_bug3279_storage_resource_profile.json")
    slots = {key: Path(value) / "manifest.json" for key, value in config["slots"].items()}
    m = {name: helper.load(path) for name, path in slots.items()}
    assert all(v["actualExit"] == 0 for v in m.values())
    unit, post = m["unit"], m["post"]
    assert unit["tests"] == post["tests"] == 26 and all(unit[key] == 0 for key in ("failures", "errors", "skipped"))
    assert post["physicalClasses"] == 8 and post["positiveMainCrc"] == 3
    xml = slots["post"].parent / "original-TEST-junit-jupiter.xml"
    assert len(ElementTree.parse(xml).getroot().findall("testcase")) == 26
    assert m["preflight"]["staticApplicable"] == 0 and len(m["static"]["rawFindings"]) == 36
    changed = []
    for item, workers in zip(config["testSources"], (("pool",), ("executor", "executor"))):
        path = item["path"]
        revision = unit["fixedSource"] if "fixedSource" in unit else post["source"]
        before = helper.git("show", f"{revision}^:{path}")
        after = helper.git("show", f"{revision}:{path}")
        reversed_input = reverse_fixture_change(after, workers)
        if "ResourceScopeTest.java" in path and workers == ("pool",):
            reversed_input = reversed_input.replace("import static org.junit.jupiter.api.Assertions.assertTrue;\n", "", 1)
        assert before == reversed_input
        changed.append(dict(path=path, boundedExits=len(workers), originalSourceExactlyRecovered=True))
    core = config["productionCoreMain"]
    assert not helper.git("diff", "--name-only", core, post["source"], "--", ":(glob)src/*/src/main/java/**/*.java")
    raw_path = OUT / "unfiltered.tsv"
    raw = {}
    for row in raw_path.read_text().splitlines():
        fields = row.split("\t")
        if fields[0] == "CLASS":
            raw[fields[1]] = {key: dict(missed=int(miss), covered=int(hit))
                for key, miss, hit in [field.split(":") for field in fields[6:]]}
    assert len(raw) == len(config["physicalClasses"])
    body = raw["dev/codex/schubert/nk/storage/ResourceScope"]
    assert all(counter["missed"] == 0 and counter["covered"] > 0 for counter in body.values())
    retention = OUT / "retention.json"
    archives = helper.archive_streams(config)
    helper.write(retention, archives)
    result = dict(actualExit=0, terminalAtUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      source=post["source"], productionCoreMain=core, tests=26, failures=0, errors=0, skipped=0, notRun=0,
      newTestDefinitions=0, firstProductRunSuccess=True, firstIndependentPostSuccess=True,
      changed=changed, staticApplicable=0, staticRawPmd=36, physicalClasses=8, positiveMainCrc=3,
      rawMainScope=body, unfiltered=raw, standardScope=post["coverage"],
      fixturePreparationFailures=[
        "Ad hoc admission assembly predicted 26 instead of 30 distinct path/rule/line/message identities, so it did not write input.",
        "Preflight correctly rejected grouped occurrences until the existing exact per-message rawMultiplicity schema was used.",
        "Post evidence helper initially held an escaped regex as a physical newline. Fixed before interpreting the existing raw outputs."
      ],
      noProductTestDuringPreparationFailures=True,
      rawEvidence=helper.ref(raw_path), rawCommand=helper.ref(OUT / "raw-command.json"), archive=helper.ref(retention),
      proofs={key:helper.ref(path) for key,path in slots.items()}, verifier=helper.ref(__file__), combinedOldExec=False,
      coverageExclusions=0, newAcceptance=0, formalUpdated=False, whole451Accepted=False,
      remaining=["The retained StorageIoException SQL-compatibility graph is separate F02 work.",
                 "Supporting executor untouched production classes have raw deficits in this run; the ResourceScope result applies to its own executable type.",
                 "Whole six-module coverage and cross-process closing evidence remain outside this run."])
    helper.write(OUT / "manifest.json", result)
    print(helper.ref(OUT / "manifest.json"))


if __name__ == "__main__":
    main()
