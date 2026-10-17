"""Fresh04bb ordinary Root once, original1800s budget, old72 are data only."""
import inspect
import datetime
import json
import pg4736_new_normal_root_once as previous
import pg4886_ssc301_302_publication_post as post
import pg4890_new_current_same_peer_observer as observer

W,P,SSH=previous.W,previous.P,previous.SSH
SLOT='pg4892-new-normal-root-once-v1'
SOURCE,BOM=observer.SOURCE,observer.BOM
QUALIFICATION='pg4896-new-normal-root-qualification-v1'


def oracle_applicable(proof,now,before_sha):
    if not(type(proof.get('actualExit'))is int and proof['actualExit']==0 and proof.get('source')==SOURCE):
        raise ValueError('actual current independent oracle preflight')
    result=proof.get('result',{});rows=result.get('projections',[])
    if not(result.get('beforeSha256')==before_sha and result.get('dbOrClockChanged')is False
           and result.get('rootStartIssued')is False and len(rows)==2
           and all(row.get('independentApplicability')is True for row in rows)):
        raise ValueError('same before/independent applicable window, no mutation')
    bounds=[datetime.datetime.fromisoformat(row['cutoff']) for row in rows]
    if not(all(x.tzinfo is not None for x in bounds) and bounds[0]<bounds[1] and bounds[0]<=now<=bounds[1]):
        raise ValueError('fresh oracle window, never backdated eligibility')


def action():
    raw=observer.bind(previous.action())
    for a,b in [(previous.SLOT,SLOT),('require(len(records)==64)','require(len(records)==72)')]:
        if raw.count(a)!=1:raise ValueError('one exact new ordinary once boundary '+a)
        raw=raw.replace(a,b,1)
    return raw


def payload(hashes):
    ns={**vars(previous),'post':post,'observer':observer,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,'action':action}
    exec(compile(inspect.getsource(previous.payload),'<all72 true normal Root once>','exec'),ns)
    return ns['payload'](hashes)


def main():
    from pg4888_new_current_readonly import context
    oracle_applicable(json.loads((W/'pg4898-current-query-oracle-preflight-v1/manifest.safe.json').read_bytes()),
                      datetime.datetime.now(datetime.timezone.utc),context())
    ns={**vars(previous),'post':post,'observer':observer,'SLOT':SLOT,'SOURCE':SOURCE,'BOM':BOM,
        'QUALIFICATION':QUALIFICATION,'payload':payload}
    raw=inspect.getsource(previous.main).replace('pg4730-new-current-readonly-v1','pg4888-new-current-readonly-v1').replace('pg4734','pg4890')
    exec(compile(raw,'<new04bb single ordinary Root entry>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
