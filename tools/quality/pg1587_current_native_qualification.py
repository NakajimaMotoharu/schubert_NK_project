"""Same-source eight native sessions/CRC + qualified1532 full host, no VM mutation."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import tarfile
from lan_server import copy,run
from pg1446_current_cold_stage import W,SSH
from pg1579_current_owned_stop_sources import SOURCE
from pg1271_current_native_gap import coordinates

CODE=r'''
import datetime,hashlib,json,os,subprocess,tarfile
from pathlib import Path
os.umask(0o077)
def require(v):
 if not v:raise ValueError('current native sameSource qualification refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
B=Path('/home/mini/schubert-nk-pgpt');O=B/'runs/PG1587-native-v1';require(not O.exists());O.mkdir(mode=0o700)
archive=B/'transfer/PG1587-native-input.tar';require(sha(archive)==ARCHIVE_SHA)
with tarfile.open(archive,'r:')as tar:
 members=tar.getmembers();require(all(m.isfile()and '/'not in m.name and m.name not in {'','..','.'}for m in members)and len({m.name for m in members})==len(members));tar.extractall(O,filter='data')
v=json.loads((O/'input.safe.json').read_bytes());require(v['productionSource']=='4d6bcbddb417b76d27e52d5d9640752c300edccf'and len(v['selected'])==8)
for name,h in v['files'].items():require(sha(O/name)==h)
full=json.loads((B/'runs/PG1532-six-v1/manifest.safe.json').read_bytes());qualified=v['qualifiedFull']
require(sha(B/'runs/PG1532-six-v1/manifest.safe.json')==qualified['serverManifestSha256']and full['productionSource']==v['productionSource']and full['actualExit']==full['mavenExit']==0 and full['tests']==3583)
J=B/'tools/jdk-25.0.4/bin';repo=B/'m2/repository';libs=[]
for rel,digest in v['libraries'].items():p=repo/rel;require(sha(p)==digest);libs.append(str(p))
classes=O/'classes';classes.mkdir(mode=0o700);cp=':'.join(libs)
commands=[('compile',[str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(O/n)for n in ['NativeCoverage.java','NativeSessions571.java','NativeSessions571Test.java','NativeCoverageXml471.java']]]),('session-oracle',[str(J/'java'),'-cp',str(classes)+':'+cp,'NativeSessions571Test'])]
for label,args in commands:
 r=subprocess.run(args,capture_output=True,timeout=30);(O/(label+'.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
cp=str(classes)+':'+cp;sessions=[];streams=[]
for i,selected in enumerate(v['selected']):
 p=O/(str(i)+'.exec');require(p.stat().st_size==selected['bytes']and sha(p)==selected['sha256']);streams.append(p)
 r=subprocess.run([str(J/'java'),'-cp',cp,'NativeSessions571',str(selected['lowerMs']),str(selected['upperMs']),str(p)],capture_output=True,timeout=30)
 (O/(str(i)+'-session.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
 rows=[json.loads(line)for line in r.stdout.splitlines()];require(len(rows)==1 and rows[0]['sessions']==1);sessions.extend(rows)
modules=['protocol','storage','bootstrap','api','web','batch'];executions=[];jars={}
for m in modules:
 t=B/'source-full-PG1532/src'/('schubert-nk-'+m)/'target';p=t/'jacoco.exec';jar=t/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')
 require(sha(p)==qualified['qualificationInputs'][m]['exec']and sha(jar)==qualified['jarHashes'][m]);executions.append(p);jars[m]=jar
 require(sha(t/'site/jacoco/jacoco.xml')==qualified['qualificationInputs'][m]['coverageXml'])
local={};host={};union={};gain={};xml_hashes={};gaps={};start=datetime.datetime.now(datetime.timezone.utc)
for m in modules:
 for label,data in [('local',[executions[modules.index(m)]]),('host',executions),('union',executions+streams)]:
  r=subprocess.run([str(J/'java'),'-cp',cp,'NativeCoverage',str(jars[m]),*[str(p)for p in data]],capture_output=True,timeout=45)
  (O/(m+'-'+label+'.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
  result=json.loads(r.stdout);require(result['classByteMismatch']==0 and result['formal']is False)
  (local if label=='local'else host if label=='host'else union)[m]=result
 require(all(local[m][k]==qualified['coverage'][m][k]for k in ['LINE','METHOD','CLASS','BRANCH']))
 gain[m]={k:host[m][k]['missed']-union[m][k]['missed']for k in ['LINE','METHOD','CLASS','BRANCH']};require(all(n>=0 for n in gain[m].values()))
 xml=O/(m+'-union.xml');r=subprocess.run([str(J/'java'),'-cp',cp,'NativeCoverageXml471',str(jars[m]),str(xml),*[str(p)for p in executions+streams]],capture_output=True,timeout=45)
 (O/(m+'-xml.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr and b'classMismatch0=true'in r.stdout)
 xml_hashes[m]=sha(xml);gaps[m]=coordinates(xml.read_bytes(),union[m])
result={'actualExit':0,'run':'PG1587-native-v1','productionSource':v['productionSource'],'currentNativeStreams':8,'currentNativeSessions':sessions,'oldNativeImported':False,'excludedHistorical':v['excludedHistorical'],'hostOnlyCounters':host,'moduleLocalCounters':local,'moduleCounters':union,'gain':gain,'xmlHashes':xml_hashes,'gaps':gaps,'qualified1532Tests':3583,'classByteMismatch':0,'coverage100':all(union[m][k]['missed']==0 for m in modules for k in ['LINE','METHOD','CLASS','BRANCH']),'formalAccepted':False,'wholeNativeAccepted':False,'remainingInspectorCurrent':True,'remainingBootstrapCurrent':True,'startedUTC':start.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceChanged0':True,'newVmOperations0':True}
with(O/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'manifestSha256':sha(O/'manifest.safe.json'),'result':result}))
'''

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    os.umask(0o077);out=W/'pg1587-current-native-qualified-v1';out.mkdir(mode=0o700)
    catalog=json.loads((W/'pg1586-current-native-catalog-v2/manifest.safe.json').read_bytes())
    if catalog['actualExit']!=0 or catalog['productionSource']!=SOURCE or len(catalog['selected'])!=8:raise ValueError('actual current eight catalog required')
    require_bytes=8*16777216+805306368
    if os.statvfs(W).f_bavail*os.statvfs(W).f_frsize<require_bytes:raise ValueError('native capture/close capacity required')
    for i,v in enumerate(catalog['selected']):
        path=out/(str(i)+'.exec')
        with path.open('xb')as f:
            r=subprocess.run(SSH+['sudo','-n','cat','/run/schubert-nk/pt-coverage/'+v['relative']],stdout=f,stderr=subprocess.PIPE,timeout=20);f.flush();os.fsync(f.fileno())
        if r.returncode!=0 or r.stderr or sha(path)!=v['sha256']or path.stat().st_size!=v['bytes']:raise ValueError('private current immutable native read refused')
    root=Path(__file__).parent/'vm/050_s1'
    for name in ['NativeCoverage.java','NativeSessions571.java','NativeSessions571Test.java','NativeCoverageXml471.java']:
        (out/name).write_bytes((root/name).read_bytes())
    libs={};repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository')
    for pattern in ['org/jacoco/org.jacoco.core/0.8.15/*.jar','org/jacoco/org.jacoco.report/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar']:
        paths=list(repo.glob(pattern))
        if len(paths)!=1:raise ValueError('fixed same helper library required')
        libs[str(paths[0].relative_to(repo))]=sha(paths[0])
    full=json.loads((W/'pg1542-filesystem-full-qualified-v3/manifest.safe.json').read_bytes())
    if full['actualExit']!=0 or full['result']['productionSource']!=SOURCE:raise ValueError('qualified current1532 host source required')
    data={k:catalog[k]for k in ['productionSource','selected','excludedHistorical']};data['qualifiedFull']=full['result'];data['libraries']=libs
    data['files']={p.name:sha(p)for p in out.iterdir()if p.is_file()}
    (out/'input.safe.json').write_text(json.dumps(data,sort_keys=True))
    archive=out/'input.private.tar'
    with tarfile.open(archive,'x:')as tar:
        for p in out.iterdir():
            if p!=archive:tar.add(p,arcname=p.name,recursive=False)
    code,status=run("python3 -c \"import os,json;v=os.statvfs('/home/mini/schubert-nk-pgpt');print(json.dumps({'availableBytes':v.f_bavail*v.f_frsize}))\"",timeout=30)
    if code or json.loads(next(line for line in status.splitlines()if line.strip().startswith('{')))['availableBytes']<10737418240+archive.stat().st_size:
        raise ValueError('current server transfer/analysis preservation capacity refused')
    # Server-only work uses existing qualified target/class/exec bytes, never a new full campaign.
    code,status=copy(str(archive),'/home/mini/schubert-nk-pgpt/transfer/PG1587-native-input.tar',timeout=120)
    (out/'transfer.private.log').write_text(status)
    if code:raise ValueError('private current native transfer refused')
    source='ARCHIVE_SHA='+repr(sha(archive))+'\n'+inspect.getsource(coordinates)+'\n'+CODE
    source='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\ndef require(value):\n if not value:raise ValueError("current coverage XML counter mismatch")\n'+source
    (out/'server-payload.private.py').write_text(source)
    code,status=run("python3 - <<'PG1587'\n"+source+'\nPG1587',timeout=240)
    (out/'observer.private.log').write_text(status)
    value={'actualExit':code,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'productionSource':SOURCE,'payloadSha256':hashlib.sha256(source.encode()).hexdigest(),'formalAccepted':False}
    if code==0:value.update(json.loads(next(line for line in status.splitlines()if line.strip().startswith('{'))))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    if code==0:
        result=value['result'];print(json.dumps({'actualExit':0,'streams':8,'classByteMismatch':result['classByteMismatch'],'newlyCovered':{k:sum(x[k]for x in result['gain'].values())for k in ['LINE','METHOD','CLASS','BRANCH']},'remaining':{k:sum(x[k]['missed']for x in result['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']},'coverage100':result['coverage100'],'serverManifestSha256':value['manifestSha256'],'formalAccepted':False}))
    else:print(json.dumps(value))
    return code

if __name__=='__main__':raise SystemExit(main())
