"""Independent literal same-run argv/runtime oracle plus full closed-resource snapshot."""
import datetime
import hashlib
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg1963_reload_ref_scoped_full_post import payload as previous

SLOT='pg1986-fresh-resume-independent-post-v1'


def payload():
    raw=previous().replace('pg1963-reload-ref-scoped-full-post-v1',SLOT)
    begin=raw.index("    original_configuration=after['configuration'];new_configuration={}")
    end=raw.index("    after['configuration']=new_configuration",begin)+len("    after['configuration']=new_configuration")
    raw=raw[:begin]+'\n'.join('    '+line for line in ORACLE.splitlines())+raw[end:]
    raw=raw.replace("'normalSingleReload':True","'normalSingleReload':False,'normalSingleRuntimeReload':True,'freshResumeRuntimePrepared':True")
    from pyflakes.api import check
    if check(raw,'<independent literal freshresume full post>'):raise ValueError('all actual post globals required')
    compile(raw,'<fresh completed resume full post>','exec');return raw


ORACLE=r'''
qualified=base/'pg1963-reload-ref-scoped-full-post-v1';qualified_raw=(qualified/'before.private.json').read_bytes()
require(hashlib.sha256(qualified_raw).hexdigest()=='ee13ec0b75e1320f4daba711ef90d24b2c05ae588c3b27fedb0224114896fc15')
original=json.loads(qualified_raw)
fresh=base/'pg1984-fresh-resume-preparation-v1'
def fresh_private(name):
 p=fresh/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o600,1)and not os.listxattr(p))
 value=p.read_bytes();require(metadata9(p.lstat())==metadata9(s));return value
require(fresh_private('complete.private')==b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\nfreshResumeRuntimePrepared=true\nnormalSingleRuntimeReload=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstartsStopsEpochSqlWrites0=true\noldUnknownNormalized=false\n')
require(fresh_private('daemon-reload-reserved.private')==b'one normal runtime daemon-reload; no retry\n')
require(fresh_private('refs-prepare.private.log')==b'')
require(hashlib.sha256(fresh_private('before.private.json')).hexdigest()=='ee13ec0b75e1320f4daba711ef90d24b2c05ae588c3b27fedb0224114896fc15')
new=json.loads(fresh_private('after.private.json'))
require(set(new)==set(original)and all(new[k]==original[k]for k in original if k not in {'configuration','runtime'}))
require(set(after)==set(original)and all(after[k]==original[k]for k in original if k not in {'configuration','runtime'}))
morning='schubert-nk-morning-controller.service';target='/run/systemd/system/'+morning+'.d/zz-pg1980-once-resume.conf'
require(set(new['configuration'])==set(original['configuration']))
for unit,old in original['configuration'].items():
 current=complete_configuration(command(['systemctl','show',unit,'--property='+','.join(sorted(FIELDS))]).decode(),unit)
 require(current==new['configuration'][unit]and set(current)==set(old))
 if unit!=morning:require(current==old);continue
 require(all(current[k]==old[k]for k in old if k not in {'ExecStart','DropInPaths'}))
 left=exec_record(old['ExecStart']);right=exec_record(current['ExecStart']);require(left is not None and right is not None)
 require(right[:3]==(left[0],left[1]+' --resume 4148e3e8-f107-431a-ab27-d6e6d1f1772e',left[2])and right[3:]==('n/a','n/a','0','(null)','0/0'))
 require(current['DropInPaths']==old['DropInPaths']+' '+target)
native=pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes()
require(hashlib.sha256(native).hexdigest()=='9a6d94310d1f18e1a0b09882503948e43f1a76386962c7ba8a73a166091201b7')
argv=[line[len(b'ExecStart='):]for line in native.splitlines()if line.startswith(b'ExecStart=')and line!=b'ExecStart='];require(len(argv)==1)
literal=b'# SS343 6.13: explicit same-run fresh activation; retire after genuine terminal.\n[Service]\nExecStart=\nExecStart='+argv[0]+b' --resume 4148e3e8-f107-431a-ab27-d6e6d1f1772e\n'
require(fresh_private('new-runtime.private')==literal)
runtime_actual=tree(pathlib.Path('/run/systemd/system'));runtime_before=original['runtime'];directory='/run/systemd/system/'+morning+'.d'
require(set(runtime_before)=={'/run/systemd/system',directory}and set(runtime_actual)==set(runtime_before)|{target})
require(runtime_actual['/run/systemd/system']==runtime_before['/run/systemd/system'])
old=runtime_before[directory]['metadata'];current=runtime_actual[directory]['metadata']
lower=(fresh/'before.private.json').stat().st_mtime_ns;upper=(fresh/'runtime-prepared.private.json').stat().st_mtime_ns
require(current[:6]==old[:6]and current[6]>=old[6]and all(max(old[i],lower)<=current[i]<=upper for i in [7,8]))
metadata_target=runtime_actual[target]['metadata'];require(metadata_target[0]==old[0]and metadata_target[1]!=old[1]and metadata_target[2:7]==[0,0,stat.S_IFREG|0o644,1,len(literal)]and all(lower<=metadata_target[i]<=upper for i in [7,8]))
require(pathlib.Path(target).read_bytes()==literal and not os.listxattr(target)and not os.listxattr(directory))
require(runtime_actual==json.loads(fresh_private('runtime-prepared.private.json'))==new['runtime'])
gap=fresh_private('observations.private').decode('ascii');require(re.fullmatch(r'maxGapNanos=[0-9]+\n',gap)is not None and int(gap.split('=')[1])<30000000000)
require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
after=new
'''


def main():
    actual=json.loads((W/'pg1983-prepare-resume-v1.safe.json').read_bytes())
    if actual['actualExit']!=0 or actual['sourceQualified']is not True or actual['freshResumeRuntimePrepared']is not True or actual['currentApprovalEpochChanged']is not False or subprocess.check_output(['git','status','--porcelain']):raise ValueError('actual normal freshresume preparation and clean fixed source required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    value={'actualExit':r.returncode,'operatorSource':operator,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False}
    if not r.returncode:value.update(json.loads(r.stdout))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
