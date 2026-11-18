"""Reanalyze only the two modules with a missing same-build peer in the original report."""
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
import os
from pathlib import Path
from xml.etree import ElementTree as ET

spec = spec_from_file_location("ports", Path(__file__).with_name("5151_ssc461_service_db_ports.py"))
m = module_from_spec(spec)
spec.loader.exec_module(m)
RUNTIME = m.E / "provisional/PG13218-spotbugs-fresh-aux-plan-recovery-v1/manifest.json"
RUNTIME_SHA = "a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564"
OUT = m.E / "PG39440-service-jdbc-spotbugs-current-peers-v1"


def main():
    build = m.load(m.BUILD)
    hashes = m.checked_build(build)
    before = m.OUT / "manifest.json"
    original = m.load(before)
    assert original["source"] == build["sourceCore"] and original["inputHashes"] == hashes
    assert m.digest(RUNTIME) == RUNTIME_SHA
    runtime = m.load(RUNTIME)
    deps = {p: h for p, h in runtime["auxiliaryClasspathHashes"].items() if p not in runtime["currentJarHashes"]}
    files = {**runtime["toolRuntimeHashes"], **deps}
    assert all(Path(p).is_relative_to(m.TC) and m.digest(Path(p)) == h for p,h in files.items())
    current = {module:Path(build["cwd"])/f"src/schubert-nk-{module}/target/classes" for module in build["physicalClassHashes"]}
    original_missing = {}
    for module, report in original["reports"].items():
        path = Path(report["xml"]["path"])
        assert m.ref(path) == report["xml"] and report["bugs"]==report["errors"]==0 and report["exactScope"]
        absent = [row.text.replace(".", "/") + ".class" for row in ET.parse(path).findall(".//MissingClass")]
        if absent:
            assert all(sum(name in classes for classes in build["physicalClassHashes"].values()) == 1 for name in absent)
            original_missing[module] = absent
    assert {k:len(v) for k,v in original_missing.items()} == {"bootstrap":3,"batch":7}
    OUT.mkdir()
    m.receipt.SLOT=OUT
    cp_file=(OUT/"aux.txt").resolve()
    cp_file.write_text("\n".join(sorted([*deps,*map(str,current.values())])) + "\n")
    updated = {}
    for module in original_missing:
        report=(OUT/(module+".xml")).resolve()
        command=[str(m.JAVA),"-Xmx2g","-cp",os.pathsep.join(runtime["toolClasspath"]),"edu.umd.cs.findbugs.FindBugs2",
          "-effort:max","-low","-xml:withMessages","-exitcode","-auxclasspathFromFile",str(cp_file),"-output",str(report),str(current[module])]
        terminal=m.receipt.step(module,command,m.ROOT,timeout=230)
        tree=ET.parse(report).getroot()
        exact={x.get("class").replace(".","/") + ".class" for x in tree.findall(".//ClassStats")} == set(build["physicalClassHashes"][module])
        updated[module]=dict(actualExit=terminal["actualExit"],timedOut=terminal["timedOut"],terminal=terminal,
             xml=m.ref(OUT/report.name),exactScope=exact,bugs=len(tree.findall(".//BugInstance")),
             errors=len(tree.findall(".//Error")),missing=len(tree.findall(".//MissingClass")))
    assert m.checked_build(build) == hashes and all(m.digest(Path(p)) == h for p,h in files.items())
    ok=all(v["exactScope"] and not any(v[k] for k in ("bugs","errors","missing","actualExit","timedOut")) for v in updated.values())
    m.write(OUT/"manifest.json",dict(actualExit=0 if ok else 1,source=build["sourceCore"],compile=m.ref(m.BUILD),
        original=m.ref(before),runtime=m.ref(RUNTIME),toolHashes=files,currentPeerTrees={k:str(v) for k,v in current.items()},
        terminalAtUTC=datetime.now(timezone.utc).isoformat(),reports=updated,originalMissing=original_missing,
        retainedUnchangedModules=["protocol","storage"],analysisApplicationTests=0,wholeF03Accepted=False))
    print({k:{n:v[n] for n in ("bugs","missing","errors","actualExit","exactScope")} for k,v in updated.items()})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
