"""One current exact-entry retire/reload in normal M/A/DB/Ref scopes, no business replay."""
import json
import os
import sys
import pg2376_current_resume_owned_dispatch as previous
from pg2392_current_completed_runtime_retirement_sources import sources,SOURCE,SHA,TOOLS
from pg2380_current_resume_owned_post import payload as stopped_payload
from pg1446_current_cold_stage import W,P
from pg1674_critical_management_gate import management_gate
import pg1257_fresh_independent_terminal_post as schema

GUEST='/var/lib/pgpt-s1-preservation/'+TOOLS
REMOTE='/home/ubuntu/pg2394-fixed-stage-v1'
ARCHIVE='pg2394-'+TOOLS+'.tar'
STAGE=previous.STAGE.replace(previous.ARCHIVE,ARCHIVE).replace(previous.REMOTE,REMOTE).replace(previous.TOOLS,TOOLS).replace('pg2374','pg2392').replace('Pg2374','Pg2392').replace('pg2376','pg2394').replace('PG2376','PG2394')
PARENT_PREQUAL=previous.PARENT_PREQUAL.replace('pg2374','pg2392')
POST_SLOT='pg2380-current-resume-owned-post-v1'


def context():
    p=json.loads((W/POST_SLOT/'manifest.safe.json').read_bytes())
    if not(p['actualExit']==0 and p['productionSource']==SOURCE and p['allClientAdvisoryFlock0']and p['proofHashes']['after.private.json']['sha256']==SHA):raise ValueError('actual current stopped original image required')
    return SHA,None,p['genuineCompletion'],None


def post_payload():
    p=json.loads((W/POST_SLOT/'manifest.safe.json').read_bytes());b=json.loads((W/'pg2375-frozen-v1.safe.json').read_bytes())
    receipt=(W/previous.TOOLS/'pg2374_parent_receipt.py').read_text()
    seals={n:p['proofHashes'][n]['sha256']for n in schema.previous.SEALS}
    return 'HASHES='+repr(b['fileHashes'])+'\nRECEIPT='+repr(receipt)+'\n'+stopped_payload(seals)


def run_source():
    raw=previous.run_source().replace("('stage', 'stop')","('stage', 'retire')")
    raw=raw.replace("post['privateBeforeSha256'] != before","post['proofHashes']['after.private.json']['sha256'] != before")
    for a,z in [('pg2375','pg2393'),('pg2376','pg2394'),('pg2377','pg2395'),('pg2378','pg2396'),('Pg2374','Pg2392'),('Pg2392NativeStop stop','Pg2392NativeStop retire')]:raw=raw.replace(a,z)
    return raw


def run_action(action):
    base=previous.previous.prior.prior.prior.prior.runner
    ns={**base.__dict__,'GUEST':GUEST,'REMOTE':REMOTE,'ARCHIVE':ARCHIVE,'STAGE':STAGE,'PARENT_PREQUAL':PARENT_PREQUAL,'sources':sources,'context':context,'SOURCE':SOURCE,'TOOLS':TOOLS,'POST_SLOT':POST_SLOT,'post_payload':post_payload}
    exec(compile(run_source(),'<current exact one retirement dispatch>','exec'),ns);return ns['run_action'](action)


def main():
    if sys.argv[1:]not in (['stage'],['retire']):raise ValueError('distinct stage or retire only')
    os.umask(0o077)
    with management_gate(P/'current-management-critical.lock'):return run_action(sys.argv[1])


if __name__=='__main__':raise SystemExit(main())
