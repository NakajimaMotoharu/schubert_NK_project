"""Read-only close of the copied PG1431 disk; never repeat copy/convert/start."""
import json
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent/'vm/050_s1'))
from pg997_offline_preservation import VM, digest, identity, idle, write_new
from lan_server import run

OLD=VM/'private/pg1431-lan-standalone-v1'
OUT=VM/'private/pg1434-lan-copy-close-v1'


def main():
    os.umask(0o077)
    idle();OUT.mkdir(mode=0o700)
    before=json.loads((OLD/'begin.safe.json').read_bytes())['sourceChain']
    proof=json.loads((OLD/'offline-qualified.safe.json').read_bytes())
    assert proof['actualExit']==proof['logicalCompareExit']==proof['convertExit']==0
    assert not (OLD/'manifest.safe.json').exists()
    assert before=={p:{'identity':identity(Path(p)),'sha256':digest(Path(p))} for p in before}
    assert digest(OLD/'guest.qcow2')==proof['guestSha256']
    code,process=run("python3 -c \"import subprocess,json;v=subprocess.check_output(['ps','-eo','pid,ppid,comm'],text=True);print(json.dumps([x for x in v.splitlines() if 'sha256sum' in x or 'qemu-system' in x]))\"")
    assert code==0 and json.loads(process)==[]
    write_new(OUT/'begin.safe.json',{'oldJobActualExit':1,'remoteOldHashProcessAbsent':True,
                                   'oldCompletedManifestAbsent':True,'hashDeadlineSeconds':240,
                                   'copyReissued':False,'bootIssued':False})
    code,output=run("python3 - <<'END'\nimport os,hashlib,json\nfrom pathlib import Path\np=Path('/home/mini/schubert-nk-pgpt/vm/pg1431/guest.qcow2');s=p.stat();h=hashlib.sha256()\nwith p.open('rb') as f:\n while b:=f.read(8*1024*1024):h.update(b)\nassert s==p.stat()\nprint(json.dumps({'sha256':h.hexdigest(),'bytes':s.st_size,'mode':s.st_mode&511,'freeBytes':os.statvfs('/').f_bavail*os.statvfs('/').f_frsize}))\nEND",timeout=240)
    assert code==0
    remote=json.loads(output)
    assert remote['sha256']==proof['guestSha256'] and remote['bytes']==proof['guestBytes']
    assert remote['mode']==0o600 and remote['freeBytes']>10*1024**3
    assert before=={p:{'identity':identity(Path(p)),'sha256':digest(Path(p))} for p in before}
    idle()
    record={'run':'PG1434-lan-copy-close-v1','actualExit':0,'oldJobActualExit':1,
            'oldCompletedManifestAbsent':True,'sourceChainStable':True,'hostCompareExit':0,
            'remote':remote,'copyReissued':False,'vmBootIssued':False,'ramRestored':False,
            'oldToolNormalClose':False,'oldIntentRetired':False,'formalAccepted':False,
            'relatedBUG':'BUG1098','relatedYKT':'YKT867'}
    write_new(OUT/'manifest.safe.json',record);print(json.dumps(record))


if __name__=='__main__':main()
