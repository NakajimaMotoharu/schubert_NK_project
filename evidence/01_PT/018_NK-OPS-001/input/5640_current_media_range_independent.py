"""Measure the media port's original exec and isolate new static-analysis findings."""

from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


h = runpy.run_path(str(Path(__file__).with_name("5639_current_media_range_error_response.py")))
OPS, BIN, DIR, TEST, check, pin, read = (
    h[key] for key in ("OPS","BIN","DIR","TEST","check","pin","read")
)


def main():
    unit_path = OPS/h["RUN"]/"manifest.json"
    outcome = read(unit_path)
    assert outcome["actualExit"]==0 and outcome["actualProductTests"]==11
    archives = outcome["originalArtifacts"]
    for item in [*archives,*outcome["coverageClassFiles"],*outcome["inputSources"],outcome["testInput"]]:
        assert pin(Path(item["path"]))==item
    exec_path=unit_path.parent/"unit.exec"
    assert pin(exec_path)["sha256"]==archives[1]["sha256"]
    assert pin(unit_path.parent/"jupiter.xml")["sha256"]==archives[2]["sha256"]
    assert pin(unit_path.parent/"spotbugs.xml")["sha256"]==archives[3]["sha256"]
    candidates = [Path(item["path"]) for item in outcome["coverageClassFiles"]]
    s,=OPS.glob("PG41200-*/manifest.json")
    prior=read(s)
    deps=[Path(row["path"]) for row in prior["admittedDependencies"] if Path(row["path"]).name in {
        "junit-platform-console-standalone-1.13.4.jar","current-protocol176.jar","jspecify-1.0.1.jar"
    }]
    assert len(deps)==3 and all(pin(dep) in prior["admittedDependencies"] for dep in deps)
    tools_repo=Path("../toolchain/m2/repository").resolve()
    measure_deps=[tools_repo/"org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"]+[
        tools_repo/f"org/ow2/asm/{lib}/9.10.1/{lib}-9.10.1.jar"
        for lib in ("asm","asm-commons","asm-tree")
    ]
    reader=Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
    evidence=OPS/"PG41252-media-current-range-independent-v1"
    evidence.mkdir()
    origin = subprocess.check_output(["git","show",f'{prior["source"]}:{TEST}'],timeout=10)
    old_source = next(ref for ref in prior["sourceInputs"] if ref["path"]==str(TEST))
    assert __import__("hashlib").sha256(origin).hexdigest()==old_source["sha256"]
    pmd_ref,=OPS.glob("PG41208-*/manifest.json")
    pmd_base=read(pmd_ref)["stages"]["pmd"]["command"][:6]
    stages={}
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-range-service-post-") as tmp:
        root=Path(tmp)
        cp=os.pathsep.join(map(str,measure_deps))
        stages["compile"], built=check([BIN/"javac","--release","25","-proc:none","-cp",cp,
            "-d",root,reader])
        assert built.returncode==0,built.stderr
        stages["analysis"], measured=check([BIN/"java","-cp",f"{root}:{cp}",
            "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
            "--strict-original-exec",exec_path,*candidates])
        report=evidence/"coverage.tsv"
        report.write_bytes(measured.stdout)
        assert measured.returncode==0,measured.stderr
        for path in candidates:
            dst=root/DIR/path.name
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes(path.read_bytes())
        legacy=root/"prior"/TEST.name
        legacy.parent.mkdir()
        legacy.write_bytes(origin)
        aux=":".join(map(str,(BIN.parent/"lib/jrt-fs.jar",root,*deps)))
        raw_sites={}
        for tag,path in (("before",legacy),("current",TEST)):
            files=root/(tag+".txt")
            files.write_text(str(path.resolve())+"\n")
            dest=evidence/(tag+"-pmd.xml")
            stages[tag], outcome_pmd=check([*pmd_base,files,"--rulesets","tools/quality/static/pmd.xml",
                "--use-version","java-25","--aux-classpath",aux,"--no-cache",
                "--format","xml","--report-file",dest])
            rt=ET.parse(dest).getroot()
            assert outcome_pmd.returncode in (0,4)
            assert not any(node.tag.split("}")[-1] in {"error","configerror","suppressedviolation"} for node in rt)
            raw_sites[tag]=[
                dict(rule=node.get("rule"),line=int(node.get("beginline")))
                for node in rt.iter() if node.tag.split("}")[-1]=="violation"
            ]
    dif=Counter(item["rule"] for item in raw_sites["current"])-Counter(item["rule"] for item in raw_sites["before"])
    classes={}
    for line in measured.stdout.decode().splitlines():
        if not line.startswith("CLASS\t"):
            continue
        fields=line.split("\t")
        assert fields[1] not in classes
        classes[fields[1]]={name:dict(missed=int(miss),covered=int(hit))
                           for name,miss,hit in (part.split(":") for part in fields[6:])}
    assert len(classes)==len(candidates)==13
    metrics={k:dict(missed=sum(coverage[k]["missed"] for coverage in classes.values()),
                    covered=sum(coverage[k]["covered"] for coverage in classes.values()))
             for k in ("LINE","METHOD","CLASS","BRANCH","INSTRUCTION")}
    r=dict(actualExit=0 if not dif else 1,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
           source=outcome["source"],unit=pin(unit_path),referenceFixture=old_source,
           originalCoverage=pin(exec_path),measurement=pin(reader),classCounters=classes,wholeScope=metrics,
           rawPmd=raw_sites,increasedPmdByRule=dict(dif),rawOutputs=list(map(pin,sorted(evidence.iterdir()))),
           stages=stages,productTestsExecuted=0,nativeOperations=0,whole451=False,formalDelta=0)
    manifest=evidence/"manifest.json"
    with manifest.open("x") as f:
        json.dump(r,f,indent=2)
        f.write("\n")
    print(pin(manifest),metrics,dict(dif))
    return r["actualExit"]


if __name__=="__main__":
    raise SystemExit(main())
