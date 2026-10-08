"""Offline union of two independently qualified current-source cohorts only."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE='36fe7a0b938489d61d17d49c1c30a6fbbef699d5'
MODULES={'protocol','storage','bootstrap','api','web','batch'}


def admissible(a,b):
    for v in (a,b):
        if (type(v)is not dict or type(v.get('actualExit'))is not int or v.get('actualExit')!=0 or v.get('productionSource')!=SOURCE
                or v.get('currentNativeStreams')!=8 or len(v.get('selected',[]))!=8 or len(v.get('singleSessions',[]))!=8
                or any(s.get('sessions')!=1 for s in v['singleSessions'])
                or v.get('frozenHostManifestSha256')!='067b8a155fe5a137aebb9c732bf800122752cb173ca8a09f3c41087d9efc178b'
                or set(v.get('moduleCounters',{}))!=MODULES or set(v.get('hostExecHashes',{}))!=MODULES
                or any(m.get('classByteMismatch')!=0 for m in v.get('moduleCounters',{}).values())):
            raise ValueError('qualified same-source native cohort required')
    if a['run']==b['run']or a['hostExecHashes']!=b['hostExecHashes']:
        raise ValueError('distinct qualification and identical frozen host required')
    sessions=[s['sessionIdSha256']for v in (a,b)for s in v['singleSessions']]
    if len(set(sessions))!=16:raise ValueError('distinct sixteen qualified sessions required')
    return True


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    os.umask(0o077)
    first=W/'pg644-current-eight-native-v1';second=W/'pg657-normal-eight-native-v1'
    a=json.loads((first/'manifest.safe.json').read_bytes());b=json.loads((second/'manifest.safe.json').read_bytes());admissible(a,b)
    assert sha(first/'manifest.safe.json')=='3200b4a2e5b5bd63a5854dbb541c22ca66cdb14bc98fde75173797a96bb68aa0'
    host=W/'pg630-retention-factory-six-host-v1';h=json.loads((host/'manifest.safe.json').read_bytes())
    assert sha(host/'manifest.safe.json')==a['frozenHostManifestSha256']and h['candidateSource']==SOURCE and h['actualExit']==0
    target=W/'pg658-same-source-sixteen-native-v1';target.mkdir(mode=0o700)
    streams=[]
    for directory,record in ((first,a),(second,b)):
        for i,v in enumerate(record['selected']):
            p=directory/(str(i)+'.exec');assert p.stat().st_size==v['bytes']and sha(p)==v['sha256'];streams.append(p)
    modules=('protocol','storage','bootstrap','api','web','batch')
    executions=[host/m/'jacoco.exec'for m in modules]
    for m,p in zip(modules,executions):assert sha(p)==a['hostExecHashes'][m]==h['moduleResults'][m]['execSha256']
    helper=W/'pg571-current-ten-native-v2/classes';assert sha(helper/'NativeCoverage.class')=='37227f2f494bf2cc8e36eb52ba47c65af3e79ccaeb0c3efcb1fdf9f5d3e0af5a'
    repo=Path('/home/mini/codex/project1/work/toolchain/m2/repository');cp=[str(helper)]
    for pattern in ('org/jacoco/org.jacoco.core/0.8.15/*.jar','org/ow2/asm/asm/9.10.1/*.jar','org/ow2/asm/asm-tree/9.10.1/*.jar','org/ow2/asm/asm-commons/9.10.1/*.jar'):
        matches=list(repo.glob(pattern));assert len(matches)==1;cp.append(str(matches[0]))
    counters={};gain={}
    for m in modules:
        jar=host/m/('schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar');assert sha(jar)==h['moduleResults'][m]['jarSha256']
        result=subprocess.run(['/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java','-cp',':'.join(cp),'NativeCoverage',str(jar),*[str(p)for p in executions+streams]],capture_output=True,timeout=45)
        with(target/(m+'.private.log')).open('xb')as f:f.write(result.stdout+result.stderr)
        assert result.returncode==0 and not result.stderr
        v=json.loads(result.stdout);assert v['classByteMismatch']==0 and v['formal']is False;counters[m]=v
        gain[m]={k:a['moduleCounters'][m][k]['missed']-v[k]['missed']for k in ('LINE','METHOD','CLASS','BRANCH')};assert all(x>=0 for x in gain[m].values())
    record={'run':'PG658-same-source-sixteen-native-v1','actualExit':0,'source':SOURCE,'atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qualificationManifests':{d.name:sha(d/'manifest.safe.json')for d in (first,second)},'qualifiedCohorts':2,'qualifiedSingleSessions':16,'otherSourceStreamsImported':False,'moduleCounters':counters,'gainVsPG644':gain,'remaining':{k:sum(v[k]['missed']for v in counters.values())for k in ('LINE','METHOD','CLASS','BRANCH')},'coverage100':all(v[k]['missed']==0 for v in counters.values()for k in ('LINE','METHOD','CLASS','BRANCH')),'formalAccepted':False,'rawExported':False,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    with(target/'manifest.safe.json').open('x')as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps({'actualExit':0,'native16':True,'gainVsPG644':{k:sum(v[k]for v in gain.values())for k in ('LINE','METHOD','CLASS','BRANCH')},'remaining':record['remaining'],'coverage100':record['coverage100'],'formalAccepted':False}))


if __name__=='__main__':main()
