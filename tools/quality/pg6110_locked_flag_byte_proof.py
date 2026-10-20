"""Actual one-field ClassFile delta and all JVM method/lock/remaining visibility obligations."""
import argparse
import hashlib
import json
import os
import subprocess
import zipfile
from collections import Counter
from pg5940_private_lock_compile import W,BASE,TC,sha
from pg6108_locked_flag_qualification import SOURCE
from pg6106_locked_flag_selected import MAIN
from classfile_field_flags import fields,only_clear_private_volatile
from pg6056_expiry_read_methods import methods

CLASS='dev.codex.schubert.nk.web.messaging.ArtemisReplyConsumers'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--qualification-sha256',required=True);args=parser.parse_args()
    qp=BASE/'PG6108-locked-flag-qualification-v1/manifest.json'
    if sha(qp)!=args.qualification_sha256:raise ValueError('genuine same-source925 qualification hash before byte proof')
    q=json.loads(qp.read_bytes());private=W/'pg6108-locked-flag-qualification-v1/manifest.safe.json'
    if q['source']!=SOURCE or q['actualExit']!=0 or (q['tests'],q['suites'],q['physicalMain'])!=(925,150,1667)or sha(private)!=q['privateManifestSha256']:
        raise ValueError('one current925 all8511667 source/byte manifest')
    oldbase=W/'pg6090-original3985-artifacts-v1/jars';newbase=W/'pg6106-locked-flag-web925-v1/source/src'
    def jar(module,old=False):return oldbase/('schubert-nk-'+module+'.jar')if old else newbase/('schubert-nk-'+module+'/target/schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
    def binary(module,cls,old=False):
        with zipfile.ZipFile(jar(module,old))as z:return z.read(cls.replace('.','/')+'.class')
    def text(module,cls,old=False,public=False):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'),*(['-public','-s']if public else['-p','-c','-s']),'-classpath',str(jar(module,old)),cls],text=True)
    before,after=binary('web',CLASS,True),binary('web',CLASS)
    key='web:'+CLASS.replace('.','/')+'.class'
    if q['changedPhysical']!=[key]or q['unchangedPhysical']!=1666:raise ValueError('one actual changed class only,all1666 other Main bytes unchanged')
    changed=only_clear_private_volatile(before,after)
    f=fields(after)
    if (f[b'stateLock']['flags'],f[b'stopping']['flags'],f[b'started']['flags'])!=(0x12,0x42,0x42):
        raise ValueError('private final lock and two outside-lock visibility fields retained')
    blocks=methods(text('web',CLASS));prior=methods(text('web',CLASS,True))
    if blocks!=prior or text('web',CLASS,public=True)!=text('web',CLASS,True,public=True):
        raise ValueError('all method descriptors/instructions/exception edges/public ABI unchanged')
    close=blocks['  public void close();'];accesses=[(k,v.count('// Field closed:Z'))for k,v in blocks.items()if '// Field closed:Z'in v]
    if accesses!=[('  public void close();',2)]or not close.index('ReentrantLock.lock:')<close.index('// Field closed:Z')<close.index('ReentrantLock.unlock:'):
        raise ValueError('both closed accesses only within same lock-owned close method')
    roles=[]
    for module,cls in (('api','dev.codex.schubert.nk.api.messaging.inbound.SyncRequestConsumers'),
                        ('api','dev.codex.schubert.nk.api.messaging.inbound.WebLogConsumers')):
        b=binary(module,cls);m=methods(text(module,cls));ready=m['  public boolean ready();']
        if fields(b)[b'closed']['flags']!=0x42 or '// Field closed:Z'not in ready or 'ReentrantLock.lock:'in ready:
            raise ValueError('API ready reads closed outside a lock;do not delete required visibility')
        roles.append(dict(className=cls,closedFlags=0x42,readyReadsClosedWithoutLock=True,modified=False))
    for module,cls,lock in (('api','dev.codex.schubert.nk.api.messaging.inbound.QuestionWorkConsumers',b'lock'),
                             ('web','dev.codex.schubert.nk.web.messaging.WebBrokerContexts',b'stateLock')):
        b=binary(module,cls);f=fields(b)
        if f[b'closed']['flags']!=2 or f[lock]['flags']!=0x12:raise ValueError('existing nonvolatile/own private final lock implementation retained')
        roles.append(dict(className=cls,closedFlags=2,privateFinalLock=True,modified=False))
    raw=json.loads(private.with_name('findings.safe.json').read_bytes())
    oldraw=json.loads((W/'pg6082-web-factory-qualification-v1/findings.safe.json').read_bytes())
    old=[r for r in oldraw if r['sourcePath']==MAIN];new=[r for r in raw if r['sourcePath']==MAIN]
    ignored=[r for r in old if r['rule']=='AvoidUsingVolatile'and r['beginline']=='23']
    signature=lambda r:tuple(r[k]for k in('rule','beginline','endline','begincolumn','endcolumn','priority','diagnosticTextSha256'))
    if len(ignored)!=1 or len(old)!=19 or len(new)!=18 or Counter(map(signature,new))!=Counter(map(signature,[r for r in old if r not in ignored]))or q['pmdRawFindings']!=1314:
        raise ValueError('only the specified closed volatile warning disappears;other18/allraw retained')
    value=dict(actualExit=0,source=SOURCE,qualificationSha256=sha(qp),classFileDelta=changed,
        oldClassSha256=hashlib.sha256(before).hexdigest(),newClassSha256=hashlib.sha256(after).hexdigest(),
        allMethodInstructionsAndExceptionsUnchanged=True,publicAbiUnchanged=True,closedAccessSites=accesses,
        lockCodeSha256=hashlib.sha256(close.encode()).hexdigest(),otherOwnerRoles=roles,
        rawPmdFindings=1314,removedWarnings=1,otherOwnerWarningsUnchanged=18,
        testsExecuted=0,additionalBuildsIssued=0,formalAccepted=False,fullCurrentWholePending=True,
        oldSourceWholeImported=False,nativeQualified=False,ptAlternativeCompleted=0)
    os.umask(0o077);out=BASE/'PG6110-locked-flag-byte-v1';out.mkdir()
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,source=SOURCE,classFileDelta=changed,pmdRaw=1314,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
