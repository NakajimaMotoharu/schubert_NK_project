"""Fresh all32/all24/current signed187/resource authentication before new staging.
Reuse only proven readonly algorithm, not its old result; no Unit start/stop/deploy.
"""
from pathlib import Path
from pg906_retained_inspector_v2 import payload as previous
R=Path(__file__).resolve().parent
def payload(proof,seals):
    return previous(proof,seals).replace('pg906-retained-inspector-v2','pg935-current-preflight-v1').replace('PG906-retained-inspector-v2','PG935-current-preflight-v1')
if __name__=='__main__':
    raw=(R/'pg901_bootstrap_post.py').read_text();env={'__file__':str(R/'pg935_current_preflight.py'),'__name__':'fresh_current_preflight'}
    exec(compile(raw,'<935 existing readonly dispatcher>','exec'),env);env['payload']=payload
    main=raw[raw.index('def main():'):raw.index("if __name__=='__main__':")].replace('pg901-bootstrap-post-v1','pg935-current-preflight-v1')
    exec(compile(main,'<935 new-only current preflight>','exec'),env);env['main']()
