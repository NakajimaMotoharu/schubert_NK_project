"""Bind the original Web payload cases to three finite workers and actual unfiltered evidence."""
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
OUT = E / "PG39500-f03-web-custom-payload-independent-v1"
METHODS = re.compile(r"^  void (web(?:pay|full)\d{3})[^\n]*\n(.*?)(?=^  @Test|^  private |^\})", re.M | re.S)


def verify_inputs(c, post):
    start = h.load(next(D.glob("453_*")))
    repo_path = c["testSources"][0]["path"]
    initial = h.git("show", f"{start['values']['source']}:{repo_path}")
    fixed = h.git("show", f"{post['source']}:{repo_path}")
    assert fixed == Path(repo_path).read_text()
    before, after = map(lambda text: dict(METHODS.findall(text)), (initial, fixed))
    assert len(before) == len(after) == 26 and before.keys() == after.keys()
    changed = {n for n in before if before[n] != after[n]}
    assert changed == {"webpay005", "webpay013", "webfull011", "webfull012"}, changed
    assert before["webpay005"] == after["webpay005"].replace(', "DEBTf", "STANDAQc"', "", 1)
    worker_expect = {"webpay013":("workers",10), "webfull011":("executor",30), "webfull012":("executor",30)}
    for label, (name, seconds) in worker_expect.items():
        body=after[label]
        shortcut=f"{name}.awaitTermination({seconds}, TimeUnit.SECONDS)"
        assert f"{name}.shutdownNow();" in body and shortcut in body
        assert "try (var "+name+" = Executors." not in body
        old_assert=[a for a in h.assertion_calls(before[label]) if "awaitTermination" not in a]
        new_assert=[a for a in h.assertion_calls(body) if "awaitTermination" not in a]
        assert old_assert == new_assert
    body=after["webfull012"]
    assert body.index("try (var bundle = new Bundle())") < body.index("executor.submit") < body.index("executor.awaitTermination")
    assert body.index("standard.close();") < body.index("executor.awaitTermination") < body.rindex("standard.close();")
    return sorted(changed)


def main():
    p = B / "input/5163_bug3284_web_payload_profile_v2.json"
    c = h.load(p)
    paths = {k:Path(v)/"manifest.json" for k,v in c["slots"].items()}
    m = {k:h.load(f) for k,f in paths.items()}
    source = m["post"]["source"]
    unit = m["unit"]
    assert all(v["actualExit"] == 0 for v in m.values())
    assert unit["tests"] == m["post"]["tests"] == 26
    assert all(unit[key] == 0 for key in ("failures","errors","skipped"))
    assert m["preflight"]["staticApplicable"]==0 and len(m["static"]["rawFindings"])==17
    assert not h.git("diff","--name-only",c["productionCoreMain"],source,"--",":(glob)src/*/src/main/java/**/*.java")
    assert len(ElementTree.parse(paths["post"].parent/"original-TEST-junit-jupiter.xml").getroot().findall("testcase"))==26
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
    assert len(counters)==m["post"]["physicalClasses"]==22 and m["post"]["positiveMainCrc"]==15
    body=next(v for k,v in counters.items() if k.endswith("/WebCustomMetricPayload"))
    assert all(x["missed"]==0 for x in body.values())
    assert mode and mode["BRANCH"]["missed"]==0
    archives=h.archive_streams(c)
    h.write(OUT/"retention.json",archives)
    initial=E/"PG39480-bug3284-web-payload-prepare-v1/test-compile-exit.safe.json"
    assert h.load(initial)["actualExit"]==1
    result=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=source,productionCoreMain=c["productionCoreMain"],
        tests=26,failures=0,errors=0,skipped=0,notRun=0,firstProductRunSuccess=True,independentPostSuccess=True,newDefinitions=0,
        changedOriginalMethods=changed,allOtherCasesExact=True,originalGoldenAssertionsRetained=True,threeBoundedExecutors=True,
        failureReleaseOwnershipProved=True,independentModeCollisionInputs=["DEBTf","STANDAQc"],staticApplicable=0,staticPMDRaw=17,
        actualPhysicalClasses=22,positiveCrc=15,rawTarget=body,rawMode=mode,rawSupport=counters,rawDeficits=deficits,
        initialLintRejectedBeforeProductPT=h.ref(initial),archive=h.ref(OUT/"retention.json"),evidence=h.ref(raw),
        rawCommand=h.ref(OUT/"raw-command.json"),proofs={k:h.ref(v) for k,v in paths.items()},verifier=h.ref(__file__),
        formalUpdated=False,newAcceptance=0,whole451Accepted=False)
    h.write(OUT/"manifest.json",result)
    print(h.ref(OUT/"manifest.json"), body, mode, len(deficits))


if __name__=="__main__":
    main()
