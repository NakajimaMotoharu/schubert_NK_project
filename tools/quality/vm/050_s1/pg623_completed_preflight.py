"""Fresh readonly old current genuine-DONE proof plus new unused candidate; no activation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import pg613_terminal_final as baseline

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload():
    source=baseline.PAYLOAD
    for old,new in [("save=base/'pg613-terminal-final-v1'","save=base/'pg623-completed-preflight-v1'"),
                    ("'run':'PG613-terminal-final-v1'","'run':'PG623-completed-preflight-v1'")]:
        assert source.count(old)==1
        source=source.replace(old,new)
    anchor="bus=dbus.SystemBus(private=True);"
    assert source.count(anchor)==1
    candidate=r"""
candidate=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG621')
candidate_raw=(candidate/'RELEASE-MANIFEST.json').read_bytes()
require(hashlib.sha256(candidate_raw).hexdigest()=='4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e')
candidate_data=json.loads(candidate_raw)
require(candidate_data['source']['commit']=='72fb7440697ee1048a5c0145055dc1cc3c577914'and len(candidate_data['artifacts'])==187 and candidate_data['versions']['schema']=='028')
expected={v['path']for v in candidate_data['artifacts']}|{'RELEASE-MANIFEST.json','SHA256SUMS'}
require({p.relative_to(candidate).as_posix()for p in candidate.rglob('*')if p.is_file()}==expected)
for p in(candidate,*candidate.rglob('*')):
 s=p.lstat();executable=p.relative_to(candidate).as_posix()in('operations/bin/schubert-nkctl','operations/bin/schubert-nk-inbox-inspector')
 require(not p.is_symlink()and s.st_uid==0 and s.st_gid==986 and stat.S_IMODE(s.st_mode)==(0o750 if p.is_dir()or executable else 0o640))
 if p.is_file():require(stat.S_ISREG(s.st_mode)and s.st_nlink==1)
for v in candidate_data['artifacts']:
 p=candidate/v['path'];require(p.stat().st_size==v['size']and hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'])
command(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(candidate/'RELEASE-MANIFEST.json'),'-sigfile',str(base/'pg621-manifest.sig')],4096)
"""
    source=source.replace(anchor,candidate+'\n'+anchor)
    marker="'formalAccepted':False}"
    assert source.count(marker)==1
    source=source.replace(marker,"'formalAccepted':False,'candidateWhole187SignatureVerified':True,'candidateSource':'72fb7440697ee1048a5c0145055dc1cc3c577914','candidateManifestSha256':'4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e','activationNotRun':True}")
    compile(source,'<fresh current completion and unused signed candidate>','exec')
    return source


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    operator=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R.parents[3],text=True).strip()
    stage=json.loads((W/'pg622-candidate-stage-v2.safe.json').read_bytes())
    assert stage['actualExit']==0 and stage['currentUnchanged']
    log=W/'pg623-completed-preflight-v1.private.log'
    assert not log.exists() and not (W/'pg623-completed-preflight-v1.safe.json').exists()
    classes=W/'pg611-native-tools-v1'
    files={n:classes/n for n in ('Pg611NativeStop.class','Pg611NativeStop$References.class')}
    for n in ('pg611_native_refs.py','pg611_native_owned_stop.py','pg526_term_witness.py',
              'pg526_native_term_witness.py','pg611_parent_receipt.py','pg611_durable.py'):
        files[n]=R/n
    hashes={n:hashlib.sha256(p.read_bytes()).hexdigest()for n,p in files.items()}
    prefix='HASHES='+repr(hashes)+'\nRECEIPT='+repr((R/'pg611_parent_receipt.py').read_text())+'\n'
    code=prefix+payload()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes',
         '-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),
         '-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    result=subprocess.run(ssh,input=code.encode(),capture_output=True,timeout=90)
    with log.open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':result.returncode,'operatorSource':operator,'startedUTC':started,
          'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),
          'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if result.returncode==0:
        proof=json.loads(result.stdout)
        assert proof['run']=='PG623-completed-preflight-v1' and proof['candidateWhole187SignatureVerified']
        safe['proof']=proof
    with (W/'pg623-completed-preflight-v1.safe.json').open('x')as f:
        json.dump(safe,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':result.returncode,'currentUnchanged':result.returncode==0,
                      'allOriginalBackupDbUnitValuesRechecked':result.returncode==0,
                      'activationNotRun':True,'formalAccepted':False}))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
