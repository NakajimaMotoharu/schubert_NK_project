"""Build the authorized four-module subset and bind the schema PT to the physical output."""

import io
import json
from pathlib import Path
import runpy
import shutil
import tarfile
from tempfile import TemporaryDirectory
from xml.etree import ElementTree
from zipfile import ZipFile


B = runpy.run_path(str(Path(__file__).with_name("5364_f02_utc42_four_current_jars.py")))
OPS, PLAN, COMMON, PACKAGE, MODULES, UPPER = (
    B[n] for n in ("OPS","PLAN","COMMON","PACKAGE","MODULES","UPPER"))
SOURCE = "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission.java"
TYPE = "dev/codex/schubert/nk/api/bootstrap/SchemaHistoryAdmission.class"


def main():
    read=UPPER["read"]
    pin,sha,git,dump=(COMMON[k] for k in ("pin","sha","git","dump"))
    start=read(next(PLAN.glob("893_*")))
    w=start["values"]
    green_path=next(OPS.glob("PG40494-*/manifest.json"))
    green=read(green_path)
    core=green["productionCore"]
    assert green["actualExit"]==0 and green["acceptedPtCount"]==13
    previous=read(w["oracleReferences"][3]["path"])
    assert previous["sourceCore"]==w["productionCoreMain"]
    assert git("diff","--name-only",previous["sourceCore"],core,"--","src","pom.xml",
               ":(exclude)src/**/src/test/**").decode().splitlines()==[SOURCE]
    old_compiler=read(next(OPS.glob("PG39862-*/manifest.json")))
    java=Path(read(next(OPS.glob("PG40128-*/begin.json")))["jdk"]["path"])
    maven=old_compiler["maven"]["command"]
    assert pin(java)["sha256"]==old_compiler["tools"]["javaSha256"]
    assert pin(Path(maven[0]))["sha256"]==old_compiler["tools"]["mavenLauncherSha256"]
    plugin_lineage=previous["oldJarManifest"]
    assert pin(Path(plugin_lineage["path"]))==plugin_lineage
    maven_plugin=read(plugin_lineage["path"])["mavenPlugin"]
    assert pin(Path(maven_plugin["path"]))==maven_plugin
    env={"JAVA_HOME":str(java.parents[1]),"PATH":str(java.parent)+":/usr/bin:/bin","LANG":"C.UTF-8"}
    tree=["pom.xml","program/characterization/pom.xml","src/schubert-nk-api/pom.xml","src/schubert-nk-web/pom.xml"]
    for module in MODULES:
        tree.extend((f"src/schubert-nk-{module}/pom.xml",f"src/schubert-nk-{module}/src/main"))
    scan=git("ls-tree","-r","--name-only",core,*tree).decode().splitlines()
    assert sum(name.endswith(".java") for name in scan)==482 and not any("/src/test/" in n for n in scan)
    assert not any(Path(name).stem in ("TemporaryInfrastructureException","FingerprintKeyRing",
                                      "ResponseSnapshotCodec","WebStartupException") for name in scan)
    run="PG40496-schema-history-current-four-packaged-v1"
    out=(OPS/run).resolve()
    out.mkdir()
    output_jars=Path.cwd().parent/"pgpt-runs"/"PG379"/run.lower()
    stages,delta,artifacts={},{},{}
    equivalent=False
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-schema-four-artifacts-") as loc:
        root=Path(loc)
        with tarfile.open(fileobj=io.BytesIO(git("archive",core,*tree))) as t:
            t.extractall(root,filter="data")
        stages["compile"]=UPPER["run"](out,"compile",maven,root,env)
        if stages["compile"]["actualExit"]==0:
            stages["package"]=UPPER["run"](out,"package",[
                *maven[:-2],"org.apache.maven.plugins:maven-jar-plugin:3.4.1:jar"],root,env)
        if "package" in stages and stages["package"]["actualExit"]==0:
            output_jars.mkdir(mode=0o700)
            diff_target=set()
            for module in MODULES:
                name=f"schubert-nk-{module}"
                mpath=root/"src"/name
                prior=previous["packagedJars"][module]["artifact"]
                assert pin(Path(prior["path"]))==prior
                now=PACKAGE["inventory"](mpath/"target/classes")
                with ZipFile(prior["path"]) as archive:
                    then={entry:sha(archive.read(entry)) for entry in archive.namelist() if entry.endswith(".class")}
                    assert set(then)==set(now)
                    delta[module]=sorted(entry for entry in now if now[entry]!=then[entry])
                    if module=="bootstrap":
                        old=root/"old"/TYPE
                        old.parent.mkdir(parents=True)
                        old.write_bytes(archive.read(TYPE))
                diff_target.update(delta[module])
                copy=output_jars/(name+"-0.1.0-SNAPSHOT.jar")
                shutil.copyfile(mpath/"target"/copy.name,copy)
                copy.chmod(0o600)
                artifacts[module]=PACKAGE["verify_jar"](copy,name,now,(mpath/"pom.xml").read_bytes())
            assert diff_target=={TYPE} and sum(a["classes"] for a in artifacts.values())==1102
            file=root/"src/schubert-nk-bootstrap/target/classes"/TYPE
            equivalent=sha(file.read_bytes())==green["physicalClassHashes"][TYPE]
            approved=read(next(OPS.glob("PG40474-*/manifest.json")))
            tool=approved["terminal"]["command"]
            cfg=Path(tool[tool.index("-auxclasspathFromFile")+1])
            models=cfg.read_text().splitlines()
            aux=out/"spotbugs-aux.txt"
            aux.write_text("\n".join([artifacts[n]["artifact"]["path"] for n in ("storage","bootstrap")]+models)+"\n")
            sb=out/"spotbugs.xml"
            stages["spotbugs"]=UPPER["run"](out,"spotbugs",[
                *tool[:tool.index("-auxclasspathFromFile")+1],aux,"-output",sb,file],root,env)
            for label,p in (("abi-before",old),("abi-after",file)):
                stages[label]=UPPER["run"](out,label,[java.with_name("javap"),"-public","-s",p],root,env)
    abi=(stages.get("abi-before",{}).get("stdout",{}).get("sha256")
         ==stages.get("abi-after",{}).get("stdout",{}).get("sha256"))
    if artifacts and sb.is_file():
        result=ElementTree.parse(sb).getroot()
        ast=[row.get("class") for row in result.findall(".//ClassStats")]
        bugs=len(result.findall("BugInstance"))
        missing=len(result.findall(".//MissingClass"))
        errors=len(result.findall(".//Error"))
    else:
        ast,bugs,missing,errors=[],None,None,None
    okay=len(stages)==5 and all(x["actualExit"]==0 for x in stages.values()) and abi and +        ast==["dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission"] and [bugs,missing,errors]==[0,0,0]
    d=dict(actualExit=0 if okay else 1, productionCore=core, source=core, canonicalDesign=green["canonicalDesign"],
           stages=stages,baseFour=pin(Path(w["oracleReferences"][3]["path"])),packagedBuild=artifacts,
           mavenPlugin=maven_plugin,
           changedPhysical=delta,freshPhysicalCount=1102 if artifacts else 0,spotbugsClassStats=ast,
           spotbugsFindings=bugs,spotbugsMissing=missing,spotbugsErrors=errors,publicAbiEqual=abi,
           samePhysicalAsFocused13=equivalent,focusedRun=pin(green_path),sourcedMainCount=482,
           newProductTestExecutionsHere=0,backendActions=0,whole451Accepted=False,
           terminalAtUTC=COMMON["timestamp"]())
    dump(out/"manifest.json",d)
    print(pin(out/"manifest.json"),{n:r["actualExit"] for n,r in stages.items()},equivalent)
    return d["actualExit"]


if __name__=="__main__":
    raise SystemExit(main())
