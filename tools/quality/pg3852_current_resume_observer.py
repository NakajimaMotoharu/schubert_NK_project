"""New immutable read-only observer for the independently prepared current resume."""
from pathlib import Path
import pg3798_hygiene_current_observer as previous
from pg3844_current_resume_sources import SOURCE,BOM
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate


def source():
    raw=previous.source().replace('pg3798','pg3852').replace('PG3798','PG3852')
    marker=" assert json.loads((W/'pg3794-hygiene-publication-independent-post-v1/manifest.safe.json').read_bytes())['actualExit']==0"
    if raw.count(marker)!=1:raise ValueError('one immutable observer admission boundary')
    raw=raw.replace(marker," post=json.loads((W/'pg3850-current-resume-independent-post-v1/manifest.safe.json').read_bytes());assert post['actualExit']==0 and post['source']==SOURCE and post['result']['independentResumeOnlyDeltaVerified'] and post['result']['newTenRefsReturnedNormally'] and post['result']['snapshotKeys']==11")
    compile(raw,'<current prepared resume immutable observer>','exec');return raw


def namespace():
    values={'__file__':str(Path(__file__).resolve().parent/'vm/050_s1/pg3852_current_resume_observer.py'),'__name__':'current_resume_readonly_observer'}
    exec(compile(source(),'<new current resume observer namespace>','exec'),values);return values


def main():
    import sys
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':main()
