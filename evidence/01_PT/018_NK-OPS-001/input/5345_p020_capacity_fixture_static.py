"""Run static checks on the same bytes under the declared Java filename."""

import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET


ROOT = Path(__file__).parent
UPPER = runpy.run_path(str(ROOT / "5326_f02_group_lookup_upper.py"))
STORE, COMMON = (UPPER[key] for key in ("EVIDENCE", "COMMON"))


def main():
    read, pin = UPPER["read"], COMMON["pin"]
    host = read(next(STORE.glob("PG40396-*/begin.json")))
    first = next(STORE.glob("PG40397-*"))
    old = read(first / "manifest.json")
    assert old["source"] == host["source"] and old["fixture"] == host["fixture"]
    fixture = Path(host["fixture"]["path"])
    assert pin(fixture) == host["fixture"]
    assert old["stages"]["checkstyle"]["actualExit"] == 1
    initial = ET.parse(first / "checkstyle.xml")
    messages = list(initial.iter("error"))
    assert len(messages) == 1 and messages[0].get("source").endswith(".OuterTypeFilenameCheck")
    static = read(next(STORE.glob("PG40210-*/begin.json")))
    tool_pins = static.get("toolAndRulePins")
    if tool_pins:
        assert all(pin(Path(value["path"])) == value for value in tool_pins)
    out = (STORE / "PG40399-p020-real-filestore-fixture-static-qualified-v1").resolve()
    out.mkdir()
    stages = {}
    with TemporaryDirectory(dir="/dev/shm", prefix="pgpt-gate-real-fixture-static-") as directory:
        owned = Path(directory)
        java = owned / "GateOwnedFileStoreContract.java"
        java.write_bytes(fixture.read_bytes())
        assert pin(java)["sha256"] == host["fixture"]["sha256"]
        selected = owned / "selected.txt"
        selected.write_text(str(java) + "\n")
        for label in ("format", "checkstyle", "pmd"):
            command = static["commands"][label][:]
            if label == "format":
                command = [*command[:6], java]
            elif label == "checkstyle":
                command[command.index("-o") + 1] = out / "checkstyle.xml"
                command[-1] = "@" + str(selected)
            else:
                command[command.index("--file-list") + 1] = selected
                command[command.index("--report-file") + 1] = out / "pmd.xml"
            stages[label] = UPPER["run"](out, label, command, Path.cwd(),
                                        {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
    assert stages["format"]["actualExit"] == stages["checkstyle"]["actualExit"] == 0
    assert not list(ET.parse(out / "checkstyle.xml").iter("error"))
    rules = ET.parse(out / "pmd.xml").getroot()
    raw = [item for item in rules.iter() if item.tag.rsplit("}", 1)[-1] == "violation"]
    assert stages["pmd"]["actualExit"] == 4 and len(raw) == 1
    item, = raw
    assert item.get("rule") == "UseConcurrentHashMap" and item.get("variable") == "options"
    assert item.get("method") == "admitsOnlyTheOwnedRealFileStoreThroughThePublicCli"
    suite = Path(next(STORE.glob("PG40396-*/manifest.json")))
    runtime = read(suite)
    argv = runtime["terminal"]["steps"]["unit"]["command"]
    assert "--config=junit.jupiter.execution.parallel.enabled=false" in argv
    assert fixture.read_text().count("options.forEach") == 2
    decision = dict(rule=item.get("rule"), line=int(item.get("beginline")), disposition="NOT_APPLICABLE",
                    reason="The local LinkedHashMap is created, iterated synchronously twice and never escapes. "
                           "The one selected fixture is run with JUnit parallel execution disabled and "
                           "restores each modified property in finally.")
    result = dict(actualExit=0, executedFixtureSource=host["source"], fixture=host["fixture"],
                  originalCheckstyleExit=1, correctedCheckstyleExit=0, formatExit=0, pmdExit=4,
                  pmdRaw=1, pmdApplicable=0, pmdUnclassified=0, pmdPerSite=[decision],
                  styleInputByteChanged=False, sourceByteChanged=False, newToolOrProductTests=0,
                  stages=stages, earlierStatic=pin(first / "manifest.json"), unit=pin(suite),
                  rulesChanged=False, whole451Accepted=False, terminalAtUTC=COMMON["timestamp"]())
    COMMON["dump"](out / "manifest.json", result)
    print(pin(out / "manifest.json"))


if __name__ == "__main__":
    main()
