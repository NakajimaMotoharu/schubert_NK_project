"""Match the four outstanding config diagnostics against the previously qualified inputs."""

from datetime import datetime, timezone
from pathlib import Path
import runpy
from xml.etree import ElementTree as XML


H = runpy.run_path(str(Path(__file__).with_name("5662_f03_bootstrap_pmd_flows.py")))
OPS, pin, checked, read, write, git = (H[n] for n in ("OPS", "pin", "checked", "read", "write", "git"))
PLAN = H["H"]["H"]["PLAN"]
NS = H["H"]["NS"]


def main():
    plan, = PLAN.glob("1710_*.json")
    start = read(plan)["values"]
    _, current_path, older_path, tunit_path = map(checked, start["oracleReferences"])
    current, pre, unit = map(read, (current_path, older_path, tunit_path))
    assert current["classified"] == 47 and current["unclassified"] == 4
    assert pre["actualExit"] == pre["staticApplicable"] == pre["unclassified"] == 0
    assert unit["actualExit"] == unit["errors"] == unit["failures"] == unit["skipped"] == unit["notRun"] == 0
    assert unit["tests"] == 14 and unit["actualHeldActions"] == 0 and unit["actualServicesStarted"] == 0
    current_raw_path = checked(current["typedStatic"])
    current_raw = read(current_raw_path)
    old_core = unit["productionCoreMain"]
    assert old_core != start["productionCoreMain"]
    targets = {name: sha for name, sha in pre["inputHashes"].items()
               if name.endswith(("ApiNonSecretConfig.java", "WebNonSecretConfig.java"))}
    assert len(targets) == 2
    paths = [*targets, "pom.xml", "src/schubert-nk-bootstrap/pom.xml", "tools/quality/static/pmd.xml"]
    assert not git("diff", "--name-only", old_core, start["productionCoreMain"], "--", *paths)
    for path, digest in targets.items():
        assert pin(Path(path))["sha256"] == digest == current_raw["analyzedSourceSha256"][path]
    assert unit["static"]["ref"] == pre["static"] and unit["static"]["rootCompilerExact"]
    checked(pre["static"])
    current_pmd = XML.parse(checked(current_raw["pmd"])).getroot()
    current_scope = []
    for src in current_pmd.findall("p:file", NS):
        owner = next((path for path in targets if Path(path).name == Path(src.attrib["name"]).name), None)
        if owner:
            current_scope.extend((owner, site.attrib["rule"], site.attrib["beginline"], site.text.strip())
                                 for site in src.findall("p:violation", NS))
    known = {(row["path"], row["rule"], row["line"], row["message"]): row["reason"]
             for row in pre["classified"]
             if row["path"] in targets and row["disposition"] == "NOT_APPLICABLE"}
    assert len(current_scope) == len(known) == 4 and set(current_scope) == known.keys()
    observations = read(checked(current["readOnlyReport"]))
    for row in observations:
        if row["state"] == "UNCLASSIFIED_CURRENT_FLOW":
            key, = [r for r in current_scope if r[:3] == (row["path"], row["rule"], str(row["line"]))]
            row["state"] = "EXACT_CONFIG_PARSE_AND_PATH_FAIL_CLOSED"
            row["reason"] = known[key]
            row["independentTypedPrior"] = pin(older_path)
    assert len(observations) == 51 and all(row["state"] != "UNCLASSIFIED_CURRENT_FLOW" for row in observations)
    out = OPS / start["run"]
    out.mkdir()
    write(out / "all-51-site-dispositions.json", observations)
    write(out / "manifest.json", dict(
        actualExit=0, run=out.name, source=start["source"], core=start["productionCoreMain"],
        currentPmd=pin(current_raw_path), oldInputEvidence=pin(older_path), oldRuntimeEvidence=pin(tunit_path),
        oldRuntimeCases=14, rerunOldCases=0, noOldExecMerged=True, exactFiles=len(targets),
        identicalConfigRawSiteCount=4, confirmedClassifications=51, unclassified=0, rawDiagnostics=51,
        localStaticApplicable=0, stillHeldNativeAgentClasses=1,
        dispositions=pin(out / "all-51-site-dispositions.json"), wholeF03=False, whole451=False,
        formalDelta=0, terminalAtUTC=datetime.now(timezone.utc).isoformat()))
    print("Raw 51, classified 51, config four exact, native hold 1")


if __name__ == "__main__":
    main()
