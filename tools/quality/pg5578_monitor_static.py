"""Unused diagnostic rebound to3905/0ea before first issue; frozen rules, never F03 PASS."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from lan_server import run,copy
import pg5556_snapshot_static as previous
from pg5574_monitor_whole_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED

SLOT='pg5578-monitor-static-v1'


def server_source(data):
    raw=previous.server_source(data)
    for before,after in(('source-full-PG5550','source-full-PG5588'),
        ('runs/PG5424-ownership-static-v1/manifest.safe.json','runs/PG5556-snapshot-static-v1/manifest.safe.json'),
        ('current3900/1664','current3905/1664'),('PG5550 Jars','PG5588 Jars'),
        ('PG5552 current sourcea19 all3900/563/1664','PG5574 current source0ea all3905/563/1664'),
        ('PG5552 original PG5550 all3900/563/1664; exact four new scratch fault methods, one Main codec changed,1663 unchanged; no old native or counters imported.',
         'PG5574 original PG5588 all3905/563/1664; five new monitor/canary methods, six code and five debug differences/1653 identical; no old native or counters imported.'),
        ('actualRuleCountDeltaFromSourceA2ecc','actualRuleCountDeltaFromSourceA19')):
        if before not in raw:raise ValueError('exact previous diagnostic source/description/namespace')
        raw=raw.replace(before,after)
    return raw


def main():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT):raise ValueError('current canonical source first')
    raw=(W/QUALIFIED/'manifest.safe.json').read_bytes();qualified=json.loads(raw);q=qualified['result']
    if not(type(qualified['actualExit'])is int and qualified['actualExit']==0 and q['productionSource']==SOURCE
        and(q['tests'],q['suites'],q['mainClasses'])==(3905,563,1664)and q['allSixFormatBeforeAnyPt']is True
        and q['staticSixModules']==q['FESFlakyNotRun']==0 and len(q['changedClasses'])==11):raise ValueError('actual independently qualified current3905/all11 raw differences first')
    previous_raw=(W/previous.SLOT/'manifest.safe.json').read_bytes();prior=json.loads(previous_raw)
    if prior['actualExit']!=0 or prior['productionSource']!='a19a9f7d940b4f9fba47e51bd9be675f4420401b':raise ValueError('actual a19 diagnostic comparison, not imported acceptance')
    data={'source':SOURCE,'head':SOURCE,'candidateJob':'PG5578-monitor-static-input-v1','staticJob':'PG5578-monitor-static-v1','includeCheckstyle':False,
        'qualifiedJars':q['jarHashes'],'originalStaticManifestSha256':hashlib.sha256((W/'pg3422-candidate-static-v1/manifest.safe.json').read_bytes()).hexdigest(),
        'priorStaticManifestSha256':prior['result']['serverManifestSha256'],
        'sourceSha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    script=server_source(data)
    if check(script,'<current3905 static standalone>'):raise ValueError('complete diagnostic payload namespace')
    compile(script,'<current3905 static standalone>','exec')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'static.private.py'
    with path.open('x')as f:f.write(script);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(script.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5578-monitor-static-v1'
    code,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG5578-monitor-static-v1 && test ! -e /home/mini/schubert-nk-pgpt/runs/PG5578-monitor-static-input-v1 && mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only diagnostic, recover original on collision')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed current input transfer')
    code,text=run('sha256sum '+remote+'/static.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('actual static payload bytes')
    code,text=run('python3 -B '+remote+'/static.private.py',timeout=360)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'productionSource':SOURCE,'payloadSha256':digest,'formalAccepted':False,'vmActions':0,'wholeTestsReplayed':0,'qualifiedWholeSha256':hashlib.sha256(raw).hexdigest()}
    if code==0:value['result']=json.loads(next(line for line in reversed(text.splitlines())if line.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('pmd','checkstyle','F03Accepted','sameCurrentSixJarAbi','serverManifestSha256')}))
    return code


if __name__=='__main__':raise SystemExit(main())
