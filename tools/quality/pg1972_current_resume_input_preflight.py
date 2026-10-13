"""Current qualified full-before inputs for fresh completed-run resume, readonly."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate

SLOT='pg1972-current-resume-input-preflight-v1'
PAYLOAD=r'''
import hashlib,json,pathlib,stat
base=pathlib.Path('/var/lib/pgpt-s1-preservation');raw=(base/'pg1963-reload-ref-scoped-full-post-v1/before.private.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='ee13ec0b75e1320f4daba711ef90d24b2c05ae588c3b27fedb0224114896fc15'
before=json.loads(raw);runtime=pathlib.Path('/run/systemd/system');unitdir=runtime/'schubert-nk-morning-controller.service.d'
def metadata(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
assert set(before['runtime'])=={str(runtime),str(unitdir)}
for p in [runtime,unitdir]:
 assert metadata(p)==before['runtime'][str(p)]['metadata']and metadata(p)[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(p)
assert not list(unitdir.iterdir())and [p.name for p in runtime.iterdir()]==[unitdir.name]
base_unit=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1846/systemd/schubert-nk-morning-controller.service').read_bytes()
native_file=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf');native=native_file.read_bytes()
starts=[v[len(b'ExecStart='):]for v in base_unit.splitlines()if v.startswith(b'ExecStart=')];assert len(starts)==1
assert starts[0].startswith(b'/usr/bin/java ')and starts[0].endswith(b' dev.codex.schubert.nk.batch.file.MorningProcessMain')and b'--resume'not in starts[0]and b'-javaagent'not in starts[0]
agent=b'/usr/bin/java -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=destfile=/run/schubert-nk/pt-coverage/parent/parent.exec,append=false '
argv=agent+starts[0][len(b'/usr/bin/java '):]
wanted=b'# PGPT only: same entry/byte/owners; JaCoCo and explicit same-run resume.\n[Service]\nExecStart=\nExecStart='+argv+b'\nReadWritePaths=/run/schubert-nk/pt-coverage/parent\n'
assert native==wanted
assert not(pathlib.Path('/var/lib/schubert-nk/maintenance')/'active').exists()
assert (pathlib.Path('/var/lib/schubert-nk/maintenance/attempts')/'9adbf05a-61d0-408b-b51d-ab19c7e5b16a.done').is_file()
assert not(unitdir/'zz-pg1973-once-resume.conf').exists()
print(json.dumps({'actualExit':0,'currentSource':'0fd734195b4d5338f6b7e860e087cce561d49562','privateBeforeSha256':hashlib.sha256(raw).hexdigest(),'runtimeEmptyOwnedDirectoryVerified':True,'runtimeDirectoryMetadata':metadata(unitdir),'baseUnitSha256':hashlib.sha256(base_unit).hexdigest(),'nativeDropinSha256':hashlib.sha256(native).hexdigest(),'baseAndNativeLiteralWholeByteJoin':True,'activeAbsent':True,'selectedOldActivationDonePresent':True,'newRuntimeNameAbsent':True,'startsStopsReloadsSqlWrites0':True,'formalAccepted':False}))
'''


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=PAYLOAD.encode(),capture_output=True,timeout=30)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(PAYLOAD.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:result.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
