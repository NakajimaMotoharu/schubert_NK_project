"""Recover the original completed package artifacts and preserve missing tool exits."""

import gzip
import json
import os
from pathlib import Path
import runpy
from stat import S_IMODE
from xml.etree import ElementTree
from zipfile import ZipFile


H = runpy.run_path(str(Path(__file__).with_name("5375_schema_history_candidate_packaging.py")))
OPS, PLAN, COMMON, UPPER, TYPE = (H[k] for k in ("OPS","PLAN","COMMON","UPPER","TYPE"))


def main():
    read=UPPER["read"]
    pin,sha,dump,git = (COMMON[k] for k in ("pin","sha","dump","git"))
    p=next(OPS.glob("PG40496-*/wrapper-failure.json"))
    interrupted=read(p)
    assert interrupted["actualExit"]==1 and not interrupted["originalNumericChildStatusesSaved"]
    assert all(pin(Path(row["path"]))==row for row in interrupted["evidence"])
    output=p.parent
    terminal={}
    for phase in ("compile","package"):
        log=output/(phase+".stdout.log.gz")
        assert b"BUILD SUCCESS" in gzip.decompress(log.read_bytes())
        terminal[phase]=dict(log=pin(log),buildSuccessMessage=True,
                             statusZeroImpliedByOriginalChildSuccessBranch=True)
    source=read(next(PLAN.glob("893_*")))["values"]
    old_path=source["oracleReferences"][3]["path"]
    prior=read(old_path)
    assert pin(Path(old_path))==source["oracleReferences"][3]
    accepted=next(OPS.glob("PG40494-*/manifest.json"))
    green=read(accepted)
    core=green["productionCore"]
    assert green["counts"]==dict(tests=13,failures=0,errors=0,skipped=0)
    archived=Path.cwd().parent/"pgpt-runs"/"PG379"/output.name.lower()
    products={}
    classfiles={}
    for module,item in prior["packagedJars"].items():
        name="schubert-nk-"+module
        file=(archived/(name+"-0.1.0-SNAPSHOT.jar")).resolve()
        assert not file.is_symlink() and file.lstat().st_uid==os.getuid() and S_IMODE(file.lstat().st_mode)==0o600
        after=pin(file)
        before=item["artifact"]
        assert pin(Path(before["path"]))==before
        with ZipFile(file) as new, ZipFile(before["path"]) as old:
            a={info.filename:(info.CRC,info.file_size) for info in new.infolist() if info.filename.endswith(".class")}
            b={info.filename:(info.CRC,info.file_size) for info in old.infolist() if info.filename.endswith(".class")}
            assert a.keys()==b.keys() and len(a)==item["classes"]
            difference={name for name in a if a[name]!=b[name]}
            assert difference==({TYPE} if module=="bootstrap" else set())
            for name_ in a.keys() & green["physicalClassHashes"].keys():
                content=new.read(name_)
                classfiles[name_]=sha(content)
            pom="META-INF/maven/dev.codex.schubert/"+name+"/pom.xml"
            assert new.read(pom)==git("show",f"{core}:src/{name}/pom.xml")
        products[module]=dict(artifact=after,classes=len(a),different=sorted(difference),
                              nonTargetComparison="ZIP entry CRC and length, original hash comparison reached before wrapper failure")
    assert sum(a["classes"] for a in products.values())==1102
    assert classfiles==green["physicalClassHashes"]
    abi_before=gzip.decompress((output/"abi-before.stdout.log.gz").read_bytes())
    abi_after=gzip.decompress((output/"abi-after.stdout.log.gz").read_bytes())
    assert abi_before==abi_after and b"public void verify(java.sql.Connection)" in abi_after
    xml=output/"spotbugs.xml"
    root=ElementTree.parse(xml).getroot()
    ids=[x.get("class") for x in root.findall(".//ClassStats")]
    assert ids==["dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission"]
    assert not any(root.findall(q) for q in ("BugInstance",".//Error",".//MissingClass"))
    result=OPS/"PG40498-schema-history-packaged-proof-recovered-v1"
    result.mkdir()
    info=dict(actualExit=0,source=core,productionCore=core,canonicalDesign=green["canonicalDesign"],
              originalWrapper=pin(p),recoveredCompileTerminal=terminal,packagedBuild=products,
              exactPhysicalScope=classfiles,physicalMatchesCoverageAtUnit=pin(accepted),
              publicAbiEqual=True,publicAbiOutputSha256=sha(abi_after),javapChildExitAfterRecovery=None,
              spotbugsXml=pin(xml),spotbugsClass=ids[0],spotbugsXmlFindings=0,spotbugsXmlErrors=0,
              spotbugsXmlMissing=0,spotbugsChildExitAfterRecovery=None,
              reranAnyChild=False,wholeF03Accepted=False,whole451Accepted=False,
              terminalAtUTC=COMMON["timestamp"]())
    dump(result/"manifest.json",info)
    print(pin(result/"manifest.json"),len(classfiles),sum(a["classes"] for a in products.values()))


if __name__=="__main__":
    main()
