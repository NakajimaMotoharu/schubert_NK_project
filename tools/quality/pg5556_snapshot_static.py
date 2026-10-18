"""Exact a19 six-Jar diagnostic; retain every raw warning, no F03 acceptance."""
import hashlib
import json
import os
import subprocess
from pyflakes.api import check
from lan_server import copy,run
import pg5424_ownership_static as previous
from pg5552_snapshot_whole_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED

SLOT='pg5556-snapshot-static-v1'


def server_source(data):
    raw=previous.server_source(data)
    for before,after in(('source-full-PG5414','source-full-PG5550'),
        ('runs/PG4976-ssc304-static-v1/manifest.safe.json','runs/PG5424-ownership-static-v1/manifest.safe.json'),
        ('current3896/1664','current3900/1664'),('PG5414 Jars','PG5550 Jars'),
        ('PG5416 current source296 all3896/562/1664','PG5552 current sourcea19 all3900/563/1664'),
        ('PG5416 original PG5414 all3896/562/1664 after factory ownership manufacture; exact82 new methods; selected1164/137 and readonly TWR/preowner qualification; no old native or counters imported.',
         'PG5552 original PG5550 all3900/563/1664; exact four new scratch fault methods, one Main codec changed,1663 unchanged; no old native or counters imported.')):
        if before not in raw:raise ValueError('exact previous diagnostic binding required: '+before)
        raw=raw.replace(before,after)
    return raw


def main():
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT):raise ValueError('fixed current Main/Test/settings required')
    qualified=json.loads((W/QUALIFIED/'manifest.safe.json').read_bytes());q=qualified['result']
    if not(type(qualified['actualExit'])is int and qualified['actualExit']==0 and q['productionSource']==SOURCE
        and(q['tests'],q['suites'],q['mainClasses'])==(3900,563,1664)and q['allSixFormatBeforeAnyPt']is True
        and q['staticSixModules']==q['FESFlakyNotRun']==0):raise ValueError('genuine same-source independent whole first')
    prior=json.loads((W/previous.SLOT/'manifest.safe.json').read_bytes())
    if prior['actualExit']!=0:raise ValueError('actual previous diagnostic comparison only')
    data={'source':SOURCE,'head':SOURCE,'candidateJob':'PG5556-snapshot-static-input-v1','staticJob':'PG5556-snapshot-static-v1',
        'includeCheckstyle':False,'qualifiedJars':q['jarHashes'],
        'originalStaticManifestSha256':hashlib.sha256((W/'pg3422-candidate-static-v1/manifest.safe.json').read_bytes()).hexdigest(),
        'priorStaticManifestSha256':prior['result']['serverManifestSha256'],
        'sourceSha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw=server_source(data)
    if check(raw,'<actual current3900 static standalone>'):raise ValueError('complete standalone static0')
    compile(raw,'<actual current3900 static standalone>','exec')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'static.private.py'
    with path.open('x')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5556-snapshot-static-v1'
    code,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG5556-snapshot-static-v1 && test ! -e /home/mini/schubert-nk-pgpt/runs/PG5556-snapshot-static-input-v1 && mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only diagnostic; recover original rather than repeat')
    code,_=copy(path,remote+'/',timeout=60)
    if code:raise ValueError('fixed diagnostic transfer')
    code,text=run('sha256sum '+remote+'/static.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('exact payload bytes')
    code,text=run('python3 -B '+remote+'/static.private.py',timeout=360)
    with(out/'observer.private.log').open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
    value={'actualExit':code,'productionSource':SOURCE,'payloadSha256':digest,'formalAccepted':False,'vmActions':0,'wholeTestsReplayed':0}
    if code==0:value['result']=json.loads(next(line for line in reversed(text.splitlines())if line.startswith('{')))
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('pmd','checkstyle','F03Accepted','sameCurrentSixJarAbi','serverManifestSha256')}))
    return code


if __name__=='__main__':raise SystemExit(main())
