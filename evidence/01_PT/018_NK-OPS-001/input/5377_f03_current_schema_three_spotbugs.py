"""Check the three approved module artifacts after the SchemaHistory fix."""

import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile, ZIP_DEFLATED


H = runpy.run_path(str(Path(__file__).with_name("5368_f03_current_three_whole_spotbugs.py")))
OPS, PLAN, COMMON, UPPER, MODULES = (H[k] for k in ("OPS","PLAN","COMMON","UPPER","MODULES"))
TYPE = "dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission.class"


def main():
    read=UPPER["read"]
    pin,sha,dump=(COMMON[k] for k in ("pin","sha","dump"))
    start=read(next(PLAN.glob("896_*")))
    w=start["values"]
    refs=w["oracleReferences"]
    assert all(pin(Path(p["path"]))==p for p in refs)
    built, isolated, previous, old, _ = (read(p["path"]) for p in refs[1:])
    assert built["productionCore"]==isolated["productionCore"]==w["productionCoreMain"]
    assert previous["productionCore"]==old["productionCore"] and previous["allObserved456"]
    assert old["terminal"]["actualExit"]==0 and built["spotbugsChildExitAfterRecovery"] is None
    command=old["terminal"]["command"]
    sdk=Path(command[command.index("-auxclasspathFromFile")+1])
    older=read(next(OPS.glob("PG39810-*/begin.json")))
    models=dict(older["sdkJars"])
    for ref in (read(next(OPS.glob("PG39812-*/manifest.json")))["onlyAdditionalAux"],
                read(next(OPS.glob("PG40370-*/manifest.json")))["explicitMetricsSdk"]):
        models[ref["path"]]=ref["sha256"]
    assert sorted(models)==sdk.read_text().splitlines()
    assert all(pin(Path(path))["sha256"]==digest for path,digest in models.items())
    tool_files={p["path"]:p["sha256"] for p in older["toolAndRulePins"]}
    assert all(pin(Path(p))["sha256"]==tool_files[p] for p in command[command.index("-cp")+1].split(":"))
    out=(OPS/w["run"]).resolve()
    out.mkdir()
    changed=set()
    all_names=set()
    artifact_proofs={}
    xml=out/"spotbugs.xml"
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-f03-schema-current-three-") as name:
        scratch=Path(name)
        combined=scratch/"f03-three-current-types.jar"
        with ZipFile(combined,"x",compression=ZIP_DEFLATED) as joined:
            for module,count in MODULES.items():
                current=built["packagedBuild"][module]["artifact"]
                previous_module=old["inputs"][module]
                archive=Path(current["path"])
                baseline=Path(previous_module["jar"]["path"])
                assert pin(archive)==current and pin(baseline)==previous_module["jar"]
                with ZipFile(archive) as new, ZipFile(baseline) as prior:
                    now={member: new.read(member) for member in new.namelist() if member.endswith(".class")}
                    then={member: sha(prior.read(member)) for member in prior.namelist() if member.endswith(".class")}
                    assert then.keys()==now.keys() and len(now)==count and not(all_names & now.keys())
                    assert sha(json.dumps(then,sort_keys=True).encode())==previous_module["classMapSha256"]
                    current_hashes={member:sha(data) for member,data in now.items()}
                    if module == "bootstrap":
                        assert current_hashes[TYPE] == built["exactPhysicalScope"][TYPE]
                    delta={entry for entry in now if current_hashes[entry]!=then[entry]}
                    changed.update(delta)
                    all_names.update(now)
                    for n,b in sorted(now.items()):
                        joined.writestr(n,b)
                artifact_proofs[module]=dict(jar=current, physical=count, changed=sorted(delta),
                    classMapSha256=sha(json.dumps(current_hashes,sort_keys=True).encode()))
        assert changed=={TYPE} and len(all_names)==456
        result=UPPER["run"](out,"spotbugs",[
            *command[:command.index("-auxclasspathFromFile")+1],sdk,"-output",xml,combined
        ],scratch,{"PATH":"/usr/bin:/bin","LANG":"C.UTF-8"})
        dump(out/"spotbugs-terminal.json",result)
    report=ElementTree.parse(xml).getroot()
    observed=[n.get("class").replace(".","/")+".class" for n in report.findall(".//ClassStats")]
    failures={node:len(report.findall(node)) for node in ("BugInstance",".//Error",".//MissingClass")}
    assert len(observed)==len(set(observed))==456 and set(observed)==all_names
    assert result["actualExit"]==0 and not any(failures.values())
    d=dict(actualExit=0,source=w["source"],productionCore=w["productionCoreMain"],artifacts=artifact_proofs,
           typeStats=len(observed),actualToolExit=result["actualExit"],report=pin(xml),terminal=result,
           failures=failures,previousIncompleteChildReobtained=False,actualTestsHere=0,
           wholeF03Accepted=False,whole451Accepted=False,terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",d)
    print(pin(out/"manifest.json"),len(observed))


if __name__=="__main__":
    main()
