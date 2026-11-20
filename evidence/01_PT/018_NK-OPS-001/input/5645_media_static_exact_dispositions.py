"""Independently classify the inherited raw findings in the current media subset."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
from xml.etree import ElementTree as ET


h=runpy.run_path(str(Path(__file__).with_name("5642_media_single_exec_current_five_types.py")))
OPS,BIN,check,pin,read=(h[key] for key in ("OPS","BIN","check","pin","read"))


def git_body(ref,path):
    return subprocess.check_output(["git","show",f"{ref}:{path}"],timeout=12).decode()


def main():
    old=OPS/h["RUN"]/"manifest.json"
    current=OPS/h["FIXED_RUN"]/"manifest.json"
    raw,=OPS.glob("PG41264-*/manifest.json")
    receipt=read(raw)
    earlier,latest=read(old),read(current)
    assert receipt["source"]==latest["productionCore"] and receipt["actualExit"]==1
    assert receipt["matchingMainToRawUnit"]==13 and receipt["stages"]["nullaway"]["exit"]==0
    assert receipt["spotbugsMissing"]==receipt["spotbugsErrors"]==0
    assert not receipt["pmdErrorsOrSuppressions"]
    for pair in receipt["outputs"]:
        assert pin(Path(pair["path"]))==pair
    test,=[Path(ref["path"]) for ref in latest["inputTests"] if ref["path"].endswith("/ExceptionValueContractTest.java")]
    main,=[Path(ref["path"]) for ref in latest["inputMain"] if ref["path"].endswith("/MediaRangeService.java")]
    old_test=git_body(earlier["source"],test)
    old_main=git_body(earlier["productionCore"],main)
    changed_test=git_body(latest["source"],test)
    changed_main=git_body(latest["productionCore"],main)
    assert changed_test==test.read_text() and changed_main==main.read_text()
    fixture_line="assertThrows(NullPointerException.class, () -> new MediaDeliveryException(null));"
    tree=ET.parse(raw.parent/"spotbugs.xml").getroot()
    spots=[]
    for hit in tree.findall("BugInstance"):
        method=hit.find("Method").get("name")
        lineno=int(hit.find("SourceLine").get("start"))
        assert changed_test.splitlines()[lineno-1].strip()==fixture_line and old_test.count(fixture_line)==1
        assert method=="lambda$exc007MediaStatusAndRetryRemainClosedAndNonNull$0"
        spots.append(dict(raw=hit.get("type"),owner=str(test),line=lineno,method=method,
            verdict="TEST_NEGATIVE_NULL_REJECTION_NOT_PRODUCT_DEFECT",
            rationale="The checked JUnit lambda deliberately calls the constructor with null and expects the exception; it uses no returned exception object. This source line is identical to the previous tested fixture."))
    assert {site["raw"] for site in spots}=={"NP_NULL_PARAM_DEREF_NONVIRTUAL","RV_EXCEPTION_NOT_THROWN"}
    [pmd]=receipt["pmdSites"]
    literal="Map<String, String> headers = new HashMap<>();"
    assert pmd["owner"]==main.name and pmd["rule"]=="UseConcurrentHashMap"
    assert changed_main.splitlines()[pmd["line"]-1].strip()==literal and old_main.count(literal)==1
    method=changed_main.split("private static void respond",1)[1]
    assert "response.begin(status, Map.copyOf(headers));" in method
    assert "response.begin(status, headers)" not in method and "static Map" not in method
    spots.append(dict(raw=pmd["rule"],owner=str(main),line=pmd["line"],
        verdict="REQUEST_LOCAL_MAP_NOT_CONCURRENTLY_SHARED",
        rationale="This method allocates the map on each invocation. Only the immutable copy is handed to the response; no instance, static, or callback retains the mutable object."))
    old_type,=[Path(ref["path"]) for ref in earlier["admittedPhysical"] if ref["path"].endswith("/MediaRangeService.class")]
    new_type,=[Path(ref["path"]) for ref in latest["admittedPhysical"] if ref["path"].endswith("/MediaRangeService.class")]
    osig,old_javap=check([BIN/"javap","-public","-s",old_type])
    nsig,new_javap=check([BIN/"javap","-public","-s",new_type])
    assert old_javap.returncode==new_javap.returncode==0 and old_javap.stdout==new_javap.stdout
    assert pin(old_type)["sha256"]!=pin(new_type)["sha256"]
    out=OPS/"PG41266-media-current-five-types-static-dispositions-v1"
    out.mkdir()
    r=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=latest["productionCore"],
      inheritedRaw=pin(raw),oldUnit=pin(old),newUnit=pin(current),findings=spots,inScopeRaw=3,
      applicableFindings=0,unclassified=0,rulesOrCoverageExclusionsChanged=False,
      publicDescriptorEqual=True,oldJavap=osig,newJavap=nsig,abiSha256=sha256(old_javap.stdout).hexdigest(),
      productTestsReplayed=0,wholeF03=False,whole451=False,formalDelta=0)
    d=out/"manifest.json"
    with d.open("x") as f:
        json.dump(r,f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(pin(d),len(spots))


if __name__=="__main__":
    main()
