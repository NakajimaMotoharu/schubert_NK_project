"""SSC288 fixed pair cleanup -> partial inspect -> five new stops -> independent post.

No entry is authorized until published SSC288 and actual proof are checked. Original4152's
same-host gate is queued, never unlinked or forced. Keeper metadata Ref survives the handoff.
"""
import hashlib
import json
import os
from pathlib import Path
import select
import shlex
import subprocess
import sys
from lan_server import run
import pg3428_vm_candidate_preflight_readonly as identity
from pg1446_current_cold_stage import W,P,SSH
from pg1724_retained_host_gate import queued_gate
from pg4176_partial_coordinator import owner,files
from pg4182_bounded_pool_coordinator import SLOT as TOOLS,GUEST

OUT=W/'pg4188-exact-partial-recover-v1'
DESIGN_MAIN='9d300bd12881a2fae3a1b42654c10cc9eb105e47'


def private(name,value):
    with(OUT/name).open('xb')as f:
        f.write(json.dumps(value,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
    fd=os.open(OUT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)


def process(pid):
    p=Path('/proc')/str(pid)
    return {'pid':pid,'ticks':int((p/'stat').read_text().rsplit(')',1)[1].split()[19]),'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()}


def bootstrap(name,hashes):
    if name not in {'keeper.py','partial.py','post.py'}:raise ValueError('fixed staged script only')
    return 'ROOT='+repr(GUEST)+'\nEXPECTED='+repr(hashes)+'\nNAME='+repr(name)+'\n'+r'''
import pathlib,hashlib,os,stat
root=pathlib.Path(ROOT);assert set(p.name for p in root.iterdir())==set(EXPECTED)
for name,digest in EXPECTED.items():
 p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and not os.listxattr(p)
 raw=p.read_bytes();after=p.lstat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)and hashlib.sha256(raw).hexdigest()==digest
p=root/NAME;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED[NAME]
exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
'''


def remote_args(name,hashes,mode=None):
    if (name,mode)not in {('keeper.py','recover'),('partial.py','inspect'),('partial.py','recover'),('post.py',None)}:
        raise ValueError('fixed staged phase only')
    # SSH joins remote arguments through the remote shell. Quote the complete -c
    # program as one argument; do not send it through the keeper ACK channel.
    args=['sudo','-n','python3','-B','-c',bootstrap(name,hashes)]+([mode]if mode else[])
    return SSH+[shlex.join(args)]


def original_receipt(receipt):
    if type(receipt)is not dict or type(receipt.get('actualExit'))is not int or receipt['actualExit']!=143 or receipt.get('oldParentNormal')is not False:
        raise ValueError('original failure receipt actual143 required')
    if receipt.get('source')!='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e' or receipt.get('payloadSha256')!='5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3' or receipt.get('formalAccepted')is not False:
        raise ValueError('fixed original source and failed artifact required')
    return receipt


def main():
    if sys.argv[1:]!=['recover']:raise SystemExit('recover once, no automatic retry')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('fixed clean operator required')
    subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
    for doc in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md',
                'documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
        if subprocess.check_output(['git','show','origin/main:'+doc])!=subprocess.check_output(['git','show',DESIGN_MAIN+':'+doc]):
            raise ValueError('finalized recovery design changed; review first')
    actual=json.loads((W/(TOOLS+'-proof')/'manifest.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['result']['signalsIssued']!=0:raise ValueError('actual current full pair proof first')
    staged=json.loads((W/(TOOLS+'-stage')/'manifest.safe.json').read_bytes())
    hashes={name:hashlib.sha256(text.encode()).hexdigest()for name,text in files().items()}
    if staged['actualExit']!=0 or hashes!=staged['result']['files']:raise ValueError('all final staged source unchanged')
    forward=process(20445)
    if forward!={'pid':20445,'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:
        raise ValueError('current pinned forward ownership required')
    code,text=run(identity.HOST,timeout=30)
    if code!=0:raise ValueError('host VM ownership refused')
    host=json.loads(text.strip())
    if host['boot']!='c7964823-c628-4ef2-99b5-07b0f0b62bba':raise ValueError('host boot changed')
    os.umask(0o077);OUT.mkdir(mode=0o700)
    private('start.safe.json',{'owner':process(os.getpid()),'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e','files':hashes,'oldRun':'PG4152','replayAllowed':False,'host':host,'forward':forward,'designMain':DESIGN_MAIN})
    with queued_gate(P/'current-management-critical.lock',validate_owner=owner)as acquired:
        error=(OUT/'keeper-stderr.private.log').open('xb')
        keeper=subprocess.Popen(remote_args('keeper.py',hashes,'recover'),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=error,text=True,bufsize=1)
        private('keeper-ssh.private.json',process(keeper.pid))
        def frame(prefix):
            poll=select.poll();poll.register(keeper.stdout.fileno(),select.POLLIN)
            if not poll.poll(240000):raise ValueError('original keeper result missing; do not retry')
            line=keeper.stdout.readline(1001)
            if not line.endswith('\n')or not line.startswith(prefix):raise ValueError('fixed keeper phase required; preserve original')
            with(OUT/'keeper-stages.safe.log').open('a')as f:f.write(line);f.flush();os.fsync(f.fileno())
            return line
        def ack():keeper.stdin.write('CONTINUE\n');keeper.stdin.flush()
        frame('SSC288_PAIR_READY ');owner(P/'current-management-critical.lock');ack()
        frame('SSC288_OLD_PAIR_GONE metadataRefsHeld=true')
        if not acquired.wait(30):raise ValueError('original gate natural release required')
        receipt=original_receipt(json.loads((W/'pg4152-exact-failed-done-recover-v1/manifest.safe.json').read_bytes()))
        private('old-original-result.safe.json',receipt);ack();frame('SSC288_METADATA_HELD postRequired=true')
        def job(name,mode,label):
            with(OUT/(label+'.stdout.private.log')).open('xb')as output,(OUT/(label+'.stderr.private.log')).open('xb')as err:
                args=remote_args(name,hashes,mode)
                child=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=output,stderr=err)
                private(label+'.process.private.json',process(child.pid));code=child.wait();output.flush();err.flush();os.fsync(output.fileno());os.fsync(err.fileno())
            content=(OUT/(label+'.stdout.private.log')).read_bytes()
            private(label+'.exit.safe.json',{'actualExit':code,'stdoutSha256':hashlib.sha256(content).hexdigest()})
            if code!=0:raise ValueError('original staged job did not succeed; never reissue automatically')
            value=json.loads(content.splitlines()[-1])
            if value['actualExit']!=0 or value['source']!='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e':raise ValueError('same-source original terminal required')
            return value
        inspect_result=job('partial.py','inspect','partial-inspect')
        if inspect_result['newScopeNormalClose']is not True:raise ValueError('same final partial read acceptance required')
        recover_result=job('partial.py','recover','partial-recover')
        if recover_result['newStopCount']!=5 or recover_result['caddyPriorStopAuthenticated']is not True or recover_result['old4152Normal']is not False or recover_result['recoverySixNormal']is not True:raise ValueError('five new stops and prior Caddy proof required')
        post_result=job('post.py',None,'independent-post')
        if post_result['newMARDDBTenRefNormalClose']is not True or post_result['independentFailedDoneRecoveryPost']is not True:raise ValueError('fresh all-resource independent post required')
        ack();tail=keeper.communicate(timeout=30)[0];error.close()
        if keeper.returncode!=0:raise ValueError('keeper refs must close normally')
        keeper_result=json.loads(tail.splitlines()[-1])
        if keeper_result['newTenRefsNormalClose']is not True:raise ValueError('new metadata keeper normal close required')
        value={'actualExit':0,'source':recover_result['source'],'old4152Exit':143,'old4152Normal':False,'oldParentRoot143Normal':False,
               'oldPairOwnedTermSignals':2,'newBusinessStops':5,'caddyStopsReissued':0,'partialInspect':inspect_result,'partialRecover':recover_result,
               'independentPost':post_result,'keeper':keeper_result,'formalAccepted':False}
        private('manifest.safe.json',value);print(json.dumps(value));return 0


if __name__=='__main__':raise SystemExit(main())
