"""Technical same-Main two-path measurement, latest Inspector closing only, NOT formal collector."""
import datetime
import hashlib
import inspect
import json
import os
import shutil
import subprocess
import tarfile
from pg1446_current_cold_stage import W
from pg2104_current_newrun_native_qualified_v2 import server as single_server
from pg2044_fresh_normal_warning_native_qualification import qualify_snapshot,SOURCE
from pg1271_current_native_gap import coordinates
from lan_server import run,copy

SLOT='pg2106-same-source-two-path-native-union-v1'


def select(inputs):
    if len(inputs)!=2 or any(v['productionSource']!=SOURCE for v in inputs)or inputs[0]['qualifiedFull']!=inputs[1]['qualifiedFull']or inputs[0]['libraries']!=inputs[1]['libraries']:raise ValueError('same qualified Main/full/libraries required')
    selected=[]
    for campaign,value in enumerate(inputs):
        if len(value['selected'])!=10:raise ValueError('each qualified ten-point path required')
        inspector=[v for v in value['selected']if v['unit']=='schubert-nk-inbox-inspector.service']
        if len(inspector)!=2 or not inspector[0]['relative'].endswith('.closing.exec')or not inspector[1]['relative'].endswith('.terminal.exec'):raise ValueError('paired independently qualified Inspector points required')
        for index,point in enumerate(value['selected']):
            if point is inspector[1]:continue
            selected.append((campaign,index,{**point,'relative':str(campaign)+'/'+point['relative']}))
    if len(selected)!=18 or len({v['relative']for _,_,v in selected})!=18:raise ValueError('eighteen unique latest/independent points required')
    return selected


def server():
    raw=single_server().replace('PG2104','PG2106').replace("len(v['selected'])==10","len(v['selected'])==18").replace("'currentNativeStreams':10","'currentNativeStreams':18")
    begin=raw.index('inspector=[(point,session)');end=raw.index("modules=['protocol'",begin)
    raw=raw[:begin]+"""inspector=[(point,session)for point,session in zip(v['selected'],sessions,strict=True)if point['unit']=='schubert-nk-inbox-inspector.service']
require(len(inspector)==2 and all(point['relative'].endswith('.closing.exec')for point,session in inspector))
require(len({session['sessionIdSha256']for point,session in inspector})==2)
require(len({session['sessionIdSha256']for session in sessions})==18)
"""+raw[end:]
    raw=raw.replace("'inspectorTwoPointsSameSessionAndOrdered':True","'inspectorLatestClosingOnlyPerProcess':True,'sameSourceTwoPathTechnicalUnion':True,'formalCollectorAccepted':False")
    compile(raw,'<same Main two-path technical measurement>','exec');return raw


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o077);qualify_snapshot()
    paths=[W/'pg2048-receipt-preserving-native-qualified-v1',W/'pg2104-current-newrun-native-qualified-v1'];parents=[json.loads((p/'manifest.safe.json').read_bytes())for p in paths]
    if any(v['actualExit']!=0 or v['productionSource']!=SOURCE or v['result']['classByteMismatch']!=0 or v['result']['inspectorTwoPointsSameSessionAndOrdered']is not True for v in parents):raise ValueError('two independent qualified sameSource ten-point parents required')
    inputs=[json.loads((p/'input.safe.json').read_bytes())for p in paths];selection=select(inputs)
    out=W/SLOT;out.mkdir(mode=0o700);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for n,(campaign,index,point)in enumerate(selection):
        p=paths[campaign]/(str(index)+'.exec')
        if sha(p)!=point['sha256']or p.stat().st_size!=point['bytes']:raise ValueError('qualified native bytes must not change')
        shutil.copyfile(p,out/(str(n)+'.exec'));(out/(str(n)+'.exec')).chmod(0o600)
    for name in ['NativeCoverage.java','NativeSessions571.java','NativeSessions571Test.java','NativeCoverageXml471.java']:
        if sha(paths[0]/name)!=sha(paths[1]/name):raise ValueError('same qualified helper source required')
        shutil.copyfile(paths[1]/name,out/name)
    data={**inputs[1],'selected':[v for _,_,v in selection],'excludedHistorical':[],'qualifiedParentManifests':[sha(p/'manifest.safe.json')for p in paths],'latestInspectorClosingOnly':True,'formalAccepted':False}
    data['files']={p.name:sha(p)for p in out.iterdir()if p.is_file()};(out/'input.safe.json').write_text(json.dumps(data,sort_keys=True))
    archive=out/'input.private.tar'
    with tarfile.open(archive,'x:')as tar:
        for p in out.iterdir():
            if p!=archive:tar.add(p,arcname=p.name,recursive=False)
    code,status=run("python3 -c \"import os,json;v=os.statvfs('/home/mini/schubert-nk-pgpt');print(json.dumps({'availableBytes':v.f_bavail*v.f_frsize}))\"",timeout=30)
    if code or json.loads(next(l for l in status.splitlines()if l.strip().startswith('{')))['availableBytes']<10737418240+archive.stat().st_size:raise ValueError('server analysis preservation capacity required')
    code,status=copy(str(archive),'/home/mini/schubert-nk-pgpt/transfer/PG2106-native-input.tar',timeout=120);(out/'transfer.private.log').write_text(status)
    if code:raise ValueError('private technical native transfer required')
    raw='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA='+repr(sha(archive))+'\n'+inspect.getsource(coordinates)+'\n'+server()
    from pyflakes.api import check
    if check(raw,'<actual eighteen independent point measurement>'):raise ValueError('all actual server exports required')
    (out/'server-payload.private.py').write_text(raw)
    code,status=run("python3 - <<'PG2106'\n"+raw+'\nPG2106',timeout=240);(out/'observer.private.log').write_text(status)
    value={'actualExit':code,'productionSource':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'noNewVmActions':True,'sameSourceTechnicalOnly':True}
    if not code:value.update(json.loads(next(l for l in status.splitlines()if l.strip().startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True))
    if code==0:
        r=value['result'];remaining={k:sum(v[k]['missed']for v in r['moduleCounters'].values())for k in ['LINE','METHOD','CLASS','BRANCH']};print(json.dumps({'actualExit':0,'remaining':remaining,'classByteMismatch':r['classByteMismatch'],'coverage100':r['coverage100'],'manifestSha256':value['manifestSha256'],'formalAccepted':False}))
    else:print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    return code


if __name__=='__main__':raise SystemExit(main())
