"""Independent SS324/331/341 new-JST-day row oracle; expected values from BEFORE only."""
import datetime
import inspect
from pg1196_completed_rows_oracle import require,instant,BATCH
from pg478_cleanup_oracle import candidates
import pg1769_next_day_rows_oracle as original
import pg2078_current_same_day_rows_oracle as common
from pg2814_network_newboot_readonly import one


def expected_inbox(rows,expected):
    selected=set(expected['inbox_scan_candidates'])
    found={r['message_id']:r for r in rows['schubert.request_inbox']if r['message_id']in selected}
    require(set(found)==selected)
    removed=set(expected['auth_sessions'])
    remaining={str(r['id'])for r in rows['schubert.auth_sessions']if str(r['id'])not in removed}
    for row in found.values():
        require((row['request_layout_id'],row['response_layout_id'],row['processing_state'],row['result_ref_type'],row['owner_user_id'])==('LGNREQ01','LGNRSP01','COMPLETED','AUTH_SESSION',None))
        require(row['result_ref_uuid']is not None and str(row['result_ref_uuid'])not in remaining)
    return {'deleted':[],'protected':sorted(selected),'basis':'SS341 session cleanup precedes SS324 12.2 immutable AUTH_SESSION inspection; absent after independently planned deletion'}


def qualify_current(before,now,run,cutoff,upper):
    require(type(before)is dict and type(now)is dict and set(before)==set(now)and len(before)==24)
    start,end=instant(cutoff),instant(upper);require(start is not None and end is not None and start<end)
    day=start.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
    require(not any(row['business_date']==day for row in before[BATCH]))
    expected=candidates(before,cutoff)
    oracle={'expected':expected,'expectedInbox':expected_inbox(before,expected)}
    return qualify_new_day(before,now,oracle,run,cutoff,upper)


def source():
    # Existing independently tested all24 delta/HTTP structure, not Production.
    raw=original.oracle_source();node=inspect.getsource(original.qualify)
    updated=node.replace('def qualify(','def qualify_new_day(',1)
    updated=one(updated,"expected=oracle['expected'];inbox=oracle['expectedInbox'];removed={}","expected=oracle['expected'];inbox=oracle['expectedInbox'];removed={}\n    day=start.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()")
    updated=one(updated,"r['business_date']=='2026-10-13'","r['business_date']==day")
    updated=one(updated,"['notifications','questions','app_logs'","['questions','app_logs'")
    updated=one(updated,"targets={'CLEAN_SESSION':session_count,","targets={'CLEAN_NOTIFICATION':len(expected['notifications']),'CLEAN_SESSION':session_count,")
    updated=one(updated,"successes={'CLEAN_SESSION':session_count,","successes={'CLEAN_NOTIFICATION':len(expected['notifications']),'CLEAN_SESSION':session_count,")
    updated=one(updated,'    for r in batch:',"    maximum=max((r['id']for r in before[BATCH]),default=0);newids=set()\n    for r in batch:\n        require(type(r['id'])is int and r['id']>maximum and r['id']not in newids);newids.add(r['id'])")
    raw=one(raw,node,updated)
    selectors=common.source();start=selectors.index('_selectors=');end=selectors.index('def classify_inbox(',start)
    raw+='\n'+selectors[start:end]+'\n'+inspect.getsource(expected_inbox)+'\n'+inspect.getsource(qualify_current)
    return raw


def namespace():
    ns={};exec(compile(source(),'<independent new day full24 oracle>','exec'),ns);return ns


def qualify_new_day(before,now,oracle,run,cutoff,upper):return namespace()['qualify_new_day'](before,now,oracle,run,cutoff,upper)


def qualify(before,now,run,cutoff,upper):return namespace()['qualify_current'](before,now,run,cutoff,upper)
