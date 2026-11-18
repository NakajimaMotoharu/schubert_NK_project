"""Verify the supplied Web Outbox fixture and raw coverage against one fixed execution."""
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree

B = Path("evidence/01_PT/018_NK-OPS-001")
E = B / "evidence"
D = Path("documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117")
S = spec_from_file_location("proof", B / "input/5139_bug3272_context_independent_checks.py")
h = module_from_spec(S)
S.loader.exec_module(h)
OUT = E / "PG39554-p00405-web-outbox-proxy-independent-v1"
METHODS = re.compile(r"^  void\s+(webObx(?:Db|Met|Conn)\d{3})[^\n]*\n(.*?)(?=^  @Test|^  private |^\})", re.M | re.S)
EXPECTED = {"WebOutboxMetricRecorderTest": {"webObxMet004"},
            "WebOutboxMetricCollectorTest": {"webObxConn004","webObxConn006","webObxConn007"},
            "WebOutboxObservationRepositoryTest": {"webObxDb004","webObxDb010"}}


def verifiers(c, source):
    start = h.load(next(D.glob("459_*")))
    result = {}
    for row in c["testSources"]:
        path = row["path"]
        name = Path(path).stem
        current = Path(path).read_text()
        assert current == h.git("show", f"{source}:{path}")
        old = h.git("show", f"{start['values']['source']}:{path}")
        before, after = [dict(METHODS.findall(arg)) for arg in (old,current)]
        assert len(before) == len(after) == row["tests"] and before.keys() == after.keys()
        changed = {k for k in before if before[k] != after[k]}
        assert changed == EXPECTED[name], (name, changed)
        for case in changed:
            update = after[case]
            if case.endswith("004") and name != "WebOutboxObservationRepositoryTest":
                assert update.replace(', "DEBTf", "STANDAQc"', "", 1) == before[case]
            elif case == "webObxDb004":
                clauses = ['f -> f.autoCommit = true','f -> f.readOnly = false',
                           'f -> f.isolation = Connection.TRANSACTION_SERIALIZABLE']
                assert all(x in update for x in clauses)
                assert 'cursor++;\n                    return cursor < rows.size();' in current
                assert h.assertion_calls(update) == h.assertion_calls(before[case])
            else:
                worker = "pool" if case=="webObxDb010" else "executor"
                assert f"{worker}.shutdownNow();" in update
                assert f"{worker}.awaitTermination(5, TimeUnit.SECONDS)" in update
                assert all(a in h.assertion_calls(update) for a in h.assertion_calls(before[case]))
        result[name] = sorted(changed)
    return result


def main():
    profile=B/"input/5173_bug3288_web_outbox_profile_v2.json"
    c=h.load(profile)
    paths = {key:Path(value)/"manifest.json" for key,value in c["slots"].items()}
    m = {key:h.load(path) for key,path in paths.items()}
    assert all(value["actualExit"]==0 for value in m.values())
    unit, post = m["unit"], m["post"]
    assert unit["tests"]==post["tests"]==26 and all(unit[k]==0 for k in ("failures","errors","skipped"))
    assert m["preflight"]["staticApplicable"]==0 and len(m["static"]["rawFindings"])==38
    assert post["wholeScopeFour100"] and post["positiveMainCrc"]==5 and post["physicalClasses"]==6
    assert not h.git("diff","--name-only",c["productionCoreMain"],post["source"],"--",":(glob)src/*/src/main/java/**/*.java")
    cases=ElementTree.parse(paths["post"].parent/"original-TEST-junit-jupiter.xml").getroot().findall("testcase")
    assert len(cases)==26 and len({(r.get("classname"),r.get("name")) for r in cases})==26
    verified=verifiers(c,post["source"])
    OUT.mkdir()
    component=(Path("../pgpt-runs/PG379")/c["privateDirs"]["prepare"]/"component").resolve()
    args=h.load(E/"PG39282-f03-api-recorder-unfiltered-with-generated-v1/raw-command.json")[:5]
    args += [str(paths["post"].parent/"jacoco.exec"),*[str(component/p) for p in c["physicalClasses"]]]
    h.write(OUT/"raw-command.json",args)
    raw=OUT/"unfiltered.tsv"
    with raw.open("xb") as stream:
        subprocess.run(args,stdout=stream,check=True,timeout=80)
    counters = {}
    deficits = []
    for line in raw.read_text().splitlines():
        f=line.split("\t")
        if f[0]=="CLASS":
            counters[f[1]]={key:dict(missed=int(miss),covered=int(hit)) for key,miss,hit in [v.split(":") for v in f[6:]]}
        if f[0]=="DEFICIT":
            deficits.append(dict(type=f[1],member=f[2],line=int(f[4]),counters=f[5:]))
    assert len(counters)==6
    previous=E/"PG39542-bug3288-web-outbox-static-v1/manifest.json"
    assert len(h.load(previous)["rawFindings"])==41
    archives=h.archive_streams(c)
    h.write(OUT/"retention.json",archives)
    total={key:dict(missed=sum(r[key]["missed"] for r in counters.values()),
                    covered=sum(r[key]["covered"] for r in counters.values()))
           for key in ("LINE","METHOD","CLASS","BRANCH","INSTRUCTION","COMPLEXITY")}
    result=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=post["source"],
        productionCoreMain=c["productionCoreMain"],tests=26,failures=0,errors=0,skipped=0,notRun=0,
        firstProductRunSuccess=True,firstIndependentPostSuccess=True,newTestDefinitions=0,verifiedChanges=verified,
        wholeSelectedFour100=post["wholeScopeFour100"],raw=total,rawPerClass=counters,rawDeficits=deficits,
        actualPhysicalClasses=6,positiveCrc=5,borrowedReadOnlyContract=True,rowsBeforeStatementAndNoConnectionOwnership=True,
        independentOriginalGoldenRetained=True,staticApplicable=0,staticRawPmd=38,
        initialBeforeCorrectionPmd=h.ref(previous),oldExecCombined=False,coverageExclusions=0,
        verifierPreparationNote="The first audit required method identifier after void on one line. The revised audit accepts the original line-broken method declarations and reuses the same qualified JUnit evidence.",
        formalUpdated=False,newAcceptance=0,whole451Accepted=False,
        rawCommand=h.ref(OUT/"raw-command.json"),rawOutput=h.ref(raw),proofs={key:h.ref(p) for key,p in paths.items()},
        retention=h.ref(OUT/"retention.json"),verifier=h.ref(__file__))
    h.write(OUT/"manifest.json",result)
    print(h.ref(OUT/"manifest.json"))
    print(total,[(d["type"].rsplit("/",1)[1],d["member"],d["line"]) for d in deficits])


if __name__=="__main__":
    main()
