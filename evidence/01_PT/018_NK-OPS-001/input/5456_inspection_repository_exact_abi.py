"""Compare the exact inspection class from its selected JUnit run with its baseline ABI."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess
import tempfile


def digest(data):
    return sha256(data).hexdigest()


def pin(path):
    return dict(path=str(path),sha256=digest(path.read_bytes()))


quality = Path("documents/400_PGPT/470_PMO")
plan = next(quality.glob("601_*"))
begin = json.loads(next(plan.glob("1247_*")).read_bytes())
ctx = begin["values"]
ops = Path("evidence/01_PT/018_NK-OPS-001/evidence")
unit_path = next(ops.glob("PG40842-*/manifest.json"))
unit = json.loads(unit_path.read_bytes())
previous_path = next(ops.glob("PG40836-*/manifest.json"))
previous = json.loads(previous_path.read_bytes())
base,core = previous["priorCore"],ctx["productionCoreMain"]
assert core == unit["currentCore"] == previous["currentCore"]
ns = "dev/codex/schubert/nk/batch/repository/InspectionSummaryRepository"
def current_at(name):
    return next(item for item in unit["sourceInputs"] if item["path"].endswith(name))
changed = Path(current_at("/InspectionSummaryRepository.java")["path"])
target = Path("../pgpt-runs/PG379")/unit["run"]/"matched-classes"/(ns+".class")
tools = Path.cwd().parent/"toolchain"
bin_path = tools/"jdk-25.0.4/bin"
jar = tools/"org.jacoco.cli-0.8.15-nodeps.jar"
annotations = tools/"m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
steps={}
def run(key,*args):
    argv = list(map(str,args))
    cp = subprocess.run(argv,capture_output=True,timeout=35)
    steps[key] = dict(command=argv,exitCode=cp.returncode,stdoutSha256=digest(cp.stdout),stderrSha256=digest(cp.stderr))
    assert cp.returncode==0,key
    return cp.stdout
def owner_refs(data):
    return {
        kind: set(re.findall(rb"^\s*#\d+ = "+kind.encode()+rb"\s+.*? // (.+)$",data,re.M))
        for kind in ("Class","Methodref","InterfaceMethodref","Fieldref","String")
    }


with tempfile.TemporaryDirectory(prefix="pg40844-",dir="/dev/shm") as tmp:
    scratch=Path(tmp)
    old_paths=[]
    for item in unit["sourceInputs"]:
        path=item["path"]
        if "/src/main/java/" not in path:
            continue
        before = run("readBaseline "+Path(path).name,"git","show",f"{base}:{path}")
        after = run("readCandidate "+Path(path).name,"git","show",f"{core}:{path}")
        assert digest(after)==item["sha256"]
        if Path(path)!=changed:
            assert before==after
        target_source=scratch/Path(path).name
        target_source.write_bytes(before)
        old_paths.append(target_source)
    assert len(old_paths)==8
    cp_dir=scratch/"baseline-classes"
    run("compileBaseline",bin_path/"javac","--release",25,"-g","-Xlint:all","-Werror","-proc:none",
        "-cp",annotations,"-d",cp_dir,*old_paths)
    old_class=cp_dir/(ns+".class")
    same_crc=unit["selectedRaw"]["measurements"][ns]["crc64"]
    assert same_crc.encode() in run("classIdentity",bin_path/"java","-jar",jar,"classinfo",target).lower()
    old_descriptor=run("priorDescriptor",bin_path/"javap","-public","-s","-constants",old_class)
    new_descriptor=run("candidateDescriptor",bin_path/"javap","-public","-s","-constants",target)
    assert old_descriptor==new_descriptor
    before=owner_refs(run("priorConstantPool",bin_path/"javap","-v",old_class))
    after=owner_refs(run("candidateConstantPool",bin_path/"javap","-v",target))
    additions={cat:sorted((x.decode() for x in after[cat]-before[cat])) for cat in before}
    assert all(before[cat]<=after[cat] for cat in before)
    assert additions=={
        "Class":["dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraph"],
        "InterfaceMethodref":["dev/codex/schubert/nk/api/bootstrap/JdbcFailureGraph.preserveFatal:(Ljava/lang/Throwable;)V"],
        "Methodref":[],"Fieldref":[],"String":[],
    },additions
    prior_physical_sha=digest(old_class.read_bytes())
run_path=ops/ctx["run"]
run_path.mkdir()
abi_out=run_path/"inspection-public-api.txt"
abi_out.write_bytes(new_descriptor)
report=dict(actualExit=0,core=core,previousCore=base,unit=pin(unit_path),changedSource=pin(changed),currentClass=pin(target),
            priorClassSha256=prior_physical_sha,crc64=same_crc,identicalPublicDescriptor=True,publicApi=pin(abi_out),
            directConstantPoolAdditions=additions,constantStringDelta=0,classpathModule="schubert-nk-bootstrap",
            steps=steps,unitReplays=0,jarAnalyzerInvocations=0,actualBackendOperations=0,
            formalDelta=0,whole451=False,terminalAtUTC=datetime.now(timezone.utc).isoformat())
(out:=run_path/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(pin(out),additions["InterfaceMethodref"])
