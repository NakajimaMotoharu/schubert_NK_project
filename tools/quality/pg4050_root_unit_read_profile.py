"""BUG1332 current-code read timing only. No Root impersonation, service action or DB access."""
import hashlib
import json
import os
import subprocess
from pathlib import Path
from pg1446_current_cold_stage import W, P, SSH
from pg1674_critical_management_gate import management_gate
from pg4002_literal_invariant_publication_sources import SOURCE, BOM

ROOT = Path(__file__).resolve().parents[2]


def payload():
    java = (ROOT / 'tools/quality/RootUnitReadProfile.java').read_text()
    return 'JAVA=' + repr(java) + '\n' + 'SOURCE=' + repr(SOURCE) + '\nBOM=' + repr(BOM) + '\n' + r'''
from pathlib import Path
import os,json,hashlib,subprocess,re,datetime
assert os.geteuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='79a3260a-e16d-42bf-942a-b914ed144c28'
release=Path('/opt/schubert-nk/current');manifest=(release/'RELEASE-MANIFEST.json').read_bytes();assert hashlib.sha256(manifest).hexdigest()==BOM and json.loads(manifest)['source']['commit']==SOURCE
out=Path('/var/lib/pgpt-s1-preservation/pg4050-unit-read-profile-v1');assert not os.path.lexists(out);os.umask(0o077);out.mkdir(mode=0o700);(out/'classes').mkdir();source=out/'RootUnitReadProfile.java';source.write_text(JAVA)
def actor():
 r=subprocess.run(['systemctl','show','schubert-nk-api.service','--property=MainPID,InvocationID,ControlGroup'],capture_output=True,text=True,timeout=10);assert r.returncode==0
 return dict(l.split('=',1)for l in r.stdout.splitlines())
before=actor();assert int(before['MainPID'])>1 and before['InvocationID']=='c9444dbf2e6a43dca0d52ab220d59b1d'
cp=str(release/'operations/batch.jar')+':'+str(release/'operations/lib/*')+':'+str(release/'api/lib/*')
env={k:v for k,v in os.environ.items()if k not in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH']}
args=['/opt/jdk-25.0.4/bin/javac','-Xlint:all','-Werror','-sourcepath','','-cp',cp,'-d',str(out/'classes'),str(source)]
compiled=subprocess.run(args,env=env,capture_output=True,timeout=30);(out/'compile.private.log').write_bytes(compiled.stdout+compiled.stderr);assert compiled.returncode==0
start=datetime.datetime.now(datetime.timezone.utc).isoformat();run=['/opt/jdk-25.0.4/bin/java','--enable-native-access=ALL-UNNAMED','-cp',str(out/'classes')+':'+cp,'dev.codex.schubert.nk.batch.platform.RootUnitReadProfile']
r=subprocess.run(run,env=env,capture_output=True,text=True,timeout=45);(out/'profile.private.log').write_text(r.stdout+r.stderr);assert r.returncode==0
lines=r.stdout.splitlines();assert lines and all(re.fullmatch(r'READONLY_PROFILE1 phase=[A-Za-z-]+ count=[0-9]+ nanos=[0-9]+',l)for l in lines)
assert before==actor() and (release/'RELEASE-MANIFEST.json').read_bytes()==manifest
value={'actualExit':0,'source':SOURCE,'BOM':BOM,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compileCommand':args,'profileCommand':run,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'profile':lines,'sameOrdinaryApiGenerationBeforeAfter':True,'rootStartStopDbActions':0,'newGuestEvidenceOnly':True,'acceptanceOrCoverageClaim':False}
(out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value))
'''


def main():
    os.umask(0o077); out = W / 'pg4050-unit-read-profile-v1'; out.mkdir()
    raw = payload(); compile(raw, '<fixed new-source read-only profile>', 'exec'); (out / 'payload.private.py').write_text(raw)
    with management_gate(P / 'current-management-critical.lock'):
        result = subprocess.run(SSH + ['sudo', '-n', 'python3', '-B', '-'], input=raw.encode(), capture_output=True, timeout=100)
    (out / 'stdout.safe.json').write_bytes(result.stdout); (out / 'stderr.private.log').write_bytes(result.stderr)
    value = {'actualExit': result.returncode, 'source': SOURCE, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalAccepted': False}
    if result.returncode == 0: value['result'] = json.loads(result.stdout)
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True)); print(json.dumps(value)); return result.returncode


if __name__ == '__main__': raise SystemExit(main())
