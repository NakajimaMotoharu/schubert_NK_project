"""Independent literal resume-only delta plus original24/187/Backup/ten-unit/resource post."""
import json
import types
from pyflakes.api import check
import pg2940_current_resume_before as prior
from pg2950_current_cold_resume_sources import SAVE,RUN

SLOT='pg2956-current-resume-independent-post-v1'

ORACLE=r'''
fresh=base/FRESH
def fresh_private(name):
 p=fresh/name;s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 raw=p.read_bytes();require(metadata(p)==[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]);return raw
require(fresh_private('complete.private')==b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\nfreshResumeRuntimePrepared=true\nnormalSingleRuntimeReload=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsEpochSqlWrites0=true\noldUnknownNormalized=false\n')
require(fresh_private('refs-prepare.private.log')==b'')
require(fresh_private('daemon-reload-reserved.private')==b'one normal runtime daemon-reload; no retry\n')
initial=json.loads(fresh_private('before.private.json'));final=json.loads(fresh_private('after.private.json'))
require(initial==after and set(final)==set(initial))
require(all(final[k]==initial[k]for k in initial if k not in {'configuration','runtime'}))
from CONFIG_MODULE import exec_record,config_same
morning='schubert-nk-morning-controller.service';root='/run/systemd/system';directory=root+'/'+morning+'.d';target=directory+'/zz-pg2950-once-resume.conf'
require(set(final['configuration'])==set(initial['configuration']))
for unit,old in initial['configuration'].items():
 new=final['configuration'][unit]
 if unit!=morning:require(config_same(old,new,exec_record));continue
 require(set(old)==set(new)and all(new[k]==old[k]for k in old if k not in {'ExecStart','DropInPaths'}))
 left=exec_record(old['ExecStart']);right=exec_record(new['ExecStart']);require(left is not None and right is not None)
 require(right[:3]==(left[0],left[1]+' --resume '+RESUME_RUN,left[2])and tuple(right[3:])==('n/a','n/a','0','(null)','0/0'))
 require(new['DropInPaths']==old['DropInPaths']+' '+target)
native_bytes=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes()
argv=[x[len(b'ExecStart='):]for x in native_bytes.splitlines()if x.startswith(b'ExecStart=')and x!=b'ExecStart='];require(len(argv)==1)
literal=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv[0]+b' --resume '+RESUME_RUN.encode('ascii')+b'\n'
require(fresh_private('new-runtime.private')==literal)
clock=json.loads(fresh_private('metadata-clock-lower.private.json'));require(set(clock)=={'clockId','lowerNs','fallback'}and clock['clockId']==5 and type(clock['lowerNs'])is int and clock['lowerNs']>0 and clock['fallback']is False)
lower=clock['lowerNs'];prepared=json.loads(fresh_private('runtime-prepared.private.json'));upper=(fresh/'runtime-prepared.private.json').lstat().st_mtime_ns
require(0<lower<=upper and set(initial['runtime'])=={root}and set(prepared)=={root,directory,target})
old=initial['runtime'][root]['metadata'];new=prepared[root]['metadata'];d=prepared[directory]['metadata'];f=prepared[target]['metadata']
require(old[2:6]==[0,0,stat.S_IFDIR|0o755,2]and new[:5]==old[:5]and new[5]==3 and new[6]>=old[6])
require(all(max(old[i],lower)<=new[i]<=upper for i in [7,8]))
require(d[0]==old[0]and d[1]not in {0,old[1]}and d[2:6]==[0,0,stat.S_IFDIR|0o755,2])
require(f[0]==old[0]and f[1]not in {0,old[1],d[1]}and f[2:7]==[0,0,stat.S_IFREG|0o644,1,len(literal)])
require(all(lower<=row[i]<=upper for row in [d,f]for i in [7,8]))
require(prepared[root]['sha256']is None and prepared[directory]['sha256']is None and prepared[target]['sha256']==hashlib.sha256(literal).hexdigest())
require(tree(pathlib.Path(root))==prepared==final['runtime']and pathlib.Path(target).read_bytes()==literal)
require(not os.listxattr(root)and not os.listxattr(directory)and not os.listxattr(target))
gap=fresh_private('observations.private').decode('ascii');require(re.fullmatch(r'maxGapNanos=[0-9]+\n',gap)is not None and int(gap.split('=')[1])<30000000000)
# Only the two independently constrained fields are projected. The retained raw
# before/after anchors stay byte-identical; no observed DB/result becomes oracle.
after={**after,'configuration':final['configuration'],'runtime':prepared}
'''


def payload(seals):
    raw=prior.payload(seals).replace(prior.SLOT,SLOT).replace('PG2940-current-resume-before-v1','PG2956-current-resume-independent-post-v1')
    marker='\nbus = dbus.SystemBus(private=True)\n'
    if raw.count(marker)!=1:raise ValueError('one independent resource boundary required')
    extra='FRESH='+repr(SAVE)+'\nRESUME_RUN='+repr(RUN)+'\n'+ORACLE.replace('CONFIG_MODULE','pg2950_configuration')
    extra="import sys\nsys.path.insert(0,'/var/lib/pgpt-s1-preservation/pg2950-current-cold-resume-tools-v1')\n"+extra
    raw=raw.replace(marker,'\n'+extra+marker)
    marker="'rawExported': False"
    if raw.count(marker)!=1:raise ValueError('one independent proof publication required')
    raw=raw.replace(marker,marker+",'independentResumeOnlyDeltaVerified':True,'normalResumePrepared':True,'coarseClockMeasured':True")
    if check('HASHES={}\nRECEIPT="actual"\n'+raw,'<independent literal current full post>'):raise ValueError('complete post namespace required')
    compile(raw,'<only exact approved resume/runtime delta>','exec');return raw


def entry():
    actual=json.loads((prior.prior.W/'pg2954-prepare-resume-v1.safe.json').read_bytes())
    if actual.get('actualExit')!=0 or actual.get('sourceQualified')is not True or actual.get('freshResumeRuntimePrepared')is not True or actual.get('normalSingleRuntimeReload')is not True:
        raise ValueError('actual successful normal resume preparation required')
    fn=prior.entry()
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SLOT':SLOT,'payload':payload},'current_resume_independent_post')


if __name__=='__main__':raise SystemExit(entry()())
