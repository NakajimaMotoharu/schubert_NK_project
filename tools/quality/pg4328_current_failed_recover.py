"""SSC291 exact one-shot recovery. Only after published design, frozen inspect and independent post preparation."""
import hashlib
import inspect
import json
import os
import stat
import subprocess
import sys
import pg4152_exact_failed_done_recover as previous
import pg4316_current_failed_dispatch as driver
import pg4324_current_failed_post as post
import pg3428_vm_candidate_preflight_readonly as identity
from lan_server import run
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate

OUT=W/(driver.SLOT+'-recover')
DESIGN_MAIN='5086547c33aa61c94dbac02085dc34a23f94e15d'
DRIVER_SHA='87ef52f80156a0c83ae1451a08f1b20508797c6072c9b86263af90b163569182'
POST_SHA='f1a3cea25c936b78bfe18a1d5aebd24f97146d351d891902354fa2ad4eae53d3'


def completed_output(raw):
    ns={**vars(previous)}
    text=inspect.getsource(previous.completed_output).replace('SSC287_STOPPED','SSC291_STOPPED').replace('all33StartupEntriesPreserved','all37StartupEntriesPreserved')
    exec(compile(text,'<current bounded complete recovery receipt>','exec'),ns);return ns['completed_output'](raw)


def fixed(path,expected):
    m=previous.meta(path);s=path.lstat();raw=path.read_bytes()
    if not(stat.S_ISREG(s.st_mode)and s.st_uid==os.geteuid()and stat.S_IMODE(s.st_mode)==0o400 and s.st_nlink==1 and not os.listxattr(path)):
        raise ValueError('exact private frozen artifact required')
    if previous.meta(path)!=m or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('unchanged frozen bytes required')
    return raw


def main():
    if sys.argv[1:]!=['recover']:raise SystemExit('recover once only; existing OUT prohibits replay')
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed current operator required')
    if subprocess.check_output(['git','diff','--name-only',driver.role.SOURCE,'HEAD','--','src','pom.xml','mvnw','.mvn','program/characterization']):raise ValueError('unchanged actual current whole3717 source required')
    subprocess.run(['git','merge-base','--is-ancestor',DESIGN_MAIN,'origin/main'],check=True)
    for name in ['documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md','documents/300_SS/350_運用・品質/353_障害検知・復旧runbook.md']:
        if subprocess.check_output(['git','show','origin/main:'+name])!=subprocess.check_output(['git','show',DESIGN_MAIN+':'+name]):raise ValueError('published current design changed; review first')
    raw=fixed(driver.ARTIFACT/'dispatch.private.py',DRIVER_SHA)
    if raw!=driver.payload().encode():raise ValueError('exact same qualified actual driver required')
    qualified=json.loads((W/(driver.SLOT+'-inspect')/'manifest.safe.json').read_bytes())
    if qualified['actualExit']!=0 or qualified['source']!=driver.role.SOURCE or qualified['payloadSha256']!=DRIVER_SHA or qualified['result']['newScopeNormalClose']is not True:raise ValueError('same artifact actual normal inspect required')
    prepared=fixed(post.ARTIFACT/'post.private.py',POST_SHA)
    if prepared!=post.payload().encode():raise ValueError('same fixed independent post prepared first')
    q=json.loads((W/'pg4330-current-recovery-qualification-v1/manifest.safe.json').read_bytes())
    if q['actualExit']!=0 or q['source']!=driver.role.SOURCE or q['driverSha256']!=DRIVER_SHA or q['postSha256']!=POST_SHA:raise ValueError('complete current qualification required')
    for name,digest in q['hostSha256'].items():
        from pathlib import Path
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:raise ValueError('all affected qualified host bytes unchanged')
    forward=previous.process(20445)
    if forward!={'pid':20445,'ticks':104194,'argvSha256':'fd6ff71b025aa4b485f64f9dd2289f9072ac6f78d9fc6a9c44912adf8bad097b'}:raise ValueError('fresh exact forward required')
    code,text=run(identity.HOST,timeout=30)
    if code!=0:raise ValueError('fresh host/VM ownership required')
    host=json.loads(text)
    if host['boot']!='c7964823-c628-4ef2-99b5-07b0f0b62bba':raise ValueError('same host boot required')
    os.umask(0o077);OUT.mkdir(mode=0o700)
    previous.durable(OUT/'start.safe.json',{'source':driver.role.SOURCE,'payloadSha256':DRIVER_SHA,'postPayloadSha256':POST_SHA,'owner':previous.process(os.getpid()),'host':host,'forward':forward,'designMain':DESIGN_MAIN,'replayAllowed':False})
    with management_gate(P/'current-management-critical.lock'):
        with(OUT/'stdout.private.log').open('xb')as stdout,(OUT/'stderr.private.log').open('xb')as stderr:
            child=subprocess.Popen(SSH+['sudo','-n','python3','-B','-','recover'],stdin=subprocess.PIPE,stdout=stdout,stderr=stderr)
            previous.durable(OUT/'ssh.private.json',previous.process(child.pid))
            child.stdin.write(raw);child.stdin.close();code=child.wait();stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
    value={'actualExit':code,'source':driver.role.SOURCE,'payloadSha256':DRIVER_SHA,'postRequired':True,'oldParentNormal':False,'formalAccepted':False}
    if code==0:value['result']=completed_output((OUT/'stdout.private.log').read_bytes())
    previous.durable(OUT/'manifest.safe.json',value);print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
