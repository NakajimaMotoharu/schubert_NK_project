"""Independently check the two exact result classes without executing product tests."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import runpy
from xml.etree import ElementTree as ET

ROOT = Path("evidence/01_PT/004_NK-DAT-001/evidence")
TARGET = "dev/codex/schubert/nk/batch/repository/RunReferences"
CLASS_KINDS = ("LINE","METHOD","CLASS","BRANCH","INSTRUCTION")


def pin(p):
    return {"path":str(p),"sha256":sha256(p.read_bytes()).hexdigest()}


def touched(ref):
    p=Path(ref["path"])
    assert pin(p)==ref
    return p


def main():
    path, = ROOT.glob("PG41150-*/manifest.json")
    status=json.loads(path.read_bytes())
    assert status["actualExit"]==0 and status["whole451"] is False
    assert set(status["steps"])=={"compile","unit","raw-compile","raw"}
    assert all(step["actualExit"]==0 for step in status["steps"].values())
    cases=ET.parse(touched(status["xml"])).getroot().findall("testcase")
    assert len(cases)==12
    assert set(status["physicalQualified"]) >= {TARGET+".class",TARGET[:-1]+"Repository.class"}
    names={r for r in status["scopedRaw"]}
    assert names=={TARGET,TARGET[:-1]+"Repository"}
    wanted={}
    for line in touched(status["raw"]).read_text().splitlines():
        row=line.split("\t")
        if row[0]=="CLASS" and row[1] in names:
            assert row[3]=="true" and row[1] not in wanted
            wanted[row[1]]={key:(int(missed),int(covered)) for key,missed,covered in
                            (r.split(":") for r in row[6:])}
    assert wanted.keys()==names
    for name,counters in wanted.items():
        assert all(counters[item][0]==0 and counters[item][1]>0 for item in CLASS_KINDS)
        assert all(status["scopedRaw"][name][item]==list(counters[item]) for item in CLASS_KINDS)
    decode=runpy.run_path("tools/quality/jacoco_readonly_exec_subset.py")["decode"]
    exec_data=decode(touched(status["exec"]).read_bytes(),names)
    assert [r["labelBytesHex"] for r in exec_data["sessions"]]==[status["session"].encode().hex()]
    out=ROOT/"PG41152-p00403-dao-result-value-joint-independent-v1"
    out.mkdir()
    artifact=out/"manifest.json"
    with artifact.open("x") as f:
        json.dump(dict(actualExit=0,productionCore=status["core"],run=pin(path),currentTests=12,
                       wholeOrdinarySuites=2,scopedTargetPhysical=2,rawCounters=wanted,
                       nativeOrDbActions=0,productTestsReplayed=0,formalDelta=0,whole451=False,
                       terminalAtUTC=datetime.now(timezone.utc).isoformat()),f,indent=2)
        f.write("\n")
    print(pin(artifact))


if __name__=="__main__":
    main()
