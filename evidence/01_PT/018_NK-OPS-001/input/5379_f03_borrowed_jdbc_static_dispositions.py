"""Connect retained JDBC finding occurrences with exact scope and resource tests."""

from collections import Counter
from pathlib import Path
import runpy
from xml.etree import ElementTree


G=runpy.run_path(str(Path(__file__).with_name("5378_f03_migration_exact_saved_pmd_anchors.py")))
OPS,UPPER,COMMON,PLAN=(G[k] for k in ("OPS","UPPER","COMMON","PLAN"))
TARGETS={"SchemaHistoryAdmission.java":12,"ServiceDatabaseAdmission.java":9,"ServiceDatabaseSource.java":4}


def signatures(path, target=None):
    root=ElementTree.parse(path).getroot()
    return [
        (node.get("name"),v.get("rule"),v.get("method"),int(v.get("beginline")),(v.text or "").strip())
        for node in root if node.tag.endswith("file") and (target is None or node.get("name").endswith(target))
        for v in node
    ]


def main():
    read=UPPER["read"]
    pin,git,sha,dump=(COMMON[k] for k in ("pin","git","sha","dump"))
    start=read(next(PLAN.glob("902_*")))
    w=start["values"]
    refs=w["oracleReferences"]
    assert all(pin(Path(ref["path"]))==ref for ref in refs)
    previous, migration, raw, schema_now, service, service_raw, service_start, schema_raw = (
        read(ref["path"]) for ref in refs[1:])
    core=w["productionCoreMain"]
    assert core==schema_now["productionCore"] and service["tests"]==32
    assert pin(Path(service["actualWholeCases"]["path"]))==service["actualWholeCases"]
    assert service["applicableOrUnclassified"]==0 and service["noRealJdbcOrServiceOperations"]
    assert raw["actualExit"]==0 and previous["unresolvedForFixedRawReport"]==49
    remainder_path=Path(migration["unclassified"]["path"])
    assert pin(remainder_path)==migration["unclassified"]
    residue=read(remainder_path)
    selected=[row for row in residue if Path(row["path"]).name in TARGETS]
    assert Counter(Path(r["path"]).name for r in selected)==TARGETS
    original=signatures(raw["reports"]["pmd.xml"]["path"])
    assert len(original)==281
    current_schema_xml=next(OPS.glob("PG40500-*/pmd.xml"))
    fresh=Counter((rule,method,msg) for _,rule,method,_,msg in signatures(current_schema_xml,"SchemaHistoryAdmission.java"))
    service_xml=Path(service_raw["scope"]["pmd"]["raw"]["path"])
    assert pin(service_xml)==service_raw["scope"]["pmd"]["raw"]
    admission_receipt=next(OPS.glob("PG39476-*/manifest.json"))
    admission=read(admission_receipt)
    assert admission["actualExit"]==admission["staticApplicable"]==0
    assert admission["tests"]==31
    admission_static=admission["proofs"]["static"]
    assert pin(Path(admission_static["path"]))==admission_static
    admission_data=read(admission_static["path"])
    admission_xml=Path(admission_static["path"]).parent/"pmd.xml"
    old_resources={}
    for target, input_file in (("ServiceDatabaseAdmission.java",admission_xml),
                               ("ServiceDatabaseSource.java",service_xml)):
        old_resources[target]=Counter((rule,method,line,msg) for _,rule,method,line,msg in signatures(input_file,target))
    exact_schema_base=next(OPS.glob("PG38670-*/manifest.json"))
    exact_schema=read(exact_schema_base)
    assert exact_schema["actualExit"]==0 and exact_schema["tests"]==11 and exact_schema["static"]==refs[8]
    verified=[]
    for item in selected:
        file=item["path"]
        name=Path(file).name
        actual=original[item["occurrence"]-1]
        assert actual[0].endswith("/"+file) and actual[1]==item["rule"] and actual[3]==int(item["line"])
        _,rule,method,line,msg=actual
        source=git("show",f"{core}:{file}")
        if name=="SchemaHistoryAdmission.java":
            former=git("show",f"{raw['productionCore']}:{file}")
            assert former==git("show",f"{exact_schema['productionCoreMain']}:{file}")
            normalized=source.decode().replace(
                "      require(!Thread.currentThread().isInterrupted());\n      return List.copyOf(observed);",
                "      return List.copyOf(observed);").replace("PT-OPS-SCHEMA001..013","PT-OPS-SCHEMA001..008")
            assert normalized.encode()==former
            standard=Counter((Path(r["path"]).name,r["rule"],int(r["line"]),r["message"]) for r in schema_raw["rawFindings"])
            assert standard[(name,rule,line,msg)]==1
            fresh[(rule,method,msg)]-=1
            assert fresh[(rule,method,msg)]>=0
            link=refs[4]
        else:
            old=git("show",f"{service['source']}:{file}")
            assert source==old and source==git("show",f"{raw['productionCore']}:{file}")
            if name=="ServiceDatabaseAdmission.java":
                assert sha(old)==admission_data["inputHashes"][file]
                link=pin(admission_receipt)
            else:
                assert sha(old)==service_start["sourceHashes"][file]
                link=refs[5]
            assert old_resources[name][(rule,method,line,msg)]==1
        if rule=="DoNotUseThreads":
            reason="Reading the caller interrupt flag is specified in SSC-474 and starts no thread"
        elif rule=="CloseResource":
            reason="The acquired statement and result are each closed through their typed finally helper as shown by the ordinary resource oracle"
        else:
            assert rule=="AvoidCatchingGenericException"
            reason="Required owned release and original Throwable precedence are verified by the independent borrowed or source fixture"
        verified.append(dict(**item,verifiedCurrentSource=sha(source),sourceFinding=msg,confirmedScope=link,
                             decision="NOT_APPLICABLE_PER_SITE",reason=reason))
    more={k:v for k,v in fresh.items() if v}
    assert list(more.values())==[1] and next(iter(more))[:2]==("DoNotUseThreads","inspect")
    used={row["occurrence"] for row in verified}
    kept=[row for row in residue if row["occurrence"] not in used]
    assert len(verified)==25 and len(kept)==24
    out=OPS/w["run"]
    out.mkdir()
    dump(out/"confirmed25.json",verified)
    dump(out/"remaining24.json",kept)
    data=dict(actualExit=0,source=w["source"],productionCore=core,originalReportCore=raw["productionCore"],
              rawCount=281,oldUnclassified=49,newRebound=25,remainingForRawReport=24,
              currentSchemaNewFlagRaw=1,currentSchemaNewFlagAlreadyIndependentlyReviewed=True,
              sourceMatchesAndRequiredExceptionsRetained=True,sourceEvidence=[*refs,pin(admission_receipt)],
              confirmed=pin(out/"confirmed25.json"),remaining=pin(out/"remaining24.json"),
              priorTestsRerun=0,actualStaticToolRan=0,noSuppressions=True,wholeF03Accepted=False,whole451Accepted=False,
              terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",data)
    print(pin(out/"manifest.json"),len(verified),len(kept))


if __name__=="__main__":
    main()
