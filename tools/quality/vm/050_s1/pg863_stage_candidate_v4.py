"""BUG976: reuse strict canonical32 plus actual typed empty ExecStop proof."""
import ast
from pathlib import Path
from pg863_stage_candidate_v3 import source as previous
from pg776_failure_full import ADDITIONAL
R=Path(__file__).resolve().parent
def source():
    raw=previous().replace('pg863-stage-v3','pg863-stage-v4').replace('pg863-release-v3.tar','pg863-release-v4.tar').replace('pg863-candidate-stage-v3','pg863-candidate-stage-v4')
    pure=(R/'pg775_configuration.py').read_text().replace('FragmentPath,DropInPaths','FragmentPath,DropInPaths,RestrictSUIDSGID,UMask,LimitCORE,MemoryMax,TasksMax')
    marker='def protected():';assert raw.count(marker)==1
    raw=raw.replace(marker,pure+'\n'+ADDITIONAL+'\n'+marker)
    marker="value['configuration']={u:subprocess.check_output(['systemctl','show',u,'--property='+','.join(sorted(baseline['configuration'][u]))],text=True)for u in units}"
    assert raw.count(marker)==1
    raw=raw.replace(marker,"value['configuration']={u:complete_configuration(subprocess.check_output(['systemctl','show',u,'--property='+','.join(sorted(baseline['configuration'][u]))],text=True),u)for u in units}")
    raw=raw.replace("for field in ('units','configuration'):","comparable['configuration']=value['configuration']\n for field in ('units',):")
    ast.parse(raw);return raw
if __name__=='__main__':
    namespace={'__file__':str(R/'pg863_stage_candidate_v4.py'),'__name__':'new_only_unused_signed862_v4'}
    exec(compile(source(),'<863 actual canonical32 v4>','exec'),namespace);namespace['main']()
