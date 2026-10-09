"""BUG974: new-only unused candidate placement against independent retired861."""
import ast
from pathlib import Path
from pg863_stage_candidate import source as previous
R=Path(__file__).resolve().parent
BASELINE_SHA='4bd686da5660104c6dc6975baa468fd80a015e5ecfcc3896fc26b4f9e2147579'

def validate_baseline(value, baseline, runtime_entries):
    assert runtime_entries == []
    assert value['rows'] == baseline['rows']
    assert len(value['rows']) == 24 and len(value['rows']['schubert.batch_runs']) == 564
    assert value['configuration'] == baseline['configuration']
    assert len(value['configuration']) == 10
    assert all(len(v) == 32 for v in value['configuration'].values())
    assert value['units'] == baseline['units']
    assert value['trees'] == baseline['trees']

def source():
    import inspect
    raw=previous()
    for a,b in (
        ('pg863-stage-v1','pg863-stage-v2'),('pg863-release-v1.tar','pg863-release-v2.tar'),
        ('pg863-candidate-stage-v1','pg863-candidate-stage-v2'),
        ('pg751-completed-baseline-v1/before.private.json','pg861-runtime841-retired-post-v1/after.private.json'),
        ('8c722e15a3bc9b6e311fe69cef0cd2aa3a954e87586c861cafa7279cd3dab6c0',BASELINE_SHA),
        ('==534','==564'),
    ):
        assert a in raw;raw=raw.replace(a,b)
    raw=raw.replace("assert not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf').exists()",
        "assert not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir())")
    raw=raw.replace("value['rows']=rows;value['current']=str(current.readlink());terminal();return value",'''value['rows']=rows;value['current']=str(current.readlink())
 comparable={'rows':rows,'trees':{},'units':{},'configuration':{}}
 for name in baseline['trees']:
  p=pathlib.Path(name); entries={}
  for q in (p,*sorted(p.rglob('*'))):
   s=q.lstat();assert not q.is_symlink() and (stat.S_ISDIR(s.st_mode)or stat.S_ISREG(s.st_mode))
   entries[str(q)]={'metadata':[s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns], 'sha256':hashlib.sha256(q.read_bytes()).hexdigest()if q.is_file()else None}
   assert q.lstat()==s
  comparable['trees'][name]=entries
 for field in ('units','configuration'):
  comparable[field]={u:dict(l.split('=',1)for l in value[field][u].splitlines())for u in units}
 validate_baseline(comparable,baseline,list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir()))
 terminal();return value''')
    marker='before=protected();assert before==protected()'
    assert raw.count(marker)==1
    raw=raw.replace(marker,inspect.getsource(validate_baseline)+'\n'+marker)
    assert '751-completed' not in raw and '==534' not in raw and 'pg492-once-resume' not in raw
    ast.parse(raw);return raw

if __name__=='__main__':
    namespace={'__file__':str(R/'pg863_stage_candidate_v2.py'),'__name__':'new_only_unused_signed862_v2'}
    exec(compile(source(),'<863 v2 complete retired861 before>','exec'),namespace);namespace['main']()
