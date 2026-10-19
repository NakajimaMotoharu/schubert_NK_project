"""One fresh0ea ordinary Root/original1800s; prior94 are data, not authority."""
import datetime
import inspect
import json
import pg5470_new_normal_root_once as previous
import pg5630_current_publication_post as post
import pg5634_new_current_same_peer_observer as observer
import pg5632_new_current_readonly as current
import pg5636_new_day_query_preflight as oracle
from pg4996_resume_connection import authenticate_host

W,P,SSH=previous.W,previous.P,previous.SSH
SLOT='pg5638-new-normal-root-once-v1'
SOURCE,BOM=observer.SOURCE,observer.BOM
QUALIFICATION='pg5642-current-normal-root-qualification-v3'


def oracle_applicable(proof,now,before_sha):
    ns={**vars(previous.previous.previous),'SOURCE':SOURCE}
    exec(compile(inspect.getsource(previous.previous.previous.oracle_applicable),'<independent source/window applicability>','exec'),ns)
    ns['oracle_applicable'](proof,now,before_sha)
    upper=datetime.datetime.fromisoformat(proof['result']['projections'][1]['cutoff'])
    if now+datetime.timedelta(seconds=1800)>upper:raise ValueError('full original Root budget must fit independent window')


def action():
    raw=observer.bind(previous.action())
    for before,after in((previous.SLOT,SLOT),('require(len(records)==88)','require(len(records)==94)')):
        if raw.count(before)!=1:raise ValueError('one fresh0ea ordinary-once boundary '+before)
        raw=raw.replace(before,after,1)
    return raw


def payload(hashes):
    template=previous.previous.previous.previous
    ns={**vars(template),'post':post,'observer':observer,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'action':action}
    exec(compile(inspect.getsource(template.payload),'<all94 preserved normal0ea Root once>','exec'),ns)
    return ns['payload'](hashes)


def main():
    oracle_applicable(json.loads((W/oracle.SLOT/'manifest.safe.json').read_bytes()),datetime.datetime.now(datetime.timezone.utc),current.context())
    template=previous.previous.previous.previous
    ns={**vars(template),'post':post,'observer':observer,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,
      'QUALIFICATION':QUALIFICATION,'payload':payload,'authenticate_host':authenticate_host}
    raw=inspect.getsource(template.main).replace('pg4730-new-current-readonly-v1',current.SLOT).replace('pg4734','pg5634')
    exec(compile(raw,'<one fresh0ea noargs ordinary Root>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
