"""SSC287 exact once-only operational entry. No Root start, reload, backup/admin or force action."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from lan_server import run
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
import pg3428_vm_candidate_preflight_readonly as identity
import pg4104_failed_done_owned_dispatch as candidate
from pg4106_failed_done_owned_inspect_runner import meta
from pg4086_failed_done_recovery_contract import ORDER

ARTIFACT=W/'pg4144-complete-signed-dispatch-qualification-v1-artifact'
QUALIFIED=W/'pg4144-complete-signed-dispatch-qualification-v1-inspect/manifest.safe.json'
OUT=W/'pg4152-exact-failed-done-recover-v1'
SHA='5fdbfff67a9aa71aeab60ae897a4e9a23f3038ae7dc6f86dc5f648c201116fe3'
DESIGN_MAIN='ebde93b8c1b190fe7149d70f2991812a4110c9fd'


def unique(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('duplicate recovery receipt key')
        value[key]=item
    return value


def completed_output(raw):
    if type(raw)is not bytes or not 0<len(raw)<=65536 or not raw.endswith(b'\n')or b'\r'in raw:
        raise ValueError('bounded complete original output required')
    lines=raw.decode('utf-8').splitlines()
    if len(lines)!=7 or lines[:-1]!=['SSC287_STOPPED unit='+u+' generationVerified=true'for u in ORDER]:
        raise ValueError('fixed six original progress rows and terminal receipt required; preserve without replay')
    result=json.loads(lines[-1],object_pairs_hook=unique)
    if type(result)is not dict or type(result.get('actualExit'))is not int or result['actualExit']!=0:
        raise ValueError('actual recovery exit0 required')
    if result.get('source')!='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'or result.get('BOM')!='0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab'or result.get('boot')!='79a3260a-e16d-42bf-942a-b914ed144c28'or result.get('mode')!='recover':
        raise ValueError('fixed source boot BOM and operational mode required')
    if result.get('oldParentNormal')is not False or result.get('formalAccepted')is not False or not all(result.get(k)is True for k in ['oldRoot143StillFailed','recoverySixNormal','canonicalEpochRevoked','newScopeNormalClose','all33StartupEntriesPreserved','independentPostRequired']):
        raise ValueError('actual new normal close without old parent normalization required')
    return result


def durable(path,value):
    raw=json.dumps(value,sort_keys=True).encode()
    with path.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)


def process(pid):
    p=Path('/proc')/str(pid)
    return {'pid':pid,'ticks':int((p/'stat').read_text().rsplit(')',1)[1].split()[19]),
            'argvSha256':hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()}


def main():
    if sys.argv[1:]!=['recover']:raise SystemExit('recover once only; existing OUT prohibits replay')
    os.umask(0o077)
    subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
    for name in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md',
                 'documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
        if subprocess.check_output(['git','show','origin/main:'+name])!=subprocess.check_output(['git','show',DESIGN_MAIN+':'+name]):
            raise ValueError('approved design changed; review first')
    p=ARTIFACT/'dispatch.private.py';m=meta(p);raw=p.read_bytes()
    if not(stat.S_ISREG(m[4])and m[2]==os.geteuid()and stat.S_IMODE(m[4])==0o400 and m[5]==1 and not os.listxattr(p)):
        raise ValueError('exact operational artifact envelope refused')
    if meta(p)!=m or hashlib.sha256(raw).hexdigest()!=SHA or raw!=candidate.payload().encode():
        raise ValueError('same final qualified artifact required')
    qualified=json.loads(QUALIFIED.read_bytes())
    if qualified['actualExit']!=0 or qualified['payloadSha256']!=SHA or qualified['result']['newScopeNormalClose']is not True:
        raise ValueError('actual same-artifact read qualification first')
    post=W/'pg4150-failed-done-post-artifact-v1/post.private.py'
    fixed=json.loads((post.parent/'manifest.safe.json').read_bytes())
    if hashlib.sha256(post.read_bytes()).hexdigest()!=fixed['payloadSha256']:raise ValueError('independent post prepared first')
    forward=process(20445)
    if forward!={'pid':20445,'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:
        raise ValueError('forward owner changed')
    code,text=run(identity.HOST,timeout=30)
    if code!=0:raise ValueError('host VM owner refused')
    host=json.loads(text.strip())
    if host['boot']!='c7964823-c628-4ef2-99b5-07b0f0b62bba':raise ValueError('host boot changed')
    OUT.mkdir(mode=0o700)
    durable(OUT/'start.safe.json',{'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
        'payloadSha256':SHA,'owner':process(os.getpid()),'host':host,'forward':forward,
        'designMain':DESIGN_MAIN,'postPayloadSha256':fixed['payloadSha256'],'replayAllowed':False})
    with management_gate(P/'current-management-critical.lock'):
        with(OUT/'stdout.private.log').open('xb')as output,(OUT/'stderr.private.log').open('xb')as error:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-','recover'],stdin=subprocess.PIPE,stdout=output,stderr=error)
            durable(OUT/'ssh.private.json',process(child.pid))
            child.stdin.write(raw);child.stdin.close()
            # No automatic timeout/termination of an unknown remote owner. The job remains
            # attachable through this recorded observer/PID and its fixed source/run on interruption.
            code=child.wait();output.flush();error.flush();os.fsync(output.fileno());os.fsync(error.fileno())
    value={'actualExit':code,'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e',
           'payloadSha256':SHA,'formalAccepted':False,'oldParentNormal':False,'independentPostRequired':True}
    if code==0:
        value['result']=completed_output((OUT/'stdout.private.log').read_bytes())
    durable(OUT/'manifest.safe.json',value);print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
