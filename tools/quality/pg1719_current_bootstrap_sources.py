"""Current completed2741 existingADMIN profile; all dependencies before ownership."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'vm/050_s1'))
import pg983_current_bootstrap_sources as prior
from pg1446_current_cold_stage import W
from pg1700_new_source_live_binding import SOURCE,DIGEST
from pg1681_closed_candidate_sources import JAVA_PREFLIGHT,INPUT_TEST

TOOLS='pg1719-current-bootstrap-tools-v1'


def bind(raw):
    for old,new in [
        ('Pg983','Pg1719'),('PG983','PG1719'),('pg983','pg1719'),
        ('pg1719-bootstrap-tools-v3',TOOLS),
        ('pg978-bootstrap-before-v2','pg1718-current-bootstrap-before-v1'),
        ('40ef6e894573d2ffab1d1732124960f9c98d5f97',SOURCE),
        ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524',DIGEST),
        ('PG932','PG1638'),('pg932','pg1638'),
        ('cc9ed874-7f4f-450e-a188-8de1e42c8441','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),
        ('cc9ed8747f4f450ea1888de1e42c8441','3d69f5af6bac46b1a5407591c4a79a0d'),
        ('eeae04ea-713c-4f2d-888d-358fb4bed274','02e941b9-1c52-4018-a193-63dd00b269af'),
        ('2026-10-09T23:31:22.087768Z','2026-10-12T14:19:28.968927Z'),
        ('091663ce-1cf4-47e7-8311-218ebb0c8653','40da389f-23fc-4ad4-a71b-cf72a6bd5a62'),
        ('2026-10-09T23:56:48.112404Z','2026-10-12T14:45:34.509749Z'),
        ('0bb4d6f3b9e74cdc91c553748a4cd018','fe43e94b1fbf4886bb4ab3922fd16f9c'),
        ('202927375873','68542820690'),('pg963','pg1703'),('==594','==674')]:raw=raw.replace(old,new)
    return raw


def files(baseline_sha):
    before=json.loads((W/'pg1718-current-bootstrap-before-v1/manifest.safe.json').read_bytes())
    if before.get('actualExit')!=0 or before.get('productionSource')!=SOURCE or before.get('beforeSha256')!=baseline_sha or before.get('batchRows')!=674:
        raise ValueError('actual current complete enriched baseline required')
    result={bind(name):bind(raw)for name,raw in prior.files(baseline_sha).items()}
    result['pg1703_parent_receipt.py']=(W/'pg1703-new-source-owned-stop-tools-v1/pg1703_parent_receipt.py').read_text()
    helper=result['pg1719_bootstrap_existing.py']
    helper=helper.replace('strict(baseline_path,0o600,33554432)','strict(baseline_path,0o600,67108864)')
    marker="query+'commit;']).splitlines()"
    if helper.count(marker)!=1:raise ValueError('one bounded complete24 query required')
    helper=helper.replace(marker,"query+'commit;'],67108864).splitlines()")
    result['pg1719_bootstrap_existing.py']=helper
    java=result['Pg1719BootstrapExisting.java']
    preflight=JAVA_PREFLIGHT.replace('pg1681_input_preflight.py','pg1719_input_preflight.py').replace('PG1681_INPUT_CLOSURE_READY','PG1719_INPUT_CLOSURE_READY')
    marker='    require(MaintenanceFileLock.create().tryExclusive('
    if java.count(marker)!=1:raise ValueError('one preownership input-closure boundary required')
    java=java.replace(marker,'    beforeOwnership(Pg1719BootstrapExisting::verifyInputClosure);\n'+marker)
    java=java.replace('  public static void main(String[] args)throws Exception{',preflight+'\n  public static void main(String[] args)throws Exception{')
    result['Pg1719BootstrapExisting.java']=java
    result['Pg1719BootstrapInputTest.java']=INPUT_TEST.replace('Pg1681InputBoundaryTest','Pg1719BootstrapInputTest').replace('Pg1640UnusedStage','Pg1719BootstrapExisting').replace('PG1681','PG1719')
    result['pg1719_input_preflight.py']=PREFLIGHT
    for name,raw in result.items():
        if name.endswith('.py'):compile(raw,'<current Bootstrap dependency '+name+'>','exec')
    return result


PREFLIGHT=r'''
import ast,hashlib,json,os,pathlib,re,stat,subprocess
def require(v):
 if not v:raise ValueError('current Bootstrap dependency preflight refused')
require(os.geteuid()==0)
root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1719-current-bootstrap-tools-v1')
def read(p):
 s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and s.st_size<=2097152 and not os.listxattr(p))
 raw=p.read_bytes();t=p.lstat();require(s==t);return raw
pins=json.loads(read(root/'payload-sha256.json'));require(type(pins)is dict and bool(pins))
require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(pins)|{'payload-sha256.json'})
directories={str(p)for n in pins for p in pathlib.PurePosixPath(n).parents if str(p)!='.'}
require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_dir()}==directories)
for p in [root,*root.rglob('*')]:
 require(not p.is_symlink())
 if p.is_dir():s=p.lstat();require((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700)and not os.listxattr(p))
standard={'ast','datetime','hashlib','json','os','pathlib','re','stat','subprocess','sys','time','ctypes','secrets','traceback','dbus'}
for name,digest in pins.items():
 require(type(name)is str and bool(name)and not name.startswith('/')and '\\'not in name and all(p not in ('','.','..')for p in name.split('/'))and type(digest)is str and re.fullmatch('[a-f0-9]{64}',digest)is not None)
 raw=read(root/name);require(hashlib.sha256(raw).hexdigest()==digest)
 if name.endswith('.py'):
  for n in ast.walk(ast.parse(raw)):
   modules=[v.name for v in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.level==0 and n.module else[]
   require(not isinstance(n,ast.ImportFrom)or n.level==0 and n.module is not None)
   for m in modules:
    head=m.split('.')[0];require(head+'.py'in pins if head.startswith('pg')else head in standard)
require({'Pg1719BootstrapExisting.class','Pg1719BootstrapExisting$References.class','pg1719_bootstrap_existing.py','pg1703_parent_receipt.py'}<=set(pins))
release=pathlib.Path('/opt/schubert-nk/current');require(str(release.readlink())=='/opt/schubert-nk/releases/0.1.0-PG1638')
raw=(release/'RELEASE-MANIFEST.json').read_bytes();require(hashlib.sha256(raw).hexdigest()=='195e0668bc5a1fea2cbf2a93747e0cdcbf1bcb66c3f3f23a362fca7c89ae82e1')
data=json.loads(raw);require(data['source']['commit']=='2741c4546afad6c1e8b6efbd53dfb58144edf7bb'and len(data['artifacts'])==187)
for row in data['artifacts']:
 p=release/row['path'];require(p.is_file()and not p.is_symlink()and p.stat().st_size==row['size']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'])
subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(release/'RELEASE-MANIFEST.json'),'-sigfile','/var/lib/pgpt-s1-preservation/pg1638-manifest.sig'],check=True,timeout=5,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('PG1719_INPUT_CLOSURE_READY',flush=True)
'''
