"""Fresh full retained current/resources after unused stage, old result is not reused."""
from pathlib import Path
from pg935_current_preflight import payload as previous
R=Path(__file__).resolve().parent
def payload(proof,seals):
    return previous(proof,seals).replace('pg935-current-preflight-v1','pg939-current-stage-post-v1').replace('PG935-current-preflight-v1','PG939-current-stage-post-v1')
if __name__=='__main__':
    raw=(R/'pg901_bootstrap_post.py').read_text();env={'__file__':str(R/'pg939_retained_stage_post.py'),'__name__':'fresh_retained_stage_post'}
    exec(compile(raw,'<939 existing readonly dispatcher>','exec'),env);env['payload']=payload
    main=raw[raw.index('def main():'):raw.index("if __name__=='__main__':")].replace('pg901-bootstrap-post-v1','pg939-current-stage-post-v1')
    exec(compile(main,'<939 new-only retained post>','exec'),env);env['main']()
