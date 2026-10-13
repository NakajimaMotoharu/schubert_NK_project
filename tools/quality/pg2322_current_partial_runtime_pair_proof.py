"""Full current pair and exact partially published runtime; no reload or signal."""
import json
import types
from pyflakes.api import check
import pg2309_current_resume_pair_proof as prior
from pg1446_current_cold_stage import W

SLOT='pg2322-current-partial-runtime-pair-proof-v1'
SOURCE=prior.SOURCE


def bound(raw):
    for old,new in [('96640','98485'),('1550071','1656317'),('96638','98483'),('96671','98516'),('1550259','1656547'),('96669','98514'),('pg2304-current-completed-resume-tools-v1','pg2316-current-cold-resume-tools-v1'),('pg2304_native_refs.py','pg2316_native_refs.py'),('Pg2304FreshResumePreparation','Pg2316FreshResumePreparation'),('pg2308-current-completed-resume-preparation-v1','pg2320-current-cold-resume-preparation-v1')]:raw=raw.replace(old,new)
    return raw


PARTIAL=r'''
failed=base/'pg2320-current-cold-resume-preparation-v1'
require({p.name for p in failed.iterdir()}=={'before.private.json','refs-prepare.private.log'})
require(hashlib.sha256((failed/'before.private.json').read_bytes()).hexdigest()=='e7456ef531cde4d5e09161f401861ad0f718febbe786e59038e46dc869298a1e')
require(hashlib.sha256((failed/'refs-prepare.private.log').read_bytes()).hexdigest()=='5f055b7cad0de6710e706b65b269fbdfd05234be61a60a7dbf978b2ceafc4f1e')
expected_runtime={
 '/run/systemd/system':{'metadata':[28,3,0,0,stat.S_IFDIR|0o755,3,60,1791913648315000000,1791913648315000000],'sha256':None},
 '/run/systemd/system/schubert-nk-morning-controller.service.d':{'metadata':[28,4223,0,0,stat.S_IFDIR|0o755,2,60,1791913648316105696,1791913648316105696],'sha256':None},
 '/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf':{'metadata':[28,4224,0,0,stat.S_IFREG|0o644,1,644,1791913648316105696,1791913648316105696],'sha256':'888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035'}}
require(set(after['runtime'])=={'/run/systemd/system'})
require(after['runtime']['/run/systemd/system']['metadata']==[28,3,0,0,stat.S_IFDIR|0o755,2,40,1791897065158000000,1791897065158000000])
require(tree(pathlib.Path('/run/systemd/system'))==expected_runtime)
native_option=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes()
argv=[line[len(b'ExecStart='):]for line in native_option.splitlines()if line.startswith(b'ExecStart=')and line!=b'ExecStart='];require(len(argv)==1)
literal=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv[0]+b' --resume 91f5484b-9702-4c7c-97f3-dd5110a853f9\n'
require(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf').read_bytes()==literal)
require(hashlib.sha256(literal).hexdigest()=='888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035')
after['runtime']=expected_runtime
'''


def body():
    raw=bound(prior.body())
    marker='\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker)!=1:raise ValueError('one independently referenced full snapshot required')
    return raw.replace(marker,'\n'+PARTIAL+'\n'+marker)


def payload():
    frozen=json.loads((W/'pg2317-frozen-v1.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['productionSource']!=SOURCE:raise ValueError('actual current cold fullABI required')
    tail=bound(prior.TAIL).replace(prior.SLOT,SLOT)
    start=tail.index('failed=');end=tail.index("tool=base/",start)
    tail=tail[:start]+tail[end:]
    tail=tail.replace("'runtimeDirectoryAbsent':True,'runtimeWriteReload0':True","'partialRuntimeFileVerified':True,'reloadNotReserved':True")
    raw='TOOL_HASHES='+repr(frozen['fileHashes'])+'\n'+body()+tail
    if check(raw,'<whole partial current runtime pair>'):raise ValueError('all partial proof globals required')
    compile(raw,'<partial current runtime pair>','exec');return raw


def main():
    fn=types.FunctionType(prior.main.__code__,{**prior.__dict__,'SLOT':SLOT,'payload':payload},'current_partial_runtime_pair_proof')
    return fn()


if __name__=='__main__':raise SystemExit(main())
