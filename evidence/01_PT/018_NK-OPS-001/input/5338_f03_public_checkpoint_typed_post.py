"""Join the current SpotBugs output with the byte-identical nine existing targets."""

from pathlib import Path
import runpy
import xml.etree.ElementTree as ET


RUN = runpy.run_path(str(Path(__file__).with_name("5333_f03_current_three_typed.py")))
STORE, COMMON = (RUN[name] for name in ("OPS", "COMMON"))


def main():
    read = RUN["UPPER"]["read"]
    pin = COMMON["pin"]
    current, bootstrap, previous, catalog, first = [
        next(STORE.glob(pattern)) for pattern in (
            "PG40384-*/manifest.json", "PG40382-*/manifest.json", "PG40362-*/manifest.json",
            "PG40374-*/compiled-classes.json", "PG40330-*/manifest.json")]
    current_data, packages, previous_data, compile_data, first_data = map(
        read, (current, bootstrap, previous, catalog, first))
    core = current_data["productionCore"]
    assert core == packages["productionCore"]
    assert core != previous_data["productionCore"]
    assert current_data["actualExit"] == current_data["terminal"]["actualExit"] == 0
    assert current_data["errors"] == 0 and current_data["missing"] == current_data["spots"] == []
    target, = current_data["observedClassStats"]
    assert current_data["targetHashes"] == {target: compile_data["classHashes"]["bootstrap"][target]}
    assert current_data["testedAuxInput"] == 1048 and current_data["excludedEarlierHoldClasses"] == 53
    xml = Path(current_data["report"]["path"])
    assert pin(xml) == current_data["report"]
    doc = ET.parse(xml).getroot()
    assert not doc.findall("BugInstance") and not doc.findall(".//Error") and not doc.findall(".//MissingClass")
    assert [node.get("class").replace(".", "/") + ".class"
            for node in doc.findall(".//ClassStats")] == [target]
    before_six = Path(previous_data["sourceEvidence"]["path"])
    assert pin(before_six) == previous_data["sourceEvidence"]
    recent = read(before_six)["targetHashes"]
    assert set(recent) == set(previous_data["newSix"])
    prior = first_data["targetHashes"]
    assert set(prior) == set(previous_data["previouslyCheckedThreeByteEquivalent"])
    old = {**recent, **prior}
    assert len(old) == 9 and target not in old
    actual = {name: value for rows in compile_data["classHashes"].values()
              for name, value in rows.items() if name in old}
    assert actual == old
    summary = dict(actualExit=0, productionCore=core, target=target, currentNewTargets=1,
                   earlierSpotBugsQualifiedByteIdentical=sorted(old), currentDeltaTargetsWithEvidence=10,
                   findings=0, missing=0, errors=0, heldPhysical=53, productTests=0,
                   whole451Accepted=False, allSixModulesAccepted=False, formalDelta=0,
                   evidence=list(map(pin, (current, bootstrap, previous, before_six, catalog, first, xml))),
                   terminalAtUTC=COMMON["timestamp"]())
    path = STORE / "PG40386-f03-public-checkpoint-typed-independent-v1"
    path.mkdir()
    COMMON["dump"](path / "manifest.json", summary)
    print(pin(path / "manifest.json"))


if __name__ == "__main__":
    main()
