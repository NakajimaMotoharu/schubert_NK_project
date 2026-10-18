"""Current six-Jar static applicability diagnostic only; never F03/native/formal acceptance."""
import hashlib
import json
import os
import subprocess
from lan_server import run,copy
import pg4976_ssc304_static as previous
from pg5416_ownership_whole_qualification import SOURCE,ROOT,W,SLOT as QUALIFIED

SLOT='pg5424-ownership-static-v1'


def server_source(data):
    raw=previous.server_source(data).replace('source-full-PG4968','source-full-PG5414')
    raw=raw.replace('runs/PG4856-static-completion-v1/manifest.safe.json','runs/PG4976-ssc304-static-v1/manifest.safe.json')
    raw=raw.replace('All six Jars are exact independently qualified PG4968 current3791/1650 ABI; every fixed third-party auxiliary retained; no F03/native/formal acceptance.',
        'All six Jars match independently qualified PG5414 current3896/1664 ABI; every fixed third-party auxiliary retained; no F03/native/formal acceptance.')
    raw=raw.replace('PG4970 qualifies original PG4968 full3791/553/1650; one JDBC Main and three internal declarations; old04bb native not imported; six-format-first independently verified.',
        'PG5416 original PG5414 all3896/562/1664 after factory ownership manufacture; exact82 new methods; selected1164/137 and readonly TWR/preowner qualification; no old native or counters imported.')
    raw=raw.replace('All six project auxiliaries are exact PG4420 independently qualified current Jars; every pinned third-party auxiliary unchanged. No old ABI equivalence assumption. Not F03/native/coverage acceptance.',
        'All six auxiliaries match PG5416-qualified current PG5414 Jars; every pinned third-party byte retained; no F03/native/formal acceptance.')
    raw=raw.replace('PG4696 original PG4694 full XML, all3739 identities,1646 Main and all849 source; SSC299 exact six modified/two internal interfaces; old964e native not imported; BUG1381 format-order gap remains separate.',
        'PG5416 current source296 all3896/562/1664, all849 current Java source inputs and original whole XML; native/global100/F03 remain separate and unaccepted.')
    raw=raw.replace('actualRuleCountDeltaFromOld04bb','actualRuleCountDeltaFromSourceA2ecc')
    return raw


def main():
    from pyflakes.api import check
    if subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT):
        raise ValueError('current same fixed source/settings required')
    qualified=json.loads((W/QUALIFIED/'manifest.safe.json').read_bytes())
    if qualified['actualExit']!=0 or qualified['result']['productionSource']!=SOURCE or qualified['result']['tests']!=3896 or qualified['result']['mainClasses']!=1664 or qualified['result']['allSixFormatBeforeAnyPt'] is not True:
        raise ValueError('current independently qualified original whole first')
    readonly=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5418-readonly-ownership-bytecode-v1/manifest.json'
    review=json.loads(readonly.read_bytes())
    if review['actualExit']!=0 or review['source']!=SOURCE or review['readonlyCandidateCount']!=4:
        raise ValueError('all four actual readonly/preowner contracts first')
    prior=json.loads((W/'pg4976-ssc304-static-v1/manifest.safe.json').read_bytes())
    if prior['actualExit']!=0:raise ValueError('prior diagnostic is only immutable comparison, never new qualification')
    data={'source':SOURCE,'head':SOURCE,'candidateJob':'PG5424-ownership-static-input-v1',
        'staticJob':'PG5424-ownership-static-v1','includeCheckstyle':False,'qualifiedJars':qualified['result']['jarHashes'],
        'originalStaticManifestSha256':hashlib.sha256((W/'pg3422-candidate-static-v1/manifest.safe.json').read_bytes()).hexdigest(),
        'priorStaticManifestSha256':prior['result']['serverManifestSha256'],
        'sourceSha256':{path.relative_to(ROOT).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in ROOT.glob('src/*/src/main/java/**/*.java')}}
    raw=server_source(data)
    if check(raw,'<current allsix actual static applicability>'):raise ValueError('complete standalone static0 before any output')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);script=out/'static.private.py'
    with script.open('x') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    digest=hashlib.sha256(raw.encode()).hexdigest();remote='/home/mini/schubert-nk-pgpt/transfer/PG5424-ownership-static-v1'
    code,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG5424-ownership-static-v1 && test ! -e /home/mini/schubert-nk-pgpt/runs/PG5424-ownership-static-input-v1 && mkdir -m700 '+remote,timeout=30)
    if code:raise ValueError('new-only diagnostic namespace; inspect original if already issued')
    code,_=copy(script,remote+'/',timeout=60)
    if code:raise ValueError('fixed static payload transfer')
    code,text=run('sha256sum '+remote+'/static.private.py',timeout=30)
    if code or text.split()[0]!=digest:raise ValueError('exact payload bytes')
    code,text=run('python3 -B '+remote+'/static.private.py',timeout=360)
    with(out/'observer.private.log').open('x') as stream:stream.write(text);stream.flush();os.fsync(stream.fileno())
    value={'actualExit':code,'productionSource':SOURCE,'payloadSha256':digest,'formalAccepted':False,'vmActions':0,
        'wholeTestsReplayed':0,'readonlyProofSha256':hashlib.sha256(readonly.read_bytes()).hexdigest()}
    if code==0:value['result']=json.loads(next(line for line in reversed(text.splitlines()) if line.startswith('{')))
    with(out/'manifest.safe.json').open('x') as stream:json.dump(value,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({key:value[key] for key in value if key!='result'}))
    if code==0:print(json.dumps({key:value['result'][key] for key in ('pmd','checkstyle','F03Accepted','sameCurrentSixJarAbi','serverManifestSha256')}))
    return code


if __name__=='__main__':raise SystemExit(main())
