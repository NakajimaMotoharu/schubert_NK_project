"""Independent current whole signed187/metadata and actual RO bind after publication."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
from pg938_stage_post import PAYLOAD,W,P
if __name__=='__main__':
    os.umask(0o077);assert json.loads((W/'pg942-activate-v1.safe.json').read_bytes())['actualExit']==0
    body=PAYLOAD.replace('readlink()==old','readlink()==root').replace("'currentUnchanged':True","'oldReleasePreserved':True,'currentPublished':True").replace("'candidateOnly':True,'publicationNotRun':True","'candidateOnly':False,'publicationNotRun':False").replace("'installedSource':'e01612fcd7f2752df5ae0836b78538fd5e87f120'","'installedSource':'40ef6e894573d2ffab1d1732124960f9c98d5f97'")
    marker="raw=(root/'RELEASE-MANIFEST.json').read_bytes()";assert body.count(marker)==1
    body=body.replace(marker,"assert os.statvfs(root).f_flag & os.ST_RDONLY\n"+marker)
    base=W/'pg951-independent-current-post-v1';assert not Path(str(base)+'.safe.json').exists()and not Path(str(base)+'.private.log').exists()
    cmd=['ssh','-i',str(P/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(P/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
    start=datetime.datetime.now(datetime.timezone.utc);r=subprocess.run(cmd,input=body.encode(),capture_output=True,timeout=60)
    with Path(str(base)+'.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    safe={'actualExit':r.returncode,'startedUTC':start.isoformat(),'elapsedSeconds':(datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),'privateLogSha256':hashlib.sha256(r.stderr).hexdigest(),'formalAccepted':False}
    if r.returncode==0:safe.update(json.loads(r.stdout))
    with Path(str(base)+'.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));raise SystemExit(r.returncode)
