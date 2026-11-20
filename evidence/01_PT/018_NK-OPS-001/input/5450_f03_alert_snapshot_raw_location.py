"""Locate the measured AlertLifecycle snapshot difference without replaying tests."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import re
import subprocess
import tempfile


def digest(value):
    return sha256(value).hexdigest()


ops = Path("evidence/01_PT/018_NK-OPS-001/evidence")
plan = next(Path("documents/400_PGPT/470_PMO").glob("601_*"))
start = json.loads(next(plan.glob("1229_*")).read_bytes())
ctx = start["values"]
core = ctx["productionCoreMain"]
prior_path = next(ops.glob("PG40828-*/manifest.json"))
prior = json.loads(prior_path.read_bytes())
assert prior["core"] == core
toolchain = Path.cwd().parent/"toolchain"
jdk = toolchain/"jdk-25.0.4/bin"
jacoco = toolchain/"org.jacoco.cli-0.8.15-nodeps.jar"
jspecify = toolchain/"m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar"
ns = "dev/codex/schubert/nk/batch/monitoring"
paths = [Path("src/schubert-nk-batch/src/main/java")/ns/n for n in (
    "AlertLifecycle.java","ObservationContext.java","package-info.java")]
pins = {item["path"]:item["sha256"] for item in prior["sources"]}
for p in paths:
    assert pins[str(p)] == digest(p.read_bytes())
    assert p.read_bytes() == subprocess.check_output(["git","show",f"{core}:{p}"])
steps = {}
env = {"LANG":"C.UTF-8","PATH":os.defpath,"TZ":"Asia/Tokyo"}


def command(name,*args):
    argv = list(map(str,args))
    run = subprocess.run(argv,capture_output=True,timeout=30,env=env)
    steps[name] = dict(command=argv,exit=run.returncode,stdoutSha256=digest(run.stdout),stderrSha256=digest(run.stderr))
    if run.returncode:
        raise RuntimeError((name,run.returncode))
    return run.stdout.decode()


with tempfile.TemporaryDirectory(prefix="pg40830-",dir="/dev/shm") as tmp:
    classes = Path(tmp)
    command("compile",jdk/"javac","--release",25,"-g","-Xlint:all","-Werror",
            "-proc:none","-cp",jspecify,"-d",classes,*paths)
    target = classes/ns/"AlertLifecycle.class"
    class_sha = digest(target.read_bytes())
    meta = command("classinfo",jdk/"java","-jar",jacoco,"classinfo",target)
    measured = prior["selectedRaw"]["primary"][ns+"/AlertLifecycle"]
    assert measured["crc64"] in meta.lower()
    text = command("javap",jdk/"javap","-c","-l","-p",target)
    start_offset = text.index("  public java.util.Optional<dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event> snapshot();")
    end_offset = text.index("  static {};",start_offset)
    body = text[start_offset:end_offset].rstrip()
    instructions = [(int(off),op) for off,op in re.findall(r"^\s*(\d+):\s+(\w+)",body,re.M)]
    handlers = [(int(begin),int(end),int(entry)) for begin,end,entry in
                re.findall(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+any\s*$",body,re.M)]
    assert len(handlers)==2 and handlers[0][2]==handlers[1][2]
    handler_tail = [op for off,op in instructions if off>=handlers[0][2]]
    assert handler_tail==["astore_2","aload_1","monitorexit","aload_2","athrow"]
    assert not any(op.startswith("invoke") for off,op in instructions)
    assert measured["counters"]["INSTRUCTION"]["missed"] == len(handler_tail)
    source = dict(path=str(paths[0]),sha256=pins[str(paths[0])])
run = ops/ctx["run"]
run.mkdir()
excerpt = run/"snapshot-javap.txt"
excerpt.write_text(body+"\n")
record = dict(actualExit=0,core=core,source=source,startedBy=start["eventId"],steps=steps,
    classSha256=class_sha,measuredCrc64=measured["crc64"],boundedInputs=[source,*(dict(path=str(p),sha256=pins[str(p)]) for p in paths[1:])],
    scope="One AlertLifecycle.class, same CRC as PG40828",
    snapshotHandler=handler_tail,handlerTable=handlers,rawMissingLine=1,rawMissingInstructions=len(handler_tail),
    correspondingExceptionHandlerOnly=True,handlerInvoked=False,reachabilityJudgment=None,exclusionApplied=False,rawGapClosed=False,
    unitReplay=0,heldFilesRead=0,actualNativeOperations=0,formalDelta=0,whole451=False,
    excerpt=dict(path=str(excerpt),sha256=digest(excerpt.read_bytes())),terminalAtUTC=datetime.now(timezone.utc).isoformat())
(out:=run/"manifest.json").write_text(json.dumps(record,indent=2)+"\n")
print(digest(out.read_bytes()), record["measuredCrc64"], handler_tail)
