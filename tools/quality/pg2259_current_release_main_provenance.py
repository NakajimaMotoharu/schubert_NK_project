"""Read-only all1643 signed runtime Main vs fresh3633 full, including physical debug-only class."""
import datetime
import hashlib
import json
import os
import subprocess
from lan_server import run
from pg1446_current_cold_stage import W,SSH
from pg2176_newsource_normal_observer import SOURCE,BOM
from pg2208_current_newboot_cold_sources import BOOT


def compare(expected,actual):
    if type(expected)is not dict or len(expected)!=1643 or type(actual)is not dict or set(expected)!=set(actual):raise ValueError('whole actual runtime Main set required')
    if any(type(v)is not list or not v or any(h!=expected[p]for h in v)for p,v in actual.items()):raise ValueError('every physical signed Main occurrence must match current full byte')
    return {'mainClasses':len(expected),'physicalOccurrences':sum(map(len,actual.values())),'classByteMismatch':0}


def payload(expected):
    return 'EXPECTED='+repr(expected)+'\nSOURCE='+repr(SOURCE)+'\nBOM='+repr(BOM)+'\nBOOT='+repr(BOOT)+'''\nimport hashlib,json,pathlib,stat,subprocess,zipfile
def require(v):
 if not v:raise ValueError('signed current runtime Main provenance refused')
require(pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()==BOOT)
release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG2126');current=pathlib.Path('/opt/schubert-nk/current');require(current.readlink()==release)
raw=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==BOM);manifest=json.loads(raw)
require(manifest['source']['commit']==SOURCE and len(manifest['artifacts'])==187)
subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile','/var/lib/pgpt-s1-preservation/pg2126-manifest.sig'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
actual={};jars={}
for record in manifest['artifacts']:
 if not record['path'].endswith('.jar'):continue
 p=release/record['path'];s=p.lstat();require(stat.S_ISREG(s.st_mode)and s.st_uid==0 and s.st_nlink==1 and s.st_size==record['size'])
 digest=hashlib.sha256(p.read_bytes()).hexdigest();require(digest==record['sha256'])
 with zipfile.ZipFile(p)as z:
  names=z.namelist();require(len(names)==len(set(names)))
  for n in names:
   if n.startswith('dev/codex/schubert/nk/')and n.endswith('.class'):
    actual.setdefault(n,[]).append(hashlib.sha256(z.read(n)).hexdigest())
 require(p.lstat()==s);jars[record['path']]=digest
require(current.readlink()==release and(release/'RELEASE-MANIFEST.json').read_bytes()==raw)
print(json.dumps({'actual':actual,'jars':jars,'startsStopsWrites0':True,'source':SOURCE,'boot':BOOT}))
'''


def main():
    os.umask(0o077);out=W/'pg2259-current-release-main-provenance-v1';out.mkdir(mode=0o700)
    qualification=json.loads((W/'pg2236-root-host-integration-full-qualified-v1/manifest.safe.json').read_bytes())
    if qualification['actualExit']!=0 or qualification['result']['productionSource']!=SOURCE:raise ValueError('actual current full qualification required')
    code="import hashlib,json,pathlib\np=pathlib.Path('/home/mini/schubert-nk-pgpt/runs/PG2228-six-v1/manifest.safe.json');raw=p.read_bytes();v=json.loads(raw)\nassert hashlib.sha256(raw).hexdigest()=="+repr(qualification['result']['serverManifestSha256'])+"\nassert v['actualExit']==0 and v['tests']==3633\nprint(json.dumps({p:h for m in v['modules'].values()for p,h in m['mainClassHashes'].items()}))\n"
    rc,report=run("python3 - <<'CURRENT_MAIN'\n"+code+'\nCURRENT_MAIN',timeout=20)
    if rc:raise ValueError('full immutable Main hash input unavailable')
    expected=json.loads(next(l for l in report.splitlines()if l.strip().startswith('{')))
    raw=payload(expected);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=45)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'boot':BOOT,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startUTC':started,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:
        actual=json.loads(r.stdout);value.update(compare(expected,actual['actual']),jars=actual['jars'],startsStopsWrites0=True,oldNativeImported=False)
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='jars'}));return r.returncode


if __name__=='__main__':raise SystemExit(main())
