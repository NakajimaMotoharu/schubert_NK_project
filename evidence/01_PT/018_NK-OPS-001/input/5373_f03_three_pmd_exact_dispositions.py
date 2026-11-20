"""Independently reconcile the current raw static report and retained per-site decisions."""

from collections import Counter
from pathlib import Path
import runpy
from xml.etree import ElementTree


R = runpy.run_path(str(Path(__file__).with_name("5372_f03_three_main_pmd_and_checkstyle.py")))
OPS, UPPER, COMMON = (R[name] for name in ("OPS","UPPER","COMMON"))


def xml_site(path, row):
    name = "src/" + path.split("/src/",1)[1]
    return (name,row.get("rule"),row.get("beginline"),row.get("begincolumn"),row.get("method") or "",
            (row.text or "").strip())


def static_site(row):
    return (row["path"],row["rule"],str(row["beginline"]),str(row["begincolumn"]),row.get("method") or "",
            row["message"])


def main():
    read=UPPER["read"]
    pin, git, sha, dump = (COMMON[n] for n in ("pin","git","sha","dump"))
    here=next(OPS.glob("PG40486-*/manifest.json"))
    report=read(here)
    core=report["productionCore"]
    assert report["actualExit"]==0 and report["pmdRawCount"]==281
    assert report["stages"]["pmd"]["actualExit"]==4 and report["stages"]["checkstyle"]["actualExit"]==0
    assert all(pin(Path(ref["path"]))==ref for ref in report["reports"].values())
    pmd=ElementTree.parse(report["reports"]["pmd.xml"]["path"]).getroot()
    cs=ElementTree.parse(report["reports"]["checkstyle.xml"]["path"]).getroot()
    assert len(cs.findall("file"))==282 and not list(cs.iter("error"))
    assert not any(row.tag.endswith(("error","configerror")) for row in pmd)
    raw=[xml_site(node.get("name"),row) for node in pmd if node.tag.endswith("file") for row in node]
    assert len(raw)==281 and len(set(raw))==277
    original_failure=next(OPS.glob("PG40487-*/manifest.json"))
    assert read(original_failure)["identicalRepeatedRawLocations"]==4
    source_hashes={path:sha(git("show",f"{core}:{path}")) for path in {row[0] for row in raw}}
    basis={name:next(OPS.glob(f"PG{num}-*/{fname}")) for name,num,fname in (
        ("retained",37092,"all-current-dispositions.json"),("protocol",38300,"raw-findings.json"),
        ("storage",36824,"pmd18-site-dispositions.json"),("jdbc",40456,"manifest.json"),
        ("release",40424,"manifest.json"))}
    dispositions={}
    retained={
        (row["path"],row["rule"],str(row["line"]),str(row["column"]),row.get("method") or "",row["sourceSha256"]): row
        for row in read(basis["retained"]) if row["decision"].startswith("NOT_APPLICABLE")
    }
    old_protocol=read(basis["protocol"].parent/"manifest.json")
    protocol={
        static_site(row):sha(git("show",f"{old_protocol['source']}:{row['path']}"))
        for row in read(basis["protocol"])
    }
    old_storage=read(basis["storage"])
    storage={static_site(row["raw"]):row for row in old_storage}
    storage_counts=Counter(static_site(row["raw"]) for row in old_storage)
    assert all(n==Counter(raw)[key] for key,n in storage_counts.items())
    jdbc=read(basis["jdbc"])
    assert jdbc["source"]==core
    expected_jdbc=Counter((r["file"],r["rule"],r["method"],r["rawMessage"])
                          for r in jdbc["pmdIndependentDispositions"])
    release=read(basis["release"])
    for occurrence,site in enumerate(raw,1):
        path, rule, _, _, method, text=site
        old=retained.get((*site[:5],source_hashes[path]))
        key=(Path(path).name,rule,method,text)
        if old:
            dispositions[occurrence]=("retained",old["reason"])
        elif site in protocol and protocol[site]==source_hashes[path]:
            note="Ordered map is local" if rule=="UseConcurrentHashMap" else "Throwable identity avoids self-suppression"
            assert rule in ("UseConcurrentHashMap","CompareObjectsWithEquals")
            dispositions[occurrence]=("protocol",note)
        elif site in storage and storage[site]["sourceSha256"]==source_hashes[path]:
            assert storage[site]["disposition"]=="NOT_APPLICABLE"
            dispositions[occurrence]=("storage",storage[site]["reason"])
        elif expected_jdbc.get(key,0)>0:
            expected_jdbc[key]-=1
            dispositions[occurrence]=("jdbc","Preserves contractually ordered ownership release and Throwable identity")
        elif key[:3]==("ReleaseInventory.java","UnusedReturnValue","parse"):
            body=git("show",f"{core}:{path}").decode()
            assert "reader.setStrictness(Strictness.STRICT)" in body and "reader.peek();" in body
            assert sha(git("show",f"{release['source']}:{path}"))==source_hashes[path]
            test=path.replace("/main/","/test/").replace("ReleaseInventory.java","ReleaseInventoryTest.java")
            contents=git("show",f"{release['source']}:{test}").decode()
            assert 'refused(golden() + " {}");' in contents
            dispositions[occurrence]=("release","Pinned strict JSON reader checks trailing content before acceptance. Its return value is immaterial to validation")
    summary=Counter(tag for tag,_ in dispositions.values())
    assert summary=={"retained":58,"protocol":3,"storage":18,"jdbc":20,"release":1}
    assert all(n==0 for n in expected_jdbc.values())
    out=OPS/"PG40488-f03-current-282-static-independent-v1"
    out.mkdir()
    unresolved=[dict(occurrence=i,path=k[0],rule=k[1],line=k[2],column=k[3],method=k[4])
                for i,k in enumerate(raw,1) if i not in dispositions]
    assert len(unresolved)==181
    dump(out/"unresolved181.json",unresolved)
    rows=[dict(occurrence=i,path=s[0],rule=s[1],line=s[2],column=s[3],method=s[4],basis=pin(basis[tag]),
               sourceSha256=source_hashes[s[0]],status="NOT_APPLICABLE_PER_SITE",reason=reason)
          for i,s in enumerate(raw,1) if i in dispositions for tag,reason in (dispositions[i],)]
    dump(out/"classified100.json",rows)
    d=dict(actualExit=0, source=report["source"],productionCore=core,analysis=pin(here),
           pmdExitPreserved=4,currentRaw=281,classifiedNonApplicable=100,stillUnclassified=181,
           failedPrecheck=pin(original_failure),distinctRawLocationKeys=277,
           classificationOrigins=summary,checkstyleCurrentSources=282,checkstyleFindings=0,
           classified=pin(out/"classified100.json"),unresolved=pin(out/"unresolved181.json"),
           noSuppressionsOrScopeCertification=True,actualProductTests=0,wholeF03Accepted=False,
           whole451Accepted=False,terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",d)
    print(pin(out/"manifest.json"),dict(summary))


if __name__=="__main__":
    main()
