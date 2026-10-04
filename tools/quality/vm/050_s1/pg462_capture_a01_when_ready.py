"""New-source PG462 shared Current A01 capture once after genuine TLS witness.

No app start/stop/reset/retry. Old-source PG462-native-a01-v1 stays immutable.
"""
import datetime,hashlib,json,os,pathlib,subprocess,time,re,sys
assert len(sys.argv)==2 and sys.argv[1]=='ca33239da3019dad50b6ebad22318130283d6756';SOURCE=sys.argv[1]
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
WATCH=WORK/'pg462-parent-watch-private-v1.jsonl'
OUT=ROOT/'program/characterization/reports/nk/PG462-native-a01-patched-v1'
assert not OUT.exists()
deadline=time.monotonic()+1860
while time.monotonic()<deadline:
 records=[]
 if WATCH.exists():
  for line in WATCH.read_text().splitlines():
   try:records.append(json.loads(line))
   except json.JSONDecodeError:continue
 if any(r.get('caddyTlsLogin200') and r.get('sameApiWeb') and r.get('sameCaddySocket') and r.get('publicCaValidated') for r in records):break
 if any(r.get('terminalObserved') for r in records):print('CHR462_A01_NOT_RUN terminalBeforeTLS=true pass=false');raise SystemExit(2)
 time.sleep(.2)
else:print('CHR462_A01_NOT_RUN waitDeadline=true pass=false');raise SystemExit(2)
# A01 helper bytes are frozen and recorded independently; the Current oracle is unchanged.
harness=WORK/'pg460-chr-host';cp=str(harness/'test-classes')+':'+str(harness/'classes')+':'+(WORK/'pg459-chr-classpath.private').read_text().strip()
command=['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java','-cp',cp,'dev.codex.schubert.characterization.NativeNkA01Capture',str(ROOT/'program/characterization/reports/nk'),str(OUT),str(ROOT/'program/characterization/baseline/current/artifacts/CHR-A01.json')]
os.umask(0o077);log=WORK/'pg462-chr-a01-patched-native-v1.log';started=datetime.datetime.now(datetime.timezone.utc).isoformat()
env=os.environ.copy();env['PLAYWRIGHT_BROWSERS_PATH']='/home/mini/codex/project1/work/characterization-tools/playwright-browsers';env['PLAYWRIGHT_HOST_PLATFORM_OVERRIDE']='ubuntu24.04-x64';env['LD_LIBRARY_PATH']='/home/mini/codex/project1/work/characterization-tools/root/usr/lib/x86_64-linux-gnu'
with log.open('xb') as stream:r=subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=stream)
h=hashlib.sha256()
for p in sorted(harness.rglob('*.class')):h.update(str(p.relative_to(harness)).encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest())
m={'case':'CHR-A01','productionSource':SOURCE,'startedAt':started,'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'harnessClassesSha256':h.hexdigest(),'sharedCurrentDriver':True,'fullGate':False,'otherCasesNotRun':True,'wholeParentAccepted':False}
with (WORK/'pg462-chr-a01-patched-execution.private.json').open('x') as stream:json.dump(m,stream);stream.write('\n')
print(json.dumps(m));raise SystemExit(r.returncode)
