"""Technical join of two qualified 3b7f activations of the same run; no old0fd or VM operation."""
import hashlib
import inspect
import json
import os
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg1271_current_native_gap import coordinates
from lan_server import run

SOURCE='3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'
SLOT='pg2390-same-source-native-join-v1'

CODE=r'''
import datetime,hashlib,json,os,subprocess,zipfile
from pathlib import Path
os.umask(0o077)
def require(v):
 if not v:raise ValueError('same source qualified activation join refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
B=Path('/home/mini/schubert-nk-pgpt');O=B/'runs/PG2390-native-join-v1';require(not O.exists())
roots=[B/'runs/PG2284-native-v1',B/'runs/PG2384-native-v1'];inputs=[];streams=[];sessions=[]
for root,digest in zip(roots,MANIFESTS,strict=True):
 require(sha(root/'manifest.safe.json')==digest)
 result=json.loads((root/'manifest.safe.json').read_bytes());v=json.loads((root/'input.safe.json').read_bytes())
 require(result['actualExit']==0 and result['productionSource']==v['productionSource']==SOURCE and result['classByteMismatch']==0 and result['oldNativeImported']is False and result['currentNativeStreams']==9 and result['validatedNativePoints']==10 and result['inspectorLatestClosingOnly']and result['inspectorProbeMonotonic'])
 require(len(v['selected'])==10)
 for n,h in v['files'].items():require(sha(root/n)==h)
 inspector=[i for i,p in enumerate(v['selected'])if p['unit']=='schubert-nk-inbox-inspector.service']
 require(len(inspector)==2 and v['selected'][inspector[0]]['relative'].endswith('.closing.exec')and v['selected'][inspector[1]]['relative'].endswith('.terminal.exec'))
 for i,p in enumerate(v['selected']):
  f=root/(str(i)+'.exec');require(sha(f)==p['sha256']and f.stat().st_size==p['bytes'])
  if i!=inspector[1]:streams.append(f)
 inputs.append(v)
require(len(streams)==18)
old=inputs[0]['qualifiedFull'];full=inputs[1]['qualifiedFull'];require(full['tests']==3635 and full['mainClasses']==old['mainClasses']==1643 and full['staticSixModules']==0)
require(sha(B/'runs/PG2300-six-v1/manifest.safe.json')==full['serverManifestSha256'])
modules=['protocol','storage','bootstrap','api','web','batch'];executions=[];jars={};main_count=0
for m in modules:
 paths=[B/'source-full-PG2228/src'/('schubert-nk-'+m)/'target'/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'),B/'source-full-PG2300/src'/('schubert-nk-'+m)/'target'/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')]
 for p,v in zip(paths,[old,full],strict=True):require(sha(p)==v['jarHashes'][m])
 images=[]
 for p in paths:
  with zipfile.ZipFile(p)as z:images.append({n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')})
 require(images[0]==images[1]);main_count+=len(images[1]);jars[m]=paths[1]
 t=paths[1].parent;p=t/'jacoco.exec';require(sha(p)==full['qualificationInputs'][m]['exec']);executions.append(p)
require(main_count==1643)
O.mkdir(mode=0o700);J=B/'tools/jdk-25.0.4/bin';libs=[]
for name,digest in inputs[1]['libraries'].items():
 p=B/'m2/repository'/name;require(sha(p)==digest);libs.append(str(p))
require(inputs[0]['libraries']==inputs[1]['libraries'])
classes=O/'classes';classes.mkdir(mode=0o700);cp=':'.join(libs)
names=['NativeCoverage.java','NativeSessions571.java','NativeSessions571Test.java','NativeCoverageXml471.java','NativePointDominance.java','NativePointDominanceTest.java']
r=subprocess.run([str(J/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(roots[1]/n)for n in names]],capture_output=True,timeout=60);require(r.returncode==0 and not r.stdout and not r.stderr)
cp=str(classes)+':'+cp
for root,v in zip(roots,inputs,strict=True):
 early=next(i for i,p in enumerate(v['selected'])if p['relative'].endswith('.terminal.exec')and p['unit']=='schubert-nk-inbox-inspector.service')
 closing=next(i for i,p in enumerate(v['selected'])if p['relative'].endswith('.closing.exec')and p['unit']=='schubert-nk-inbox-inspector.service')
 r=subprocess.run([str(J/'java'),'-cp',cp,'NativePointDominance',str(root/(str(early)+'.exec')),str(root/(str(closing)+'.exec'))],capture_output=True,timeout=30);require(r.returncode==0 and r.stdout==b'sameSessionProbeMonotonic=true;latestClosingOnly=true\n'and not r.stderr)
 for i,p in enumerate(v['selected']):
  if i==early:continue
  r=subprocess.run([str(J/'java'),'-cp',cp,'NativeSessions571',str(p['lowerMs']),str(p['upperMs']),str(root/(str(i)+'.exec'))],capture_output=True,timeout=30)
  require(r.returncode==0 and not r.stderr);rows=[json.loads(x)for x in r.stdout.splitlines()];require(len(rows)==1 and rows[0]['sessions']==1);sessions.extend(rows)
require(len(sessions)==18 and len({s['sessionIdSha256']for s in sessions})==18)
union={};gaps={};xml_hashes={}
for m in modules:
 r=subprocess.run([str(J/'java'),'-cp',cp,'NativeCoverage',str(jars[m]),*[str(p)for p in executions+streams]],capture_output=True,timeout=45);require(r.returncode==0 and not r.stderr)
 value=json.loads(r.stdout);require(value['classByteMismatch']==0 and value['formal']is False);union[m]=value
 xml=O/(m+'-union.xml');r=subprocess.run([str(J/'java'),'-cp',cp,'NativeCoverageXml471',str(jars[m]),str(xml),*[str(p)for p in executions+streams]],capture_output=True,timeout=45);require(r.returncode==0 and not r.stderr and b'classMismatch0=true'in r.stdout)
 gaps[m]=coordinates(xml.read_bytes(),value);xml_hashes[m]=sha(xml)
result={'actualExit':0,'productionSource':SOURCE,'mainClassesIdentical':main_count,'qualifiedFullTests':3635,'qualifiedNativeActivations':2,'qualifiedNativeStreams':18,'distinctSessions':18,'oldSourceNativeImported':False,'VMOperations':0,'moduleCounters':union,'gaps':gaps,'xmlHashes':xml_hashes,'formalAccepted':False,'coverage100':all(union[m][k]['missed']==0 for m in modules for k in ['LINE','METHOD','CLASS','BRANCH']),'run':'PG2390-native-join-v1','completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with(O/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'manifestSha256':sha(O/'manifest.safe.json'),'result':result}))
'''


def payload():
    raw='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nSOURCE='+repr(SOURCE)+'\nMANIFESTS='+repr(['c9c413d904c7f674be643f2280c8becbe2c5dfe72ce8936282f1578338ff4966','50934d311032b16f870e7feb7c4999966fbaf58c34031e4c978a12587cc6eec4'])+'\n'+inspect.getsource(coordinates)+'\n'+CODE
    if check(raw,'<same source activation join>'):raise ValueError('all join globals required')
    compile(raw,'<current two activation technical join>','exec');return raw


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    for n in ['pg2284-current-signed-native-qualified-v1','pg2384-current-resume-native-qualified-v1']:
        v=json.loads((W/n/'manifest.safe.json').read_bytes())
        if v['actualExit']!=0 or v['productionSource']!=SOURCE:raise ValueError('two actual current qualified native sets required')
    raw=payload();(out/'payload.private.py').write_text(raw)
    code,status=run("python3 -B - <<'PG2390'\n"+raw+'\nPG2390',timeout=240)
    (out/'observer.private.log').write_text(status)
    v={'actualExit':code,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not code:v.update(json.loads(next(x for x in status.splitlines()if x.strip().startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True))
    if not code:print(json.dumps({'actualExit':0,'classByteMismatch':0,'mainClassesIdentical':1643,'remaining':{k:sum(m[k]['missed']for m in v['result']['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']},'manifestSha256':v['manifestSha256'],'formalAccepted':False}))
    else:print(json.dumps(v))
    return code


if __name__=='__main__':raise SystemExit(main())
