"""Actual Java25/Werror independent10-vector dominance preflight; no VM/native admission."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg1446_current_cold_stage import W
from pg2176_newsource_normal_observer import SOURCE


def main():
    os.umask(0o077);out=W/'pg2260-native-point-dominance-host-v1';out.mkdir(mode=0o700);classes=out/'classes';classes.mkdir()
    root=Path(__file__).resolve().parent/'vm/050_s1';java=Path('/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin')
    cp='/home/mini/codex/project1/work/toolchain/m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    paths=[root/n for n in ['NativePointDominance.java','NativePointDominanceTest.java']]
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    commands=[[str(java/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(p)for p in paths]],[str(java/'java'),'-cp',str(classes)+':'+cp,'NativePointDominanceTest']]
    results=[]
    for n,command in enumerate(commands):
        r=subprocess.run(command,capture_output=True,timeout=30);(out/(str(n)+'.log')).write_bytes(r.stdout+r.stderr);results.append(r.returncode)
        if r.returncode:break
    actual=0 if results==[0,0]and r.stdout==b'literalMonotonic10Vectors=true\n'and not r.stderr else 1
    value={'actualExit':actual,'source':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sourceHashes':hashes,'commands':commands,'exits':results,'independentVectors':10,'javaVersion':'25.0.4','jacocoVersion':'0.8.15','startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vmActions0':True,'productionPtAdded':0,'actualNativeQualified':False,'formalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value));return actual


if __name__=='__main__':raise SystemExit(main())
