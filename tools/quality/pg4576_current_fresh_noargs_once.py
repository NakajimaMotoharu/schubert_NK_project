"""Distinct published964e ordinary Root once, fresh INVALID/no permit; preserve old143."""
import hashlib
import inspect
import json
import os
import subprocess
from pathlib import Path
from pyflakes.api import check
import pg4016_literal_invariant_current_noargs_once as old
import pg4546_failed_current_publication_post as post
import pg4560_current_same_peer_observer as observer
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg2814_network_newboot_readonly import one
from pg4434_current_candidate_admission_read import authenticate_host
from pg4188_exact_partial_recover import process

SLOT='pg4576-current-fresh-noargs-once-v1'
SOURCE,BOM=observer.SOURCE,observer.BOM
QUALIFICATION='pg4580-current-fresh-qualification-v1'


def action():
    raw=observer.bind(old.body()).replace(old.SLOT,SLOT).replace('pg4012','pg4560')
    raw=one(raw,'require(len(records)==46)','require(len(records)==58)')
    raw=one(raw,'native==snapshot()',"native==snapshot()['native']")
    raw=raw.replace('oldCompletedRunNotResumed','oldRunNotResumed').replace('previousCompletion','previousFailedRootData')
    raw=one(raw,"'manifestSha256':hashlib.sha256(manifest).hexdigest()","'manifestSha256':sha")
    raw=one(raw,"persist('external-start-guard.private.json',","require(manifest.read_bytes()==raw and hashlib.sha256(raw).hexdigest()==sha)\npersist('external-start-guard.private.json',")
    raw=one(raw,"r=subprocess.run(['/usr/bin/systemctl','start'", "require(strict_equal(snapshot(),before_current)and strict_equal(config(),before_configuration))\nr=subprocess.run(['/usr/bin/systemctl','start'")
    return one(raw,'print(json.dumps(current))\nraise SystemExit(r.returncode)','')


PRELUDE=r'''
before_current=snapshot();before_configuration=config()
require(not before_current['actors']and not before_current['flocks']and not before_current['database']['peers']and not before_current['database']['locks'])
require(all(v['MainPID']==v['ControlPID']=='0'and not v['Job']for v in before_current['units'].values()))
require(strict_equal(before_current,json.loads((save/'second-raw8.private.json').read_bytes()))and strict_equal(before_configuration,json.loads((save/'second-config.private.json').read_bytes())))
epoch=Path('/run/schubert-nk/startup/epoch.current').read_bytes();oracle['canonical_epoch'](epoch);require(epoch==expected_epoch)
epoch_id=epoch.decode('ascii').splitlines()[3].split('=',1)[1]
require(not os.path.lexists(Path('/run/schubert-nk/startup')/(epoch_id+'.permit')))
summary={'parentInvocation':'bbcdb69957764d489a9c757b441542fd','parentExit':143,'parentNormal':False,'doneFileDataOnly':True,'previousRun':'b1ba37cb-9b2b-469b-a5f2-b0e6d8c97cd1','previousActivation':'8314450e-0dd5-4986-875c-81f73e1b50b2'}
after={**before_current,'configuration':before_configuration};native=before_current['native']
'''


def payload(hashes):
    raw=post.payload().replace(post.SLOT,SLOT+'-prestart')
    marker='finally:\n for unit in reversed(refs):'
    block=PRELUDE+action()
    raw=one(raw,marker,''.join(' '+line+'\n'for line in block.splitlines())+marker)
    end="value={'actualExit':0,'observedUTC':"
    if raw.count(end)!=1:raise ValueError('one post output boundary')
    raw=raw[:raw.index(end)]+"current.update(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),tenMetadataRefsNormalClose=True)\nprint(json.dumps(current))\nraise SystemExit(r.returncode)\n"
    raw='WATCH_FILES='+repr(hashes)+'\n'+raw
    if check(raw,'<published964e full admission one ordinary start>'):raise ValueError('all emitted static0')
    compile(raw,'<new current ordinary Root once>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator first')
    if subprocess.check_output(['git','diff','--name-only',SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('same qualified3721 source first')
    subprocess.run(['git','merge-base','--is-ancestor','b65d1283e9dc384f761899bc8448cd50b9f572fc','origin/main'],check=True)
    docs=['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']
    if subprocess.check_output(['git','diff','--ignore-blank-lines','origin/main','HEAD','--',*docs]):raise ValueError('same finalized published design first')
    proof=json.loads((W/'pg4574-capacity-current-after-v1/manifest.safe.json').read_bytes())
    if proof['actualExit']!=0 or proof['productionSource']!=SOURCE or proof['result']['newSourceParentNotStarted']is not True or proof['result']['guestFreeBytes']<12884901888:raise ValueError('actual full independent same-source capacity post0 first')
    if not(W/'pg4560-watch-v1.started').exists()or(W/'pg4560-watch-v1.exit').exists():raise ValueError('new live observer first')
    frames=[json.loads(line)for line in(W/'pg4560-parent-watch-v1.private.jsonl').read_bytes().splitlines()]
    states=[v['states']for v in frames if 'states'in v]
    if not states or any(v['MainPID']!='0'or v['ControlPID']!='0'or v['Job']for v in states[-1].values()):raise ValueError('new quiescent independent frame first')
    hashes={name:hashlib.sha256(raw.encode()).hexdigest()for name,raw in observer.files().items()}
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(P/'pg4560-observer-stage-v1').iterdir()}!=hashes:raise ValueError('frozen complete four observer files')
    raw=payload(hashes);qualification=json.loads((W/QUALIFICATION/'manifest.safe.json').read_bytes())
    if qualification['actualExit']!=0 or qualification['source']!=SOURCE or qualification['files']!=hashes or qualification['freshOnceSha256']!=hashlib.sha256(raw.encode()).hexdigest():raise ValueError('exact qualified whole payload first')
    for name,digest in qualification['hostSourceHashes'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:raise ValueError('qualified host bytes unchanged')
    authenticate_host();os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        with(out/'stdout.private.log').open('xb')as output,(out/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-','proof'],stdin=subprocess.PIPE,stdout=output,stderr=error)
            (out/'start.safe.json').write_text(json.dumps({'owner':process(os.getpid()),'ssh':process(child.pid),'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'source':SOURCE,'replayAllowed':False}))
            child.stdin.write(raw.encode());child.stdin.close();code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'source':SOURCE,'BOM':BOM,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'clientSuccessIsNotParentSuccess':True,'oldRoot143Normal':False,'formalAccepted':False}
    if code==0:value['result']=json.loads((out/'stdout.private.log').read_bytes())
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
