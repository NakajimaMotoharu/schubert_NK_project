"""Attribute raw coverage misses to the exact current classes and one original exec."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory


h=runpy.run_path(str(Path(__file__).with_name("5642_media_single_exec_current_five_types.py")))
OPS,BIN,check,pin,read=(h[key] for key in ("OPS","BIN","check","pin","read"))


def measure_fields(values):
    return {entity:dict(missed=int(miss),covered=int(hit))
            for entity,miss,hit in (part.split(":") for part in values)}


def main(fixed):
    active=OPS/h["FIXED_RUN" if fixed else "RUN"]/"manifest.json"
    m=read(active)
    assert m["actualExit"]==0 and m["tests"]==(28 if fixed else 27) and m["fixtureCanary"]==1
    for item in m["original"]+m["admittedPhysical"]+m["inputMain"]+m["inputTests"]:
        assert pin(Path(item["path"]))==item
    original=active.parent/"media.exec"
    assert pin(original)["sha256"]==m["original"][0]["sha256"]
    assert pin(active.parent/"jupiter.xml")["sha256"]==m["original"][1]["sha256"]
    origins=[Path(reference["path"]) for reference in m["admittedPhysical"]]
    tools_repo=Path("../toolchain/m2/repository").resolve()
    java_cp=[tools_repo/"org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar"]+[
        tools_repo/f"org/ow2/asm/{part}/9.10.1/{part}-9.10.1.jar"
        for part in ("asm","asm-commons","asm-tree")
    ]
    src=Path("tools/quality/jacoco/UnfilteredCodeMeasurement.java")
    name=("PG41262-media-current-five-types-corrected-independent-v1" if fixed else
          "PG41258-media-current-five-types-single-independent-v1")
    out=OPS/name
    out.mkdir()
    stages={}
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-five-media-measure-") as temp:
        base=Path(temp)
        cp=os.pathsep.join(map(str,java_cp))
        stages["compile"],compiled=check([BIN/"javac","--release","25","-proc:none",
                                         "-cp",cp,"-d",base,src])
        assert compiled.returncode==0,compiled.stderr
        stages["measure"],emitted=check([BIN/"java","-cp",f"{base}:{cp}",
            "org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement",
            "--strict-original-exec","--line-deficits",original,*origins])
        assert emitted.returncode==0,emitted.stderr
    report=out/"raw-coverage.tsv"
    report.write_bytes(emitted.stdout)
    crc=runpy.run_path(str(Path(__file__).with_name("5593_p01808_original_name_binding.py")))["class_id"]
    classes,method_misses,lines={},{},[]
    for line in report.read_text().splitlines():
        cols=line.split("\t")
        if cols[0]=="CLASS":
            assert cols[1] not in classes
            target,=[p for p in origins if p.stem==Path(cols[1]).name]
            assert int(cols[2],16)==crc(target.read_bytes())
            classes[cols[1]]=measure_fields(cols[6:])
        elif cols[0]=="METHOD":
            method=measure_fields(cols[5:])
            misses={name:counts["missed"] for name,counts in method.items() if counts["missed"]}
            if misses:
                method_misses[cols[1]+"."+cols[2]+cols[3]]=misses
        elif cols[0]=="DEFICIT":
            lines.append(dict(owner=cols[1],method=cols[2],line=int(cols[4]),
                              counters=measure_fields(cols[5:])))
    assert len(classes)==len(origins)==13
    totals={entity:{k:sum(row[entity][k] for row in classes.values()) for k in ("covered","missed")}
            for entity in ("LINE","METHOD","CLASS","BRANCH","INSTRUCTION")}
    media,=[path for path in origins if path.name=="MediaRangeService.class"]
    stages["bytecode"],bytecode=check([BIN/"javap","-c","-p","-l",media])
    assert bytecode.returncode==0
    text=bytecode.stdout.decode()
    method=text[text.index(" respond("):]
    emitted_fallback="tableswitch" in method and "java/lang/MatchException" in method
    assert emitted_fallback!=fixed
    bytecode_post=out/"media-service-bytecode.txt"
    bytecode_post.write_bytes(bytecode.stdout)
    remaining=[record for record in lines if record["counters"]["BRANCH"]["missed"]]
    d=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),
           source=m["source"],productionCore=m["productionCore"],originalExec=pin(original),
           originalUnit=pin(active),tool=pin(src),status="PARTIAL" if any(v["missed"] for v in totals.values()) else "FULL",
           tools=stages,classes=classes,wholeRaw=totals,methodMisses=method_misses,
           branchDeficitSites=remaining,compilerSwitchFallbackObserved=emitted_fallback,
           standaloneOnly=True,selectedExistingPtRerunHere=0,
           actualRuntimeOrNative=0,manualCoverageExclusions=0,
           originalArtifacts=[pin(report),pin(bytecode_post)],whole451=False,formalDelta=0)
    receipt=out/"manifest.json"
    with receipt.open("x") as stream:
        json.dump(d,stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    print(pin(receipt),totals,remaining)


if __name__=="__main__":
    assert sys.argv[1:] in ([],["--fixed"])
    main(bool(sys.argv[1:]))
