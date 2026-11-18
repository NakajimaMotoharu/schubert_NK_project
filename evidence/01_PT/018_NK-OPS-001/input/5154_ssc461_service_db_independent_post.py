"""Independent admission of the immutable bootstrap JDBC port evidence and actual raw counters."""
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET

spec=spec_from_file_location("ports", Path(__file__).with_name("5151_ssc461_service_db_ports.py"))
m=module_from_spec(spec)
spec.loader.exec_module(m)
OUT=m.E / "PG39452-f02-service-db-port-graph-independent-v1"


def main():
    build=m.load(m.BUILD)
    source=build["sourceCore"]
    hashes=m.checked_build(build)
    terminal=m.load(m.PUBLIC/"manifest.json")
    private=m.load(m.UNIT/"input.json")
    assert terminal["source"]==private["source"]==source and private["inputHashes"]==hashes
    assert m.ref(m.BUILD)==private["build"] and m.ref(m.FRESH_PEERS)==private["freshPeers"]
    assert all(m.digest(Path(p))==h for p,h in private["toolHashes"].items())
    assert terminal["actualExit"]==0 and terminal["tests"]==31
    assert all(terminal[k]==0 for k in ("failures","errors","skipped","notRun"))
    assert m.ref(m.ADMISSION)==private["admission"]
    all_cases=[]
    expected_public={
        "os.name","os.arch","java.version","file.encoding","user.timezone"}
    for name in terminal["originalXmlSha256"]:
        p=m.PUBLIC/name
        assert m.digest(p)==terminal["files"][name]
        root=ET.parse(p).getroot()
        assert not any(root.findall(".//"+name) for name in ("failure","error","skipped","system-out","system-err"))
        assert {row.get("name") for row in root.findall(".//property")} <= expected_public
        all_cases.extend((row.get("classname"),row.get("name")) for row in root.findall("testcase"))
        assert m.digest(m.UNIT/"xml"/name)==terminal["originalXmlSha256"][name]
    assert len(all_cases)==31 and set(all_cases)==set(map(tuple, private["registeredExpectedCases"]))
    first=[n for n,c in terminal["stages"].items() if n in ("unit","execinfo")]
    for stage in first:
        rec=terminal["stages"][stage]
        assert rec["actualExit"]==0 and rec["timedOut"] is False
        assert m.load(m.PUBLIC/(stage+"-exit.safe.json"))==rec
        assert all(m.digest(m.UNIT/(stage+"."+stream))==rec[stream+"Sha256"] for stream in ("stdout","stderr"))
    cmd=terminal["stages"]["unit"]["command"]
    assert cmd.count("--select-class")==2 and not any("--select-method" in a or "--scan-classpath" in a or "excludes=" in a for a in cmd)
    assert not any(v in a.lower() for a in cmd for v in ("postgresql","hikari","artemis","enable-native-access"))
    init=re.findall(r"Initializing '([^']+)'",(m.UNIT/"class-init.log").read_text())
    assert all(v in init for v in (m.PKG + "/ServiceDatabaseAdmission",m.PKG + "/ServiceDatabaseSource",
        m.PKG + "/JdbcFailureGraph","dev/codex/schubert/nk/storage/ServiceConfigFiles$Service"))
    assert not m.HOLDS.intersection(init) and not any(v.startswith("dev/codex/schubert/nk/storage/Linux") for v in init)
    assert m.digest(m.PUBLIC/"jacoco.exec")==terminal["files"]["jacoco.exec"]==m.digest(m.UNIT/"jacoco.exec")
    tracer=(m.UNIT/"execinfo.stdout").read_text()
    assert len([line for line in tracer.splitlines() if line.startswith("Session ")])==1 and m.SCOPE in tracer
    primary=[m.PKG+"/"+n+".class" for n in ("ServiceDatabaseAdmission","ServiceDatabaseAdmission$1","ServiceDatabaseSource",
        "ServiceDatabaseSource$Connector","JdbcAdmissionFailures","JdbcFailureGraph")]
    helper=["dev/codex/schubert/nk/storage/"+n+".class" for n in ("StorageIoException","StorageIoException$Reason","ServiceConfigFiles$Service")]
    dirs=m.boards(build)
    classes=[(role,p,dirs[role]/p) for role,paths in (("bootstrap",primary),("storage",helper)) for p in paths]
    assert all(m.digest(f)==build["physicalClassHashes"][role][p] for role,p,f in classes)
    OUT.mkdir()
    command=m.load(m.E/"PG39282-f03-api-recorder-unfiltered-with-generated-v1/raw-command.json")[:5]
    command += [str(m.PUBLIC/"jacoco.exec"),*[str(p) for _,_,p in classes]]
    m.write(OUT/"raw-command.json", command)
    raw=OUT/"unfiltered.tsv"
    with raw.open("xb") as stream:
        subprocess.run(command,stdout=stream,check=True,timeout=90)
    data={}
    missed=[]
    for line in raw.read_text().splitlines():
        f=line.split("\t")
        if f[0] not in ("CLASS","DEFICIT"):
            continue
        rows={k:dict(missed=int(miss),covered=int(hit)) for k,miss,hit in [v.split(":") for v in f[6 if f[0]=="CLASS" else 5:]]}
        if f[0]=="CLASS":
            label,crc,present=f[1:4]
            if present=="true":
                assert any(l.startswith(crc) and l.split()[-1]==label for l in tracer.splitlines())
            data[label]=dict(crc=crc,positive=present=="true",counters=rows)
        else:
            missed.append(dict(type=f[1],method=f[2],line=int(f[4]),counters=rows))
    assert len(data)==len(classes)
    assert set(data)=={p.removesuffix(".class") for _,p,_ in classes}
    static=m.load(m.OUT/"manifest.json")
    assert all(row["unchanged"] for row in static["abi"])
    peers=m.load(m.FRESH_PEERS)
    originals=static["reports"]
    reconciled={**originals,**peers["reports"]}
    assert source==static["source"]==peers["source"]
    assert all(v["exactScope"] and not any(v[k] for k in ("bugs","errors","missing")) for v in reconciled.values())
    result=dict(actualExit=0,terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=source,productionCoreMain=source,
        tests=31,firstSuccessful=31,originalDefinitions=29,newTestDefinitions=2,failures=0,errors=0,skipped=0,notRun=0,
        sameSourceFourMain=sum(build["mainCounts"].values()),sameSourceFourPhysical=sum(map(len,build["physicalClassHashes"].values())),
        physicalCoverageScope=len(data),positiveCRC=sum(x["positive"] for x in data.values()),rawClasses=data,rawDeficits=missed,
        reportedNewFormalAcceptance=0,effortCompletionRate=None,whole451Accepted=False,existingStorageJdkSqlEdgeRemoved=False,
        movedKnownSQLExceptionCallSites=3,totalMigratedUpperSites=32,upperRemainingSites=72,
        staticApplicable=0,staticRawPMD=len(static["pmdRaw"]),firstMavenStaticMissingClasses={"bootstrap":3,"batch":7},
        sameSourceFreshPeersMissing=0,publicAbiChanged=False,
        proofs={n:m.ref(p) for n,p in (("build",m.BUILD),("staticOriginal",m.OUT/"manifest.json"),("repair",m.FRESH_PEERS),
            ("unit",m.PUBLIC/"manifest.json"),("raw",raw),("rawCommand",OUT/"raw-command.json"))})
    m.write(OUT/"manifest.json",result)
    print(m.ref(OUT/"manifest.json"))
    print({k:v["counters"] for k,v in data.items() if k.rsplit("/",1)[1] in m.NAMES})
    print("Recorded raw deficits",len(missed))


if __name__=="__main__":
    main()
