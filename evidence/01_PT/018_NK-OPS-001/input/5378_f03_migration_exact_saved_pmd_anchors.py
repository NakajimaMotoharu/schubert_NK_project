"""Rebind unresolved migration findings to byte-identical, independently judged sites."""

from collections import Counter
from pathlib import Path
import runpy
from xml.etree import ElementTree


H=runpy.run_path(str(Path(__file__).with_name("5373_f03_three_pmd_exact_dispositions.py")))
OPS,UPPER,COMMON= (H[n] for n in ("OPS","UPPER","COMMON"))
PLAN=next(Path("documents/400_PGPT/470_PMO").glob("601_*"))


def static_key(path,line,rule,message):
    relative="src/"+path.split("/src/",1)[1] if path.startswith("/") else path
    return (relative, int(line), rule, message)


def main():
    pin,sha,git,dump=(COMMON[n] for n in ("pin","sha","git","dump"))
    read=UPPER["read"]
    start=read(next(PLAN.glob("899_*")))
    w=start["values"]
    core=w["productionCoreMain"]
    refs=w["oracleReferences"]
    assert all(pin(Path(h["path"]))==h for h in refs)
    independent,current,qualified,c1,c2,a1,a2=(read(h["path"]) for h in refs[1:])
    assert qualified["staticApplicable"]==qualified["staticUnclassified"]==0 and qualified["tests"]==162
    assert qualified["static"]==refs[4] and qualified["staticAdmission"]==refs[6]
    assert a1["static"]==refs[4] and a2["static"]==refs[5]
    assert independent["stillUnclassified"]==181 and independent["productionCore"]==current["productionCore"]
    assert c1["fullRootRulesetSha256"]==c2["fullRootRulesetSha256"]
    xml_pin=current["reports"]["pmd.xml"]
    assert pin(Path(xml_pin["path"]))==xml_pin
    xml=ElementTree.parse(xml_pin["path"]).getroot()
    rows=[static_key(f.get("name"),row.get("beginline"),row.get("rule"),(row.text or "").strip())
          for f in xml if f.tag.endswith("file") for row in f]
    assert len(rows)==281
    unresolved_path=Path(independent["unresolved"]["path"])
    assert pin(unresolved_path)==independent["unresolved"]
    pending=read(unresolved_path)
    selected=[row for row in pending if "/migration/" in row["path"]]
    assert len(selected)==142
    sources={row["path"]:git("show",f"{core}:{row['path']}") for row in selected}
    assert all(val==git("show",f"{current['productionCore']}:{path}") for path,val in sources.items())
    prior=[]
    for baseline,dispositions,ref,a_ref in ((c1,a1,refs[4],refs[6]),(c2,a2,refs[5],refs[7])):
        counts=Counter(static_key(r["path"],r["line"],r["rule"],r["message"]) for r in baseline["rawFindings"])
        anchors={static_key(r["path"],r["sourceLine"],r["rule"],r["message"]):r
                 for r in dispositions["sourceAnchors"]}
        prior.append((baseline["inputHashes"],counts,anchors,ref,a_ref))
    observed=Counter(rows)
    verified,retained=[],[]
    keys=set()
    for source_row in selected:
        occurrence=source_row["occurrence"]
        path=source_row["path"]
        key=rows[occurrence-1]
        assert key[:3]==(path,int(source_row["line"]),source_row["rule"])
        available=[]
        for hashes,counts,anchors,ref,a_ref in prior:
            evidence=anchors.get(key)
            if hashes.get(path)!=sha(sources[path]) or evidence is None or counts[key]!=observed[key]:
                continue
            value=evidence.get("rawMultiplicity",evidence["occurrences"])
            if value!=observed[key] or evidence["disposition"]!="NOT_APPLICABLE":
                continue
            line=sources[path].decode().splitlines()[int(source_row["line"])-1]
            assert line.strip()==evidence["sourceAnchor"].strip()
            available.append((evidence,ref,a_ref))
        if not available:
            retained.append(source_row)
            continue
        evidence,ref,a_ref=available[0]
        keys.add(key)
        verified.append(dict(**source_row,fullSameFileSha256=sha(sources[path]),rawCount=observed[key],
                             reason=evidence["reason"],static=ref,priorAssessment=a_ref))
    assert len(verified)+len(retained)==142 and len({row["occurrence"] for row in verified})==len(verified)
    wanted={r["occurrence"] for r in verified}
    remainder=[r for r in pending if r["occurrence"] not in wanted]
    out=OPS/w["run"]
    out.mkdir()
    dump(out/"classified.json",verified)
    dump(out/"remaining.json",remainder)
    d=dict(actualExit=0,source=w["source"],productionCore=core,originalActualPmdSource=current["productionCore"],
           all142MigrationCandidatesExamined=True,oldUnknown=181,newlyLinked=len(verified),
           unclassifiedRemainForOriginalReport=len(remainder),migrationRemain=len(retained),
           typedSourceFilesExamined=len(sources),coveredPaths=sorted({r["path"] for r in verified}),
           findingsByOriginalEvidence=dict(Counter(r["static"]["path"] for r in verified)),
           historicalRunNotReexecuted=True,originalAllModulePmDExit4Kept=True,
           actualProductTests=0,wholeF03Accepted=False,whole451Accepted=False,
           basis=refs,confirmed=pin(out/"classified.json"),unclassified=pin(out/"remaining.json"),
           terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",d)
    print(pin(out/"manifest.json"),len(verified),len(retained),len(remainder))


if __name__=="__main__":
    main()
