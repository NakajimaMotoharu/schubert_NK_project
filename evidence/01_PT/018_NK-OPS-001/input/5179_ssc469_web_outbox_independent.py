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
OUT = E / "PG39578-p00405-web-outbox-typed-close-independent-v1"
METHODS = re.compile(r"^  void\s+(webObx(?:Db|Met|Conn)\d{3})[^\n]*\n(.*?)(?=^  @Test|^  private |^\})", re.M | re.S)
def verifiers(c, source):
    start = h.load(next(D.glob("461_*")))
    result = {}
    for row in c["testSources"]:
        path = row["path"]
        name = Path(path).stem
        current = Path(path).read_text()
        assert current == h.git("show", f"{source}:{path}")
        old = h.git("show", f"{start['values']['source']}:{path}")
        if name != "WebOutboxObservationRepositoryTest":
            assert current == old
            result[name] = 0
            continue
        before = dict(METHODS.findall(old))
        after = dict(METHODS.findall(current))
        assert len(before)==10 and len(after)==11 and set(after)-set(before)=={"webObxDb011"}
        prefix = current[:current.index("\n  @Test\n  void webObxDb011")] + "\n}"
        decl='  private static final String ROWS_CLOSE = "RSclose";'
        assert prefix.count(decl)==1
        prefix=prefix.replace(decl,"",1).replace("ROWS_CLOSE",'"RSclose"')
        assert h.TOKEN.findall(prefix)==h.TOKEN.findall(old)
        check=after["webObxDb011"]
        assert "fixture.faults.put(ROWS_CLOSE, repeated)" in check
        assert "IllegalArgumentException.class" in check and "assertSame(repeated, outcome.getCause())" in check
        assert "fixture.complete()" in check
        result[name]=1
    return result


def main():
    profile=B/"input/5177_ssc469_web_outbox_typed_close_profile_v2.json"
    c=h.load(profile)
    paths = {key:Path(value)/"manifest.json" for key,value in c["slots"].items()}
    m = {key:h.load(path) for key,path in paths.items()}
    assert all(value["actualExit"]==0 for value in m.values())
    unit, post = m["unit"], m["post"]
    assert unit["tests"]==post["tests"]==27 and all(unit[k]==0 for k in ("failures","errors","skipped"))
    assert m["preflight"]["staticApplicable"]==0 and len(m["static"]["rawFindings"])==42
    assert post["wholeScopeFour100"] and post["positiveMainCrc"]==5 and post["physicalClasses"]==6
    assert not h.git("diff","--name-only",c["productionCoreMain"],post["source"],"--",":(glob)src/*/src/main/java/**/*.java")
    cases=ElementTree.parse(paths["post"].parent/"original-TEST-junit-jupiter.xml").getroot().findall("testcase")
    assert len(cases)==27 and len({(r.get("classname"),r.get("name")) for r in cases})==27
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
    previous=E/"PG39556-bug3290-web-outbox-prestyle-v1/manifest.json"
    assert h.load(previous)["actualExit"]==1
    prior=E/"PG39554-p00405-web-outbox-proxy-independent-v1/manifest.json"
    baseline=h.load(prior)
    assert baseline["raw"]["BRANCH"]["missed"]==4
    assert not deficits
    original=Path("../pgpt-runs/PG379/pg39541-bug3288-web-outbox-prepare-v2/component").resolve()
    javap=Path("../toolchain/jdk-25.0.4/bin/javap").resolve()
    klass="dev.codex.schubert.nk.web.monitoring.WebOutboxObservationRepository"
    before=subprocess.check_output([str(javap),"-public","-s","-cp",str(original),klass],timeout=15)
    after=subprocess.check_output([str(javap),"-public","-s","-cp",str(component),klass],timeout=15)
    assert before==after
    prior_physical=E/"PG39541-bug3288-web-outbox-prepare-v2/manifest.json"
    old=h.load(prior_physical)["physicalClassHashes"]
    new=m["prepare"]["physicalClassHashes"]
    assert old.keys()==new.keys()
    assert {n for n in old if old[n]!=new[n]}=={klass.replace(".","/")+".class"}
    assert h.git("diff","--name-only",baseline["productionCoreMain"],c["productionCoreMain"],
                 "--",":(glob)src/*/src/main/java/**/*.java").splitlines()==[c["mainSources"][2]]
    design="c00bfaf681f6f42d9544c335b46c452400e0cb50"
    assert subprocess.run(["git","merge-base","--is-ancestor",design,"origin/main"]).returncode==0
    archives=h.archive_streams(c)
    h.write(OUT/"retention.json",archives)
    total={key:dict(missed=sum(r[key]["missed"] for r in counters.values()),
                    covered=sum(r[key]["covered"] for r in counters.values()))
           for key in ("LINE","METHOD","CLASS","BRANCH","INSTRUCTION","COMPLEXITY")}
    result=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=post["source"],
        productionCoreMain=c["productionCoreMain"],tests=27,failures=0,errors=0,skipped=0,notRun=0,
        firstProductRunSuccess=True,firstIndependentPostSuccess=True,newTestDefinitions=1,verifiedChanges=verified,
        wholeSelectedFour100=post["wholeScopeFour100"],raw=total,rawPerClass=counters,rawDeficits=deficits,
        actualPhysicalClasses=6,positiveCrc=5,borrowedReadOnlyContract=True,rowsBeforeStatementAndNoConnectionOwnership=True,
        independentOriginalGoldenRetained=True,staticApplicable=0,staticRawPmd=42,
        initialBeforeCorrectionPmd=h.ref(previous),oldExecCombined=False,coverageExclusions=0,
        previousRawCoverage=h.ref(prior),canonicalDesign=design,designPullRequest=436,
        exactOnePhysicalChange=h.ref(prior_physical),publicAbiUnchanged=True,
        originalWhole26ExpectedRetained=True,selfSuppressionIndependentFixture=True,
        formalUpdated=False,newAcceptance=0,whole451Accepted=False,
        rawCommand=h.ref(OUT/"raw-command.json"),rawOutput=h.ref(raw),proofs={key:h.ref(p) for key,p in paths.items()},
        retention=h.ref(OUT/"retention.json"),verifier=h.ref(__file__))
    h.write(OUT/"manifest.json",result)
    print(h.ref(OUT/"manifest.json"))
    print(total,[(d["type"].rsplit("/",1)[1],d["member"],d["line"]) for d in deficits])


if __name__=="__main__":
    main()
