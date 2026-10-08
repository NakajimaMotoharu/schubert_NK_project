"""Single shared-Current A01 capture on the new PG573 parent; no restart or oracle rewrite."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import time

T=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
W=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=pathlib.Path('/home/mini/codex/project1/work/pgpt-vm/private')
SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'
OUT=T/'program/characterization/reports/nk/PG575-native-a01-v1'
WATCH=W/'pg574-watch-private-v1.jsonl'
GUARD=r'''
import hashlib,json,pathlib,subprocess,time
assert pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg573-fresh-parent-v2')
issued=json.loads((root/'external-start-issued.private.json').read_bytes())
fields='InvocationID,MainPID,ControlPID,Job,ExecMainStartTimestampMonotonic,ExecMainCode,ExecMainStatus,Result'
units={}
for unit in ['schubert-nk-morning-controller.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service']:
 raw=subprocess.check_output(['systemctl','show',unit,'--property='+fields],text=True);units[unit]=dict(l.split('=',1)for l in raw.splitlines())
m=units['schubert-nk-morning-controller.service'];assert m['InvocationID']==issued['InvocationID']and m['ExecMainStartTimestampMonotonic']==issued['ExecMainStartTimestampMonotonic']
assert time.monotonic_ns()//1000<int(m['ExecMainStartTimestampMonotonic'])+1800000000
for u,v in units.items():
 if u!='schubert-nk-morning-controller.service':assert int(v['MainPID'])>0 and v['InvocationID']
release=pathlib.Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes()
assert str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG548'and hashlib.sha256(manifest).hexdigest()=='a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b'
print(json.dumps(units))
'''


def main():
    os.umask(0o077)
    assert not OUT.exists() and not (W/'pg575-chr-a01-native-v1.private.log').exists()
    assert (W/'pg573-start-v2.exit').read_bytes()==b'0\n'
    deadline=time.monotonic()+1860
    while time.monotonic()<deadline:
        records=[]
        if WATCH.exists():
            for line in WATCH.read_bytes().splitlines():
                try:records.append(json.loads(line))
                except json.JSONDecodeError:continue
        if any(v.get('caddyTlsLogin200')and v.get('sameApiWeb')and v.get('sameCaddySocket')and v.get('publicCaValidated')for v in records):break
        if (W/'pg574-observer-v1.exit').exists():raise ValueError('parent ended before TLS capture; A01 not run')
        time.sleep(.2)
    else:raise ValueError('A01 wait deadline; not run')
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    before=json.loads(subprocess.check_output(ssh,input=GUARD.encode(),timeout=20))
    harness=W/'pg460-chr-host';digest=hashlib.sha256()
    for p in sorted(harness.rglob('*.class')):digest.update(str(p.relative_to(harness)).encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest())
    assert digest.hexdigest()=='122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d'
    cp=str(harness/'test-classes')+':'+str(harness/'classes')+':'+(W/'pg459-chr-classpath.private').read_text().strip()
    command=['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java','-cp',cp,'dev.codex.schubert.characterization.NativeNkA01Capture',str(T/'program/characterization/reports/nk'),str(OUT),str(T/'program/characterization/baseline/current/artifacts/CHR-A01.json')]
    env=os.environ.copy();env.update(PLAYWRIGHT_BROWSERS_PATH='/home/mini/codex/project1/work/characterization-tools/playwright-browsers',PLAYWRIGHT_HOST_PLATFORM_OVERRIDE='ubuntu24.04-x64',LD_LIBRARY_PATH='/home/mini/codex/project1/work/characterization-tools/root/usr/lib/x86_64-linux-gnu')
    baseline=T/'program/characterization/baseline/current/artifacts/CHR-A01.json';baseline_sha=hashlib.sha256(baseline.read_bytes()).hexdigest()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with(W/'pg575-chr-a01-native-v1.private.log').open('xb')as f:
        result=subprocess.run(command,cwd=T,env=env,stdout=f,stderr=f,timeout=90);f.flush();os.fsync(f.fileno())
    with(W/'pg575-chr-a01-native-v1.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    after=json.loads(subprocess.check_output(ssh,input=GUARD.encode(),timeout=20))
    assert all(before[u]['MainPID']==after[u]['MainPID']and before[u]['InvocationID']==after[u]['InvocationID']and before[u]['ExecMainStartTimestampMonotonic']==after[u]['ExecMainStartTimestampMonotonic']for u in before)
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()==baseline_sha
    record={'run':'PG575-native-a01-v1','productionSource':SOURCE,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actualExit':result.returncode,'harnessClassesSha256':digest.hexdigest(),'baselineSha256':baseline_sha,'sameCapturedParentApiWebCaddyBeforeAfter':True,'sharedCurrentDriver':True,'approvedDIF001TitleOnly':True,'otherCasesNotRun':True,'fullGate':False,'formalAccepted':False,'rawCookieTokenExported':False}
    with(W/'pg575-chr-a01-native-v1.safe.json').open('x')as f:json.dump(record,f,sort_keys=True)
    print(json.dumps(record));raise SystemExit(result.returncode)


if __name__=='__main__':main()
