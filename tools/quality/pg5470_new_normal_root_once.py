"""One fresh296 ordinary Root, original1800 budget; old88 are protected data, not authority."""
import datetime
import inspect
import json
import pg5022_new_normal_root_once as previous
import pg5460_ownership_publication_post as post
import pg5466_new_current_same_peer_observer as observer
import pg5464_new_current_readonly as current
import pg5468_new_day_query_preflight as oracle
from pg4996_resume_connection import authenticate_host

W,P,SSH=previous.W,previous.P,previous.SSH
SLOT='pg5470-new-normal-root-once-v1'
SOURCE,BOM=observer.SOURCE,observer.BOM
QUALIFICATION='pg5474-ownership-normal-root-qualification-v1'


def oracle_applicable(proof,now,before_sha):
    ns={**vars(previous.previous),'SOURCE':SOURCE}
    exec(compile(inspect.getsource(previous.previous.oracle_applicable),'<same independent source/window applicability>','exec'),ns)
    return ns['oracle_applicable'](proof,now,before_sha)


def action():
    raw=observer.bind(previous.action())
    for before,after in((previous.SLOT,SLOT),('require(len(records)==80)','require(len(records)==88)')):
        if raw.count(before)!=1:raise ValueError('one fresh296 ordinary-once boundary '+before)
        raw=raw.replace(before,after,1)
    return raw


def payload(hashes):
    template=previous.previous.previous
    ns={**vars(template),'post':post,'observer':observer,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'action':action}
    exec(compile(inspect.getsource(template.payload),'<all88 preserved normal296 Root once>','exec'),ns)
    return ns['payload'](hashes)


def main():
    oracle_applicable(json.loads((W/oracle.SLOT/'manifest.safe.json').read_bytes()),datetime.datetime.now(datetime.timezone.utc),current.context())
    template=previous.previous.previous
    ns={**vars(template),'post':post,'observer':observer,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,
        'QUALIFICATION':QUALIFICATION,'payload':payload,'authenticate_host':authenticate_host}
    raw=inspect.getsource(template.main).replace('pg4730-new-current-readonly-v1',current.SLOT).replace('pg4734','pg5466')
    exec(compile(raw,'<one fresh296 noargs ordinary Root>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
