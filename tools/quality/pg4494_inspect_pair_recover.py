"""SSC297 one-shot owned recovery; preserves original exit/UNKNOWN, no replay."""
import hashlib
import json
import os
from pathlib import Path
import select
import shlex
import subprocess
import sys
from pg1446_current_cold_stage import W,P,SSH
from pg4434_current_candidate_admission_read import authenticate_host
from pg4152_exact_failed_done_recover import process,durable
from pg1724_retained_host_gate import queued_gate
import pg4492_inspect_pair_stage as stage

DESIGN_MAIN='3a7f50158b05227cb274e9c98951181a99c4e557'
OUT=W/'pg4494-inspect-pair-recover-v2'


def original_receipt():
    prefix=W/'pg4462-inspect-v1'
    begin=json.loads(Path(str(prefix)+'.begin.safe.json').read_bytes())
    receipt=json.loads(Path(str(prefix)+'.safe.json').read_bytes())
    code=int(Path(str(prefix)+'.exit').read_text().strip())
    if type(receipt['actualExit'])is not int or receipt['actualExit']!=code or code==0:
        raise ValueError('genuine original non-success transport required, never infer 143')
    if any(receipt[k]!=v for k,v in begin.items()):raise ValueError('exact original reservation required')
    if receipt['candidateSource']!='964e96e45bb588e7e75798b5adf425cbd9985427' or receipt['installedSource']!='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e':raise ValueError('original distinct source attribution')
    if hashlib.sha256(Path(str(prefix)+'.private.log').read_bytes()).hexdigest()!=receipt['privateLogSha256']:raise ValueError('original full log hash required')
    return receipt


def complete(v):
    expected={'actualExit':0,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','BOM':'0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab',
        'boot':'79a3260a-e16d-42bf-942a-b914ed144c28','mode':'recover','oldScopesNormal':False,'newTenRefsNormalClose':True,'unitOperationsIssued':0,
        'candidatePlaced':False,'formalAccepted':False,'allOldProcessesAndResourcesGone':True}
    if type(v)is not dict or any(type(v.get(k))is not type(x)or v[k]!=x for k,x in expected.items()):raise ValueError('complete current recovery receipt required')
    if type(v.get('signalsIssued'))is not int or v['signalsIssued']not in [1,2]:raise ValueError('only owned Java/Python TERM once')
    post=v.get('independentPost')
    post_expected={'actualExit':0,'source':expected['source'],'BOM':expected['BOM'],'newMARDDBTenRefNormalClose':True,'all24OriginalBackupNativeUnitConfigUnchanged':True,
        'oldParentNormal':False,'parent143StillFailed':True,'independentFailedDoneRecoveryPost':True,'signalStartStopReloadDbWrites':0,'formalAccepted':False}
    if type(post)is not dict or any(type(post.get(k))is not type(x)or post[k]!=x for k,x in post_expected.items()):raise ValueError('fresh independent post required')
    return v


def main():
    if sys.argv[1:]!=['recover']or DESIGN_MAIN=='PENDING_SSC297_MAIN':raise ValueError('one recovery after design publication only')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed operator first')
    if subprocess.check_output(['git','diff','--name-only','964e96e45bb588e7e75798b5adf425cbd9985427','HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('candidate and current source unchanged')
    subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
    for name in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
        if subprocess.check_output(['git','show','origin/main:'+name])!=subprocess.check_output(['git','show',DESIGN_MAIN+':'+name]):raise ValueError('exact current published design')
    hashes={name:hashlib.sha256(raw.encode()).hexdigest()for name,raw in stage.files().items()}
    staged=json.loads((W/(stage.SLOT+'-stage')/'manifest.safe.json').read_bytes());proof=json.loads((W/(stage.SLOT+'-proof')/'manifest.safe.json').read_bytes())
    if staged['actualExit']!=0 or staged['result']['files']!=hashes or proof['actualExit']!=0 or proof['result']['signalsIssued']!=0 or proof['result']['newTenRefsNormalClose']is not True:raise ValueError('same fixed artifact proof first')
    authenticate_host();stage.owner(P/'current-management-critical.lock')
    os.umask(0o077);OUT.mkdir(mode=0o700)
    durable(OUT/'start.safe.json',{'owner':process(os.getpid()),'designMain':DESIGN_MAIN,'files':hashes,'replayAllowed':False})
    with queued_gate(P/'current-management-critical.lock',validate_owner=stage.owner)as acquired:
        with(OUT/'stderr.private.log').open('xb')as error:
            # File bytes/envelope are checked in this new SSH before exec. No
            # long raw payload is passed through argv and no file is rewritten.
            bootstrap="""from pathlib import Path
import hashlib,os,stat,sys
p=Path(PATH);s=p.lstat()
assert stat.S_ISREG(s.st_mode)and(s.st_uid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0o400,1)and not os.listxattr(p)
raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==DIGEST
sys.argv=[str(p),'recover'];exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
""".replace('PATH',repr(stage.GUEST+'/keeper.py')).replace('DIGEST',repr(hashes['keeper.py']))
            args=SSH+[shlex.join(['sudo','-n','python3','-B','-c',bootstrap])]
            child=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=error,text=True,bufsize=1)
            durable(OUT/'ssh.private.json',process(child.pid))
            def frame(prefix):
                p=select.poll();p.register(child.stdout.fileno(),select.POLLIN)
                if not p.poll(240000):raise ValueError('original recovery frame unknown; preserve, no replay')
                line=child.stdout.readline(1001)
                if not line.endswith('\n')or not line.startswith(prefix):raise ValueError('unknown phase, keep new metadata held')
                with(OUT/'stages.safe.log').open('a')as log:log.write(line);log.flush();os.fsync(log.fileno())
            def ack():child.stdin.write('CONTINUE\n');child.stdin.flush()
            frame('SSC297_OWNERS_READY ');stage.owner(P/'current-management-critical.lock');ack()
            frame('SSC297_JAVA_GONE originalTransportRequired=true')
            if not acquired.wait(30):raise ValueError('original gate natural release, never force')
            original=original_receipt();durable(OUT/'original-inspect-result.safe.json',original);ack()
            frame('SSC297_PAIR_GONE oldCloseUnknown=true');ack()
            tail=child.communicate()[0];error.flush();os.fsync(error.fileno())
        with(OUT/'tail.private.log').open('x')as log:log.write(tail)
        value={'actualExit':child.returncode,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','originalInspectActualExit':original['actualExit'],'oldScopesNormal':False,'formalAccepted':False}
        if child.returncode==0:value['result']=complete(json.loads(tail.splitlines()[-1]))
        durable(OUT/'manifest.safe.json',value);print(json.dumps(value));return child.returncode


if __name__=='__main__':raise SystemExit(main())
