"""Bind all changed Batch Java inputs to existing PMD source reports and decisions."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

OPS = Path("evidence/01_PT/018_NK-OPS-001/evidence")
ROOT = "src/schubert-nk-batch/src/main/java/"
MAIN = ":(glob)" + ROOT + "**/*.java"
NAMESPACE = {"p": "http://pmd.sourceforge.net/report/2.0.0"}


def pin(path):
    return dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest())


def verify(item):
    p = Path(item["path"])
    assert pin(p) == item
    return p


def read(item):
    return json.loads(verify(item).read_bytes())


def git(*parts):
    return subprocess.check_output(["git", *parts],timeout=25)


def sites(receipt, source_name):
    tree = ET.parse(verify(receipt)).getroot()
    assert not tree.findall("p:error", NAMESPACE)
    assert not tree.findall(".//p:suppressedviolation",NAMESPACE)
    return [row.attrib for file in tree.findall("p:file",NAMESPACE)
            if Path(file.attrib["name"]).name == source_name
            for row in file.findall("p:violation",NAMESPACE)]


def main():
    start, = Path("documents/400_PGPT/470_PMO").glob("601_*/1573_*.json")
    task=json.loads(start.read_bytes())
    values=task["values"]
    refs=values["oracleReferences"]
    assert all(verify(ref) for ref in refs)
    independent, alert, alertpost, mode, sdkpost, terminal, expiry, summary, summarypost = map(read,refs[1:])
    assert all(item["actualExit"] == 0 for item in (
        independent,alert,alertpost,mode,sdkpost,terminal,expiry,summary,summarypost))
    core = values["productionCoreMain"]
    base = independent["rootInputs"][3]
    original_core = read(base)["productionCore"]
    paths = git("diff","--name-only",original_core,core,"--",MAIN).decode().splitlines()
    assert not git("diff","--name-only",original_core,core,"--","tools/quality/static")
    assert len(paths) == 13
    closed = []
    unknown = []
    sdk = read(sdkpost["original"])
    alert_inputs = {Path(row["path"]).name:row for row in alert["inputs"] if row["path"].startswith(ROOT)}
    single_mode = next(p for p in mode["sourceInputs"] if p["path"].endswith("/MonitoringModePolicy.java"))
    assert alertpost["productionCore"]==alert["source"]==core
    assert alertpost["pmdRaw"]==alert["pmd"]["raw"]==14
    assert len(alertpost["newSyncDisposition"]) + alertpost["otherExistingPmdOccurrences"]==14
    assert sdk["pmd"]["raw"]==0
    assert terminal["applicableUnclassifiedInThisFile"]==0
    assert len(expiry["staticDispositions"])==expiry["pmdRaw"]==17 and expiry["applicable"]==0
    assert summary["pmd"]["raw"]==summarypost["preservedPmdRaw"]==10
    for key in paths:
        path = Path(key)
        current=git("show",f"{core}:{key}")
        fingerprint=pin(path)
        assert sha256(current).hexdigest()==fingerprint["sha256"]
        name=path.name
        if name == "MonitoringModePolicy.java":
            source, scan, decisions = single_mode,mode["pmd"]["report"],refs[4]
            assert mode["pmd"]["findings"]==[] and mode["pmd"]["errors"]==0
        elif name in alert_inputs:
            source, scan, decisions = alert_inputs[name],alert["pmd"]["report"],refs[3]
        elif name == "BatchStandardMetricSource.java":
            source = next(row for row in sdk["sourceInputs"] if row["path"]==key)
            scan, decisions = sdkpost["originalPMD"],refs[5]
        elif name=="CleanupTerminalRepository.java":
            source = terminal["relatedFile"]
            scan, = [entry for entry in read(terminal["inputs"][1])["reports"]
                     if entry["path"].endswith("/pmd.xml")]
            decisions = refs[6]
        elif name=="ExpiryAuditRepository.java":
            source = next(s for s in expiry["sourceEvidence"] if s["path"]==key)
            scan = next(s for s in expiry["sourceEvidence"] if s["path"].endswith("/pmd.xml"))
            decisions = refs[7]
        elif name=="InspectionSummaryRepository.java":
            source = next(row for row in summary["sources"] if row["path"]==key)
            scan, decisions = summary["pmd"]["report"],refs[9]
        else:
            unknown.append(dict(path=key,reason="no source-owner observation"))
            continue
        assert source==fingerprint
        measure=sites(scan,name)
        if name=="CleanupTerminalRepository.java":
            assert len(measure)==terminal["rawPmdCurrent"]
        if name=="ExpiryAuditRepository.java":
            assert len(measure)==len(expiry["staticDispositions"])
        if name=="InspectionSummaryRepository.java":
            assert len(measure)==len(summary["pmdFindings"])
        closed.append(dict(input=fingerprint,report=scan,decisionReceipt=decisions,
                           rawCount=len(measure),decisionScope="source-and-rules-local"))
    assert not unknown and len(closed)==13
    destination=OPS/values["run"]
    destination.mkdir()
    result=destination/"manifest.json"
    with result.open("x") as stream:
        json.dump(dict(actualExit=0,core=core,originalTypedCore=original_core,
                       diffMainCount=13,targetedExistingPmdCorrespondence=13,sourceDecisions=closed,
                       rawForTheseSources=sum(row["rawCount"] for row in closed),
                       sourceExcludedNoProof=unknown,staticReplays=0,productTests=0,
                       individualOldReportsKept=True,wholeBatchPmd=False,wholeF03=False,
                       whole451=False,formalDelta=0,terminalAtUTC=datetime.now(timezone.utc).isoformat()),
                  stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    print(pin(result),len(closed))


if __name__=="__main__":
    main()
