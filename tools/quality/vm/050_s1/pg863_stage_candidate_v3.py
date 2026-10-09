"""BUG975: strict nine preserved metadata; read access time is not authority."""
import ast,inspect
from pathlib import Path
from pg863_stage_candidate_v2 import source as previous
R=Path(__file__).resolve().parent
def metadata(s):
    return [s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def source():
    raw=previous().replace('pg863-stage-v2','pg863-stage-v3').replace('pg863-release-v2.tar','pg863-release-v3.tar').replace('pg863-candidate-stage-v2','pg863-candidate-stage-v3')
    marker='baseline=json.loads(baseline_raw)';assert raw.count(marker)==1
    raw=raw.replace(marker,marker+'\n'+inspect.getsource(metadata))
    assert raw.count('assert q.lstat()==s')==1
    raw=raw.replace('assert q.lstat()==s','assert metadata(q.lstat())==metadata(s)')
    ast.parse(raw);return raw
if __name__=='__main__':
    namespace={'__file__':str(R/'pg863_stage_candidate_v3.py'),'__name__':'new_only_unused_signed862_v3'}
    exec(compile(source(),'<863 strict nine metadata v3>','exec'),namespace);namespace['main']()
