"""Apply the pinned Root null gate and typed analyzers to the current media subset."""

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET


h=runpy.run_path(str(Path(__file__).with_name("5642_media_single_exec_current_five_types.py")))
g=runpy.run_path(str(Path(__file__).with_name("5621_range_current_nullaway_pmd.py")))
OPS,BIN,check,pin,read=(h[key] for key in ("OPS","BIN","check","pin","read"))
tag,element=(g[key] for key in ("tag","element"))
RUN="PG41264-media-current-five-types-typed-static-v1"


def main():
    before=OPS/h["FIXED_RUN"]/"manifest.json"
    unit=read(before)
    cov_path,=OPS.glob("PG41262-*/manifest.json")
    cov=read(cov_path)
    assert unit["productionCore"]==cov["productionCore"] and cov["status"]=="FULL"
    expected={Path(row["path"]).name:row["sha256"] for row in unit["admittedPhysical"]}
    for row in [*unit["inputMain"],*unit["inputTests"],*unit["sdk"],*unit["admittedPhysical"]]:
        assert pin(Path(row["path"]))==row
    root_pom=Path("pom.xml")
    root=ET.parse(root_pom).getroot()
    compiler=next(node for node in root.findall(f".//{tag('plugin')}")
                  if node.findtext(tag("artifactId"))=="maven-compiler-plugin")
    existing,=OPS.glob("PG41208-*/manifest.json")
    precedent=read(existing)
    canonical_compiler=sha256(ET.tostring(compiler)).hexdigest()
    assert canonical_compiler==precedent["exactRootCompilerSha256"]
    sdk=[Path(row["path"]) for row in unit["sdk"]]
    protocol,=[p for p in sdk if p.name=="current-protocol176.jar"]
    src=[Path(row["path"]) for row in unit["inputMain"]]
    pkg=src[0].with_name("package-info.java")
    subject,=[p for p in src if p.name=="MediaRangeService.java"]
    test,=[Path(row["path"]) for row in unit["inputTests"] if row["path"].endswith("/ExceptionValueContractTest.java")]
    work=OPS/RUN
    work.mkdir()
    results={}
    with TemporaryDirectory(dir="/dev/shm",prefix="pgpt-media-typed-static-") as tmp:
        tmp=Path(tmp)
        folder=tmp/"src/main/java"/h["DIR"]
        folder.mkdir(parents=True)
        for path in [*src,pkg]:
            (folder/path.name).write_bytes(path.read_bytes())
        pom=ET.Element(tag("project"))
        for key,val in (("modelVersion","4.0.0"),("groupId","dev.codex.schubert.quality"),
                        ("artifactId","pgpt-media-five-types-current"),("version","1")):
            element(pom,key,val)
        p=element(pom,"properties")
        for name in ("maven.compiler.release","project.build.sourceEncoding","error-prone.version","nullaway.version"):
            element(p,name,root.find(tag("properties")).findtext(tag(name)))
        dependencies=element(pom,"dependencies")
        for records in (
            (("groupId","org.jspecify"),("artifactId","jspecify"),("version","1.0.1")),
            (("groupId","dev.codex.schubert.quality"),("artifactId","current-protocol176"),
             ("version","1"),("scope","system"),("systemPath",str(protocol))),
        ):
            dep=element(dependencies,"dependency")
            for key,value in records:
                element(dep,key,value)
        element(element(pom,"build"),"plugins").append(deepcopy(compiler))
        generated=tmp/"pom.xml"
        ET.ElementTree(pom).write(generated,encoding="utf-8",xml_declaration=True)
        subset_hash=pin(generated)["sha256"]
        tc=BIN.parent.parent.resolve()
        maven=tc/"m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn"
        repo=tc/"m2/repository"
        cmd=["env",f"JAVA_HOME={BIN.parent}",f"PATH={BIN}:/usr/bin:/bin",maven,"-o","-f",generated,
             "--no-transfer-progress",f"-Dmaven.repo.local={repo}","-Dmaven.test.skip=true","compile"]
        results["nullaway"],built=check(cmd)
        # The manifest records the untouched diagnostic byte hash.
        (work/"nullaway.stdout").write_bytes(built.stdout)
        assert built.returncode==0,(built.stdout[-1400:],built.stderr[-1400:])
        main_dir=tmp/"target/classes"
        main_physical=sorted(p for p in main_dir.rglob("*.class") if p.name!="package-info.class")
        assert {p.name:pin(p)["sha256"] for p in main_physical}==expected
        test_dir=tmp/"test"
        test_dir.mkdir()
        cp=os.pathsep.join(map(str,[main_dir,*sdk]))
        results["testCompile"],compiled=check([BIN/"javac","--release","25","-g","-Xlint:all",
            "-Werror","-proc:none","-cp",cp,"-d",test_dir,test])
        assert compiled.returncode==0,compiled.stderr
        [test_physical]=test_dir.rglob("*.class")
        sb_ref,=OPS.glob("PG41162-*/manifest.json")
        sb=read(sb_ref)["stagedStatic"]["spotbugs"]["command"][:13]
        sb[10]=cp
        spot_path=work/"spotbugs.xml"
        sb[12]=spot_path
        results["spotbugs"],spot_result=check([*sb,*main_physical,test_physical])
        assert spot_result.returncode in (0,1),spot_result.stderr
        spot=ET.parse(spot_path).getroot()
        bug_sites=[dict(rule=e.get("type"),owner=e.find("Class").get("classname")) for e in spot.findall("BugInstance")]
        errors=len(spot.findall(".//Error"))
        missing=len(spot.findall(".//MissingClass"))
        listing=tmp/"static-inputs.txt"
        listing.write_text(str(subject.resolve())+"\n"+str(test.resolve())+"\n")
        pmd=precedent["stages"]["pmd"]["command"][:6]
        pmd_path=work/"pmd.xml"
        results["pmd"],scanned=check([*pmd,listing,"--rulesets","tools/quality/static/pmd.xml",
            "--use-version","java-25","--aux-classpath",f"{BIN.parent}/lib/jrt-fs.jar:{cp}",
            "--no-cache","--format","xml","--report-file",pmd_path])
        assert scanned.returncode in (0,4),scanned.stderr
        reports=ET.parse(pmd_path).getroot()
        sites=[dict(owner=Path(file.get("name")).name,rule=entry.get("rule"),line=int(entry.get("beginline")))
               for file in reports if file.tag.split("}")[-1]=="file"
               for entry in file if entry.tag.split("}")[-1]=="violation"]
        pmd_shape=[node.tag.split("}")[-1] for node in reports
                   if node.tag.split("}")[-1] in ("error","configerror","suppressedviolation")]
    result=dict(actualExit=0 if not (bug_sites or errors or missing or pmd_shape or sites) else 1,
                terminalAtUTC=datetime.now(timezone.utc).isoformat(),source=unit["productionCore"],
                unit=pin(before),rawCoverage=pin(cov_path),rootCompilerSha256=canonical_compiler,
                localPomSha256=subset_hash,junitInvocations=0,whole451=False,formalDelta=0,
                matchingMainToRawUnit=13,analyzedTestPhysical=1,spotbugsFindings=bug_sites,
                spotbugsMissing=missing,spotbugsErrors=errors,pmdSites=sites,pmdErrorsOrSuppressions=pmd_shape,
                stages=results,outputs=list(map(pin,sorted(work.iterdir()))))
    p=work/"manifest.json"
    with p.open("x") as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    print(pin(p),bug_sites,errors,missing,sites,pmd_shape)
    return result["actualExit"]


if __name__=="__main__":
    raise SystemExit(main())
