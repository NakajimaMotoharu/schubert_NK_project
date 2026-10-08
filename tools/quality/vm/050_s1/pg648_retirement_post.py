"""Independent full19/signature/namespace/resource post, readonly once."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pg636_resume_post import PAYLOAD as TEMPLATE

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
P=Path('/home/mini/codex/project1/work/pgpt-vm/private')


def payload():
    raw=TEMPLATE
    replacements=(
        ('pg635-resume-preparation-v1','pg647-runtime-retirement-v1'),
        ("==494", "==504"), ("'batchRows':494", "'batchRows':504"),
        ("complete==b'onceResumePrepared=true\\nallNewScopesReturnedNormally=true\\noriginalRunCutoffUnchanged=true\\ndatabaseUpdates0=true\\nstarts0=true\\n'", "complete==b'onceResumeRetired=true\\nallNewScopesReturnedNormally=true\\noriginalCompletedUnchanged=true\\ndatabaseUpdates0=true\\nstarts0=true\\n'"),
        ('require(prepared(before,after,strict(runtime,0o644,4096)))','require(retired(before,after) and not os.path.lexists(runtime))'),
        ("require({p.name for p in runtime.parent.iterdir()}=={'pg635-once-resume.conf'}and len(fresh_sources)==len(set(fresh_sources))==19 and set(fresh_sources)==set(after['unitFiles']))", "s=runtime.parent.lstat();require((s.st_uid,s.st_gid,s.st_mode,s.st_nlink)==(0,0,stat.S_IFDIR|0o755,2)and not {'system.posix_acl_access','system.posix_acl_default'}.intersection(os.listxattr(runtime.parent)))\n  require(not list(runtime.parent.iterdir())and len(fresh_sources)==len(set(fresh_sources))==18 and set(fresh_sources)==set(after['unitFiles']))"),
        ('3a2de24f931544c0a2fd83556a659cd0','293d218b06454bd1a8ff350bb93de2d5'),
        ("base/'pg611-native-stop-v1'/(u+'.stopped.private')", "base/'pg642-native-stop-v1'/(u+'.stopped.private')"),
    )
    for old,new in replacements:
        assert raw.count(old)==1,old;raw=raw.replace(old,new)
    return raw


def main():
    os.umask(0o077)
    assert subprocess.check_output(['git','status','--porcelain'],cwd=R.parents[3])==b''
    assert (W/'pg647-retire-v1.exit').read_bytes()==b'0\n'
    slot=W/'pg648-retirement-post-v1'
    for ext in ('.safe.json','.private.log','.exit'):assert not slot.with_suffix(ext).exists()
    ssh=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(ssh,input=("MODE='retire'\n"+(R/'pg648_post_contract.py').read_text()+'\n'+payload()).encode(),capture_output=True,timeout=90)
    with slot.with_suffix('.private.log').open('xb')as f:f.write(result.stderr);f.flush();os.fsync(f.fileno())
    with slot.with_suffix('.exit').open('x')as f:f.write(str(result.returncode)+'\n')
    safe={'actualExit':result.returncode,'startedUTC':started,'endedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'privateLogSha256':hashlib.sha256(result.stderr).hexdigest(),'formalAccepted':False}
    if result.returncode==0:safe['proof']=json.loads(result.stdout)
    with slot.with_suffix('.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(result.returncode)


if __name__=='__main__':main()
