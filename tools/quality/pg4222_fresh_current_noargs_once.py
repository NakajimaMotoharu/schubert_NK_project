"""SSC290 one distinct ordinary run after actual failed-cohort recovery; no old Root replay."""
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg4060_original_profile_dual_stack import once
import pg4214_quiescent_ten_ref_observation as current
import pg4016_literal_invariant_current_noargs_once as prior
import pg4220_same_peer_current_observer as observer
from pyflakes.api import check
from lan_server import run
import pg3428_vm_candidate_preflight_readonly as identity
from pg4188_exact_partial_recover import process

SLOT='pg4222-fresh-current-noargs-once-v1'
SOURCE,BOM=observer.SOURCE,observer.BOM
DESIGN_MAIN='ff8b4f182b386b7a78e5a0d105b80893fd684bcf'


def action():
    raw=prior.body().replace('pg4012','pg4220').replace(prior.SLOT,SLOT)
    raw=once(raw,'require(len(records)==46)','require(len(records)==52)')
    raw=once(raw,'native==snapshot()','native==snapshot()[\'native\']')
    raw=raw.replace('oldCompletedRunNotResumed','oldRunNotResumed').replace('previousCompletion','previousFailedRootData')
    raw=once(raw,"r=subprocess.run(['/usr/bin/systemctl','start'", "require(snapshot()==before_current and config()==before_configuration)\nr=subprocess.run(['/usr/bin/systemctl','start'")
    return raw.replace('print(json.dumps(current))\nraise SystemExit(r.returncode)','')


def payload(hashes):
    raw=current.payload().replace(current.SLOT,SLOT+'-prestart')
    marker="with metadata_refs(manager,bus,tuple(old['units'])):\n"
    if raw.count(marker)!=1:raise ValueError('fresh original ten-reference scope required')
    prefix=raw[:raw.index(marker)]
    prefix+='\nimport pathlib\nWATCH_FILES='+repr(hashes)+'\n'
    body=BODY+'\n'+action()
    return prefix+marker+''.join(' '+line+'\n'for line in body.splitlines())+"\ncurrent.update(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),tenMetadataRefsNormalClose=True)\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"


BODY=r'''
signed={};exec(SIGNED_SOURCE,signed)
materials=[{'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [pin,signature]]
require(signed['verify'](str(root),data['artifacts'],raw,materials)is True)
reference_raw=Path('/var/lib/pgpt-s1-preservation/pg4214-quiescent-ten-ref-observation-v1/observed.private.json').read_bytes()
require(hashlib.sha256(reference_raw).hexdigest()=='b727f62cebecad38589e235991de47ea99bfc742d9dcb3050232f46451a057c4');reference=json.loads(reference_raw)
before_current=snapshot();before_configuration=config()
require(before_current==reference['current']and before_configuration==reference['configuration'])
require(not before_current['actors']and not before_current['flocks']and not before_current['database']['peers']and not before_current['database']['locks'])
require(all(v['MainPID']==v['ControlPID']=='0'and not v['Job']for v in before_current['units'].values()))
require(all(CONFIG_CONTRACT['same'](old['configuration'][u],v,exec_record)for u,v in before_configuration.items()))
parent=before_current['units']['schubert-nk-morning-controller.service'];require(parent['InvocationID']=='820851b8291a4c958bb34f6c48430ca3'and parent['Result']=='timeout'and parent['ExecMainStatus']=='143')
require(not(Path('/proc/696557').exists())and not Path('/var/lib/schubert-nk/maintenance/active').exists())
require(hashlib.sha256(Path('/var/lib/schubert-nk/maintenance/attempts/d9d58371-bf80-49f6-bad9-3d1e0916fb04.done').read_bytes()).hexdigest()=='ca7829dbf4f1f215bc9bc6c60dd02c94137e2157a665ee57905b3c2aa5f0d090')
epoch=Path('/run/schubert-nk/startup/epoch.current').read_bytes();require(epoch.startswith(b'state=INVALID\n'))
summary={'parentInvocation':'820851b8291a4c958bb34f6c48430ca3','parentExit':143,'parentNormal':False,'doneFileDataOnly':True,'previousRun':'dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f','previousActivation':'d9d58371-bf80-49f6-bad9-3d1e0916fb04'}
after={**before_current,'configuration':before_configuration};native=before_current['native']
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator required')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('same whole3717 source required')
    subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
    for doc in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
        if subprocess.check_output(['git','show','origin/main:'+doc])!=subprocess.check_output(['git','show',DESIGN_MAIN+':'+doc]):raise ValueError('finalized published SSC290 changed; review first')
    recovered=json.loads((W/'pg4200-metadata-continuation-v1-recover/manifest.safe.json').read_bytes())
    if recovered['actualExit']!=0 or recovered['result']['independentPost']['newMARDDBTenRefNormalClose']is not True:raise ValueError('actual failed-cohort recovery/post first')
    if not(W/'pg4220-watch-v1.started').exists()or(W/'pg4220-watch-v1.exit').exists():raise ValueError('new live observer required')
    frames=[json.loads(line)for line in(W/'pg4220-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[v['states']for v in frames if 'states'in v]
    if not states or any(v['MainPID']!='0'or v['ControlPID']!='0'or v['Job']for v in states[-1].values()):raise ValueError('current quiescent independent observer frame first')
    hashes={n:hashlib.sha256(s.encode()).hexdigest()for n,s in observer.namespace()['files']().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg4220-observer-stage-v1').iterdir()}!=hashes:raise ValueError('frozen four observer artifacts unchanged')
    raw=payload(hashes)
    if check(raw,'<complete fresh failed-current admission>'):raise ValueError('all emitted globals static0 first')
    qualification=json.loads((W/'pg4230-final-fresh-observer-qualification-v1/complete.safe.json').read_bytes())
    if qualification['actualExit']!=0 or qualification['source']!=SOURCE or qualification['files']!=hashes or qualification['freshOnceSha256']!=hashlib.sha256(raw.encode()).hexdigest():raise ValueError('exact final source qualification required')
    for path,digest in qualification['hostSourceHashes'].items():
        from pathlib import Path
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise ValueError('all qualified host tools unchanged')
    if process(20445)!={'pid':20445,'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:raise ValueError('current pinned forward required')
    code,text=run(identity.HOST,timeout=30)
    if code!=0 or json.loads(text)['boot']!='c7964823-c628-4ef2-99b5-07b0f0b62bba':raise ValueError('current host VM ownership required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'stdout.private.log').open('xb')as output,(out/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-','proof'],stdin=subprocess.PIPE,stdout=output,stderr=error)
            (out/'start.safe.json').write_text(json.dumps({'owner':process(os.getpid()),'ssh':process(child.pid),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'source':SOURCE,'replayAllowed':False}))
            child.stdin.write(raw.encode());child.stdin.close();code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'source':SOURCE,'BOM':BOM,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'clientSuccessIsNotParentSuccess':True,'oldRoot143Normal':False,'formalAccepted':False}
    if code==0:value['result']=json.loads((out/'stdout.private.log').read_bytes())
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
