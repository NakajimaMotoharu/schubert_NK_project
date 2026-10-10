"""New-only corrected public refusal compiler; old failed fixture is immutable."""
import inspect
import json
import os
import shutil
import subprocess
from pathlib import Path
import pg1282_physical_pin_compile as previous

TARGET=previous.W/'pg1285-physical-pin-tools-v1'


def main():
    code=inspect.getsource(previous.main)
    code=code.replace("str(TARGET/source.name)]","str(TARGET/source.name),str(TARGET/'Pg1285PublicRefusalTest.java')]")
    marker="cp=':'.join"
    if code.count(marker)!=1:raise ValueError('fixed compiler boundary required')
    code=code.replace(marker,"shutil.copyfile(Path(__file__).with_name('Pg1285PublicRefusalTest.java'),TARGET/'Pg1285PublicRefusalTest.java')\n    "+marker)
    env=dict(previous.__dict__);env['TARGET']=TARGET
    exec(compile(code,'<corrected public boundary component compile>','exec'),env)
    result=env['main']()
    if result:return result
    cp=':'.join(str(p)for p in [TARGET,TARGET/'protocol.jar',TARGET/'storage.jar',TARGET/'bootstrap.jar'])
    log=previous.W/'pg1285-public-refusal.private.log'
    with log.open('xb')as f:
        os.fchmod(f.fileno(),0o600)
        r=subprocess.run(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java','-cp',cp,'dev.codex.schubert.nk.bootstrap.Pg1285PublicRefusalTest'],stdout=f,stderr=f)
        f.flush();os.fsync(f.fileno())
    safe={'actualExit':r.returncode,'sevenFixedVectors':log.read_bytes()==b'PUBLIC_REFUSAL_7_VECTORS_PASS\n','privateLogSha256':previous.sha(log),'formalAccepted':False}
    with(previous.W/'pg1285-public-refusal.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps(safe));return 0 if r.returncode==0 and safe['sevenFixedVectors']else 1


if __name__=='__main__':raise SystemExit(main())
