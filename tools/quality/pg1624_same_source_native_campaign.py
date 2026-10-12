"""Qualified same-source distinct resume/new-run sessions, not same-session union.

Finite diagnostic campaign only; no VM operations, old-source exec, exclusion,
formal acceptance or Production expected-value generation.
"""
import hashlib
import inspect
import json
import os
from lan_server import run,copy
from pg1446_current_cold_stage import W
from pg1609_current_ordinary_owned_stop_sources import SOURCE
from pg1271_current_native_gap import coordinates

SLOT='pg1624-same-source-native-campaign-v1'
COHORTS=[('pg1590-current-native-qualified-v2','PG1590-native-v1'),('pg1618-current-ordinary-native-qualified-v3','PG1618-native-v1')]

def qualify_inputs(records):
    if type(records)is not list or len(records)!=2:raise ValueError('two independently qualified current cohorts required')
    sessions=set();baseline=None
    for x in records:
        if type(x)is not dict or x.get('actualExit')!=0:raise ValueError('qualified cohort exit required')
        r=x['result'];items=r['currentNativeSessions']
        if r['productionSource']!=SOURCE or r['classByteMismatch']!=0 or len(items)!=8 or r['oldNativeImported']is not False or r['qualified1532Tests']!=3583:raise ValueError('same-source actual cohort qualification refused')
        if baseline is None:baseline=r['hostOnlyCounters']
        elif baseline!=r['hostOnlyCounters']:raise ValueError('same qualified host baseline required')
        for item in items:
            if type(item)is not dict or set(item)!={'index','sessions','sessionIdSha256','startMs','dumpMs'}:raise ValueError('actual native session schema refused')
            h=item['sessionIdSha256']
            if type(h)is not str or len(h)!=64 or any(v not in '0123456789abcdef'for v in h):raise ValueError('actual session digest refused')
            if type(item['sessions'])is not int or item['sessions']!=1 or h in sessions or type(item['startMs'])is not int or type(item['dumpMs'])is not int or not 0<item['startMs']<=item['dumpMs']:raise ValueError('same-session/point union forbidden')
            sessions.add(item['sessionIdSha256'])
    if len(sessions)!=16:raise ValueError('distinct actual native sessions required')
    return {'distinctSessions':16,'sameSessionPointUnion':False,'source':SOURCE,'formalAccepted':False}

SERVER=r'''
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
COUNTERS=('LINE','METHOD','CLASS','BRANCH')
os.umask(0o077)
def require(v):
 if not v:raise ValueError('sameSource distinct-session native campaign refused')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG1624-native-campaign-v1';require(not out.exists());out.mkdir(mode=0o700)
records=[];inputs=[];roots=[]
for directory,manifest_sha in COHORTS:
 root=b/'runs'/directory;require(sha(root/'manifest.safe.json')==manifest_sha)
 records.append({'actualExit':0,'result':json.loads((root/'manifest.safe.json').read_bytes())});inputs.append(json.loads((root/'input.safe.json').read_bytes()));roots.append(root)
qualification=qualify_inputs(records);require(inputs[0]['libraries']==inputs[1]['libraries']and inputs[0]['qualifiedFull']==inputs[1]['qualifiedFull'])
full=inputs[1]['qualifiedFull'];source=b/'source-full-PG1532';repo=b/'m2/repository';libraries=[]
require(sha(b/'runs/PG1532-six-v1/manifest.safe.json')==full['serverManifestSha256'])
for name,digest in inputs[1]['libraries'].items():
 p=repo/name;require(sha(p)==digest);libraries.append(str(p))
helpers=['NativeCoverage.java','NativeCoverageXml471.java','NativeSessions571.java','NativeSessions571Test.java']
for name in helpers:require(sha(roots[1]/name)==inputs[1]['files'][name])
classes=out/'classes';classes.mkdir(mode=0o700);j=b/'tools/jdk-25.0.4/bin';cp=':'.join(libraries)
r=subprocess.run([str(j/'javac'),'-Xlint:all','-Werror','-cp',cp,'-d',str(classes),*[str(roots[1]/n)for n in helpers]],capture_output=True,timeout=30)
(out/'compile.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
cp=str(classes)+':'+cp;streams=[];sessions=[];started=datetime.datetime.now(datetime.timezone.utc)
for root,inp,record in zip(roots,inputs,records):
 require(len(inp['selected'])==8 and inp['productionSource']==qualification['source'])
 for index,selected in enumerate(inp['selected']):
  p=root/(str(index)+'.exec');require(sha(p)==selected['sha256']and p.stat().st_size==selected['bytes'])
  r=subprocess.run([str(j/'java'),'-cp',cp,'NativeSessions571',str(selected['lowerMs']),str(selected['upperMs']),str(p)],capture_output=True,timeout=30)
  (out/(root.name+'-'+str(index)+'-session.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
  observed=[json.loads(line)for line in r.stdout.splitlines()];require(observed==[record['result']['currentNativeSessions'][index]])
  sessions.extend(observed);streams.append(p)
require(len(streams)==len(sessions)==16 and len({v['sessionIdSha256']for v in sessions})==16)
modules=['protocol','storage','bootstrap','api','web','batch'];host=[];jars={}
for m in modules:
 target=source/'src'/('schubert-nk-'+m)/'target';p=target/'jacoco.exec';jar=target/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar')
 require(sha(p)==full['qualificationInputs'][m]['exec']and sha(jar)==full['jarHashes'][m]and sha(target/'site/jacoco/jacoco.xml')==full['qualificationInputs'][m]['coverageXml']);host.append(p);jars[m]=jar
counters={};gaps={};xml_hashes={}
for m in modules:
 r=subprocess.run([str(j/'java'),'-cp',cp,'NativeCoverage',str(jars[m]),*[str(p)for p in host+streams]],capture_output=True,timeout=45)
 (out/(m+'-counter.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr)
 v=json.loads(r.stdout);require(v['classByteMismatch']==0 and v['formal']is False);counters[m]=v
 require(all(v[k]['missed']<=records[0]['result']['moduleCounters'][m][k]['missed']and v[k]['missed']<=records[1]['result']['moduleCounters'][m][k]['missed']for k in COUNTERS))
 xml=out/(m+'.xml');r=subprocess.run([str(j/'java'),'-cp',cp,'NativeCoverageXml471',str(jars[m]),str(xml),*[str(p)for p in host+streams]],capture_output=True,timeout=45)
 (out/(m+'-xml.private.log')).write_bytes(r.stdout+r.stderr);require(r.returncode==0 and not r.stderr and b'classMismatch0=true'in r.stdout);xml_hashes[m]=sha(xml);gaps[m]=coordinates(xml.read_bytes(),v)
result={'actualExit':0,'productionSource':qualification['source'],'distinctQualifiedSessions':16,'sameSessionPointUnion':False,'oldSourceNativeImported':False,'newVmOperations0':True,'sourceChanged0':True,'classByteMismatch':0,'moduleCounters':counters,'gaps':gaps,'xmlHashes':xml_hashes,'cohortManifestHashes':dict(COHORTS),'coverage100':all(counters[m][k]['missed']==0 for m in modules for k in COUNTERS),'formalAccepted':False,'startedUTC':started.isoformat(),'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'manifestSha256':sha(out/'manifest.safe.json'),'remaining':{k:sum(v[k]['missed']for v in counters.values())for k in COUNTERS},'distinctSessions':16,'sameSessionPointUnion':False,'coverage100':result['coverage100'],'formalAccepted':False}))
'''

def main():
    import subprocess
    if subprocess.check_output(['git','status','--porcelain'])or subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml']):raise ValueError('clean same Production source required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);records=[json.loads((W/local/'manifest.safe.json').read_bytes())for local,_ in COHORTS]
    qualify_inputs(records)
    code='COHORTS='+repr([(remote,r['manifestSha256'])for (_,remote),r in zip(COHORTS,records)])+'\nSOURCE='+repr(SOURCE)+'\n'+inspect.getsource(qualify_inputs)+'\n'+inspect.getsource(coordinates)+'\n'+SERVER
    from pyflakes.api import check
    if check(code,'<actual distinct-session native campaign>'):raise ValueError('actual complete generated static gate refused')
    script=out/'pg1624-native-campaign.private.py';script.write_text(code)
    exit_code,output=run('test ! -e /home/mini/schubert-nk-pgpt/transfer/pg1624-native-campaign.private.py && test ! -e /home/mini/schubert-nk-pgpt/runs/PG1624-native-campaign-v1',timeout=30)
    if exit_code:raise ValueError('new-only native campaign namespace required')
    exit_code,output=copy(script,'/home/mini/schubert-nk-pgpt/transfer/',timeout=60)
    (out/'transfer.private.log').write_text(output)
    if exit_code:raise ValueError('fixed campaign source transfer failed')
    # Transfer name is unique across this campaign; preserve previous artifacts.
    exit_code,output=run('python3 -B /home/mini/schubert-nk-pgpt/transfer/pg1624-native-campaign.private.py',timeout=180)
    (out/'server.private.log').write_text(output)
    safe={'actualExit':exit_code,'scriptSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if exit_code==0:safe.update(json.loads(next(v for v in output.splitlines()if v.startswith('{'))))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return exit_code

if __name__=='__main__':raise SystemExit(main())
