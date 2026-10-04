"""Wait for same-source real TLS witness, then shared Current A01 capture ONCE.
No application start/stop/reset or retry; private failure remains non-pass.
"""
import datetime,hashlib,json,os,pathlib,subprocess,time
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
WATCH=WORK/'pg460-parent-watch-private-v1.jsonl'
deadline=time.monotonic()+1860
while time.monotonic()<deadline:
 records=[]
 if WATCH.exists():
  for line in WATCH.read_text().splitlines():
   try:records.append(json.loads(line))
   except json.JSONDecodeError:continue
 if any(r.get('caddyTlsLogin200') and r.get('sameApiWeb') and r.get('sameCaddySocket') and r.get('publicCaValidated') for r in records):break
 if any(r.get('terminalObserved') for r in records):print('CHR460_A01_NOT_RUN terminalBeforeTLS=true pass=false');raise SystemExit(2)
 time.sleep(.2)
else:print('CHR460_A01_NOT_RUN waitDeadline=true pass=false');raise SystemExit(2)
cp=str(WORK/'pg460-chr-host/test-classes')+':'+str(WORK/'pg460-chr-host/classes')+':'+(WORK/'pg459-chr-classpath.private').read_text().strip()
command=['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java','-cp',cp,'dev.codex.schubert.characterization.NativeNkA01Capture',str(ROOT/'program/characterization/reports/nk'),str(ROOT/'program/characterization/reports/nk/PG460-native-a01-v1'),str(ROOT/'program/characterization/baseline/current/artifacts/CHR-A01.json')]
os.umask(0o077);log=WORK/'pg460-chr-a01-native-v1.log';started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with log.open('xb') as stream:r=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=stream)
m={'case':'CHR-A01','productionSource':'8e97eb9138828010926cd47fd10868d8a2d54f11','startedAt':started,'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'sharedCurrentDriver':True,'fullGate':False,'otherCasesNotRun':True}
with (WORK/'pg460-chr-a01-execution.private.json').open('x') as stream:json.dump(m,stream);stream.write('\n')
print(json.dumps(m));raise SystemExit(r.returncode)
