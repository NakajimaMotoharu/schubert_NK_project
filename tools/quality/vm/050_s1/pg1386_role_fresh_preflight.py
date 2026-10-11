"""Fresh separate full current proof after failed owner's actual recovery."""
import pg1376_bootstrap_role_preflight as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    return previous.payload(seals).replace('pg1376-bootstrap-role-preflight-v1','pg1386-role-fresh-preflight-v1').replace('PG1376-bootstrap-role-preflight-v1','PG1386-role-fresh-preflight-v1')

def main():
    env=dict(previous.previous.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    raw=previous.source().replace('pg1376-bootstrap-role-preflight-v1','pg1386-role-fresh-preflight-v1')
    exec(compile(raw,'<fresh current role preflight transport>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
