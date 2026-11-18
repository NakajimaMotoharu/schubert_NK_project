"""Bind the original Web standard metrics cases to one finite worker scope and actual unfiltered evidence."""
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
OUT = E / "PG39536-f03-web-standard-source-independent-v1"
METHODS = re.compile(r"^  void (webhost\d{3})[^\n]*\n(.*?)(?=^  @Test|^  private |^\})", re.M | re.S)


def verify_inputs(c, post):
    start = h.load(next(D.glob("457_*")))
    repo_path = c["testSources"][0]["path"]
    initial = h.git("show", f"{start['values']['source']}:{repo_path}")
    fixed = h.git("show", f"{post['source']}:{repo_path}")
    assert fixed == Path(repo_path).read_text()
    before, after = map(lambda text: dict(METHODS.findall(text)), (initial, fixed))
    assert len(before) == len(after) == 16 and before.keys() == after.keys()
    changed = {n for n in before if before[n] != after[n]}
    assert changed == {"webhost004", "webhost016"}, changed
    original=before["webhost004"]
    current=after["webhost004"]
    for phrase in ('owner.bind(null)','owner.scrape(null)','owner.bind("unknown")','owner.scrape("")','assertEquals(0, count.get())'):
        assert phrase in original and phrase in current
    assert 'List.of("DEBTf", "STANDAQc")' in current
    assert 'owner.bind(mode)' in current and 'owner.scrape(mode)' in current and '"invalid monitoring mode"' in current
    body=after["webhost016"]
    assert "executor.shutdownNow();" in body and "executor.awaitTermination(10, TimeUnit.SECONDS)" in body
    assert "try (var executor = Executors." not in body
    assert h.assertion_calls(before["webhost016"]) == h.assertion_calls(body)
    return sorted(changed)


def main():
    p = B / "input/5169_bug3287_web_standard_source_profile.json"
    c = h.load(p)
    paths = {k:Path(v)/"manifest.json" for k,v in c["slots"].items()}
    m = {k:h.load(f) for k,f in paths.items()}
    source = m["post"]["source"]
    unit = m["unit"]
    assert all(v["actualExit"] == 0 for v in m.values())
    assert unit["tests"] == m["post"]["tests"] == 16
    assert all(unit[key] == 0 for key in ("failures","errors","skipped"))
    assert m["preflight"]["staticApplicable"]==0 and len(m["static"]["rawFindings"])==9
    assert not h.git("diff","--name-only",c["productionCoreMain"],source,"--",":(glob)src/*/src/main/java/**/*.java")
    assert len(ElementTree.parse(paths["post"].parent/"original-TEST-junit-jupiter.xml").getroot().findall("testcase"))==16
    changed=verify_inputs(c,m["post"])
    OUT.mkdir()
    command=h.load(E/"PG39282-f03-api-recorder-unfiltered-with-generated-v1/raw-command.json")[:5]
    component=(Path("../pgpt-runs/PG379")/c["privateDirs"]["prepare"]/"component").resolve()
    command += [str(paths["post"].parent/"jacoco.exec"),*[str(component/v) for v in c["physicalClasses"]]]
    h.write(OUT/"raw-command.json",command)
    raw=OUT/"unfiltered.tsv"
    with raw.open("xb") as stream:
        subprocess.run(command,stdout=stream,check=True,timeout=80)
    counters={};mode=None
    deficits=[]
    for row in raw.read_text().splitlines():
        f=row.split("\t")
        if f[0]=="CLASS":
            counters[f[1]]={k:dict(missed=int(a),covered=int(b)) for k,a,b in [v.split(":") for v in f[6:]]}
        if f[0]=="METHOD" and f[1].endswith("/HttpMetricContract") and f[2]=="detailedMetricsEnabled":
            assert mode is None
            mode={k:dict(missed=int(a),covered=int(b)) for k,a,b in [v.split(":") for v in f[5:]]}
        if f[0]=="DEFICIT":
            deficits.append(dict(type=f[1],method=f[2],line=int(f[4]),counters=f[5:]))
    assert len(counters)==m["post"]["physicalClasses"]==12 and m["post"]["positiveMainCrc"]==6
    body=next(v for k,v in counters.items() if k.endswith("/WebStandardMetricSource"))
    own_full = all(x["missed"]==0 for x in body.values())
    assert mode and mode["BRANCH"]["missed"]==0
    past=E/"PG39481-bug3284-web-payload-prepare-v2/manifest.json"
    previous=h.load(past)["physicalClassHashes"]
    assert len(previous)==22
    assert all(previous[n]==sha for n,sha in m["prepare"]["physicalClassHashes"].items())

    archives=h.archive_streams(c)
    h.write(OUT/"retention.json",archives)
    result=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=source,productionCoreMain=c["productionCoreMain"],
        tests=16,failures=0,errors=0,skipped=0,notRun=0,firstProductRunSuccess=True,independentPostSuccess=True,newDefinitions=0,
        changedOriginalMethods=changed,allOtherCasesExact=True,originalGoldenAssertionsRetained=True,boundedExecutor=True,
        failureReleaseOwnershipProved=True,independentModeCollisionInputs=["DEBTf","STANDAQc"],staticApplicable=0,staticPMDRaw=9,
        actualPhysicalClasses=12,positiveCrc=6,rawTarget=body,rawMode=mode,rawSupport=counters,rawDeficits=deficits,
        priorRequalifiedPhysical12=h.ref(past),currentExecutableTargetAll=own_full,archive=h.ref(OUT/"retention.json"),evidence=h.ref(raw),
        rawCommand=h.ref(OUT/"raw-command.json"),proofs={k:h.ref(v) for k,v in paths.items()},verifier=h.ref(__file__),
        formalUpdated=False,newAcceptance=0,whole451Accepted=False)
    h.write(OUT/"manifest.json",result)
    print(h.ref(OUT/"manifest.json"), body, mode, len(deficits))


if __name__=="__main__":
    main()
