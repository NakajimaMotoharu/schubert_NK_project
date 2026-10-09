"""Fixed PG760-to-PG758-end finite append contract; full24 equality after newcapture."""
import json

APPENDS={'schubert.app_logs':56,'schubert_web_session.web_http_sessions':55,'schubert_web_session.web_log_outbox':56}


def preserved(before,after):
    if not isinstance(before,dict)or not isinstance(after,dict)or len(before)!=24 or set(before)!=set(after):return False
    for table,old in before.items():
        new=after[table]
        if not isinstance(old,list)or not isinstance(new,list):return False
        if table not in APPENDS:
            if old!=new:return False
            continue
        def indexed(rows):
            result={}
            for row in rows:
                if not isinstance(row,dict)or row.get('id')is None:return None
                key=json.dumps(row['id'],sort_keys=True)
                if key in result:return None
                result[key]=row
            return result
        a,b=indexed(old),indexed(new)
        if a is None or b is None or len(b)!=len(a)+APPENDS[table]or any(k not in b or v!=b[k]for k,v in a.items()):return False
    return True
