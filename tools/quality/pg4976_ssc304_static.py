"""Exact current six-Jar PMD/Checkstyle diagnostic, no private-rename predicate or F03 acceptance."""
import hashlib
import json
import os
import subprocess
from lan_server import copy,run
import pg4850_ssc301_302_static as previous
from pg4968_ssc304_full import SOURCE,ROOT,W

SLOT='pg4976-ssc304-static-v1'


def require(value,why):
    if not value:raise ValueError(why)


def server_source(data):
    require(data['includeCheckstyle']is False,'PMD-only inner phase; outer Checkstyle exactly once, not private-rename proof')
    raw=previous.server_source(data).replace('source-full-PG4844','source-full-PG4968')
    require(raw.count('def server(data):')==1,'one outer current-source diagnostic')
    raw=raw.replace('def server(data):','def server(data):\n    import os',1)
    raw=raw.replace('runs/PG4700-ssc299-static-v1/manifest.safe.json','runs/PG4856-static-completion-v1/manifest.safe.json')
    raw=raw.replace('actualRuleCountDeltaFromOld825e','actualRuleCountDeltaFromOld04bb')
    marker="    root=E.parse(out/'pmd.xml')"
    require(raw.count(marker)==1,'one immediate original PMD result boundary')
    extra="    with(out/'pmd-exit.safe.json').open('x')as f:json.dump({'actualExit':r.returncode,'logSha256':sha(out/'pmd.private.log')},f);f.flush();os.fsync(f.fileno())\n"
    raw=raw.replace(marker,extra+marker,1)
    marker="    errors = E.parse(out / 'checkstyle.xml')"
    require(raw.count(marker)==1,'one immediate outer Checkstyle result boundary')
    extra="    with(out/'checkstyle-exit.safe.json').open('x')as f:json.dump({'actualExit':checked.returncode,'logSha256':sha(out/'checkstyle.private.log')},f);f.flush();os.fsync(f.fileno())\n"
    raw=raw.replace(marker,extra+marker,1)
    raw=raw.replace('All six project Jars are exact independently qualified PG4844 current3761 ABI; every original third-party auxiliary retained. Not F03/native/coverage acceptance.',
        'All six Jars are exact independently qualified PG4968 current3791/1650 ABI; every fixed third-party auxiliary retained; no F03/native/formal acceptance.')
    raw=raw.replace('PG4846 exact original PG4844 full3761/551/all1647; two implementation changes and one data-only declaration addition; old825e native not imported; all-six format order independently verified.',
        'PG4970 qualifies original PG4968 full3791/553/1650; one JDBC Main and three internal declarations; old04bb native not imported; six-format-first independently verified.')
    return raw


def main():
    require(not subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT),'all fixed source/settings unchanged')
    q=json.loads((W/'pg4970-ssc304-whole-qualified-v1/manifest.safe.json').read_bytes())
    require(q['actualExit']==0 and q['result']['productionSource']==SOURCE
            and q['result']['tests']==3791 and q['result']['mainClasses']==1650
            and q['result']['allSixFormatBeforeAnyPt']is True,'actual current independent whole first')
    prior=json.loads((W/'pg4856-static-completion-v1/manifest.safe.json').read_bytes())
    require(prior['actualExit']==0,'actual old diagnostic comparison only')
    data={'source':SOURCE,'head':SOURCE,'candidateJob':'PG4976-ssc304-static-input-v1',
          'staticJob':'PG4976-ssc304-static-v1','includeCheckstyle':False,
          'qualifiedJars':q['result']['jarHashes'],
          'originalStaticManifestSha256':hashlib.sha256((W/'pg3422-candidate-static-v1/manifest.safe.json').read_bytes()).hexdigest(),
          'priorStaticManifestSha256':prior['result']['serverManifestSha256'],
          'sourceSha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw=server_source(data)
    from pyflakes.api import check
    require(check(raw,'<all current static standalone>')==0,'complete standalone static0')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);script=out/'static.private.py';script.write_text(raw)
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG4976-ssc304-static-v1'
    code,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG4976-ssc304-static-v1 && test ! -e /home/mini/schubert-nk-pgpt/runs/PG4976-ssc304-static-input-v1 && mkdir -m700 '+remote,timeout=30)
    require(code==0,'new-only diagnostic; recover original if already exists')
    code,_=copy(script,remote+'/',timeout=60);require(code==0,'fixed input transfer')
    code,text=run('sha256sum '+remote+'/static.private.py',timeout=30);require(code==0 and text.split()[0]==digest,'exact payload bytes')
    code,text=run('python3 -B '+remote+'/static.private.py',timeout=360);(out/'observer.private.log').write_text(text)
    value={'actualExit':code,'productionSource':SOURCE,'payloadSha256':digest,'formalAccepted':False,'vmActions':0}
    if code==0:value['result']=json.loads(next(line for line in reversed(text.splitlines())if line.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if code==0:print(json.dumps({k:value['result'][k]for k in('pmd','checkstyle','F03Accepted','sameCurrentSixJarAbi','serverManifestSha256')}))
    return code


if __name__=='__main__':raise SystemExit(main())
