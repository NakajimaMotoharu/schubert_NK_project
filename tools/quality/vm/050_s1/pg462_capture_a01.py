"""One external A01 observation from frozen common Current driver; not whole parent acceptance."""
import datetime,hashlib,json,os,pathlib,signal,subprocess
ROOT=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
witness=json.loads((WORK/'pg462-live-ready-witness.private.json').read_bytes())
assert witness['source']=='00785cf0698aecf1ace1e60b87e8849639e85b97'
assert all(witness[k] for k in ('sameCapturedCurrentPeers','sameApiWeb','sameCaddySocket','publicCaValidated','publicCaMode600','caddyTlsLogin200'))
assert witness['rootWebExternalCaptureMissing'] and not witness['wholeMorningAccepted']
# The failed original observer never produced a TLS witness, so its waiter never started a browser.
assert not (WORK/'pg461-chr-a01-native-v1.log').exists()
assert not (WORK/'pg461-chr-a01-execution.private.json').exists()
pid=1966600
proc=pathlib.Path('/proc')/str(pid)
if proc.exists():
 assert proc.joinpath('cmdline').read_bytes().split(b'\0')[:3]==[b'python3',b'tools/quality/vm/050_s1/pg461_capture_a01_when_ready.py',b'00785cf0698aecf1ace1e60b87e8849639e85b97']
 os.kill(pid,signal.SIGTERM) # Owned unused host waiter only; no application/VM Unit is stopped.
assert not (ROOT/'program/characterization/reports/nk/PG462-native-a01-v1').exists()
cp=str(WORK/'pg460-chr-host/test-classes')+':'+str(WORK/'pg460-chr-host/classes')+':'+(WORK/'pg459-chr-classpath.private').read_text().strip()
command=['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java','-cp',cp,'dev.codex.schubert.characterization.NativeNkA01Capture',str(ROOT/'program/characterization/reports/nk'),str(ROOT/'program/characterization/reports/nk/PG462-native-a01-v1'),str(ROOT/'program/characterization/baseline/current/artifacts/CHR-A01.json')]
os.umask(0o077);log=WORK/'pg462-chr-a01-native-v1.log';started=datetime.datetime.now(datetime.timezone.utc).isoformat()
env=os.environ.copy();env['PLAYWRIGHT_BROWSERS_PATH']='/home/mini/codex/project1/work/characterization-tools/playwright-browsers';env['PLAYWRIGHT_HOST_PLATFORM_OVERRIDE']='ubuntu24.04-x64';env['LD_LIBRARY_PATH']='/home/mini/codex/project1/work/characterization-tools/root/usr/lib/x86_64-linux-gnu'
with log.open('xb') as stream:r=subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=stream)
m={'case':'CHR-A01','productionSource':witness['source'],'startedAt':started,'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':r.returncode,'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'sharedCurrentDriver':True,'fullGate':False,'otherCasesNotRun':True,'wholeParentAccepted':False,'oldWaiterStoppedWithoutBrowser':True}
with (WORK/'pg462-chr-a01-execution.private.json').open('x') as stream:json.dump(m,stream);stream.write('\n')
print(json.dumps(m));raise SystemExit(r.returncode)
