"""Strict old-column preservation; explicitly observed new rows are NOT business acceptance."""
import json

APPEND_ONLY={'schubert.batch_runs','schubert_web_session.web_http_sessions','schubert.app_logs','schubert_web_session.web_log_outbox'}


def survivors_preserved(old,current):
    if type(old)is not dict or type(current)is not dict or set(old)!=set(current)or len(old)!=24:raise ValueError('all24 required')
    observed={}
    for table,rows in old.items():
        if type(rows)is not list or type(current[table])is not list:raise ValueError('rows required')
        def canonical(items):
            if any(type(r)is not dict or not r for r in items):raise ValueError('row schema invalid')
            values=[json.dumps(r,sort_keys=True,separators=(',',':'))for r in items]
            if len(values)!=len(set(values)):raise ValueError('duplicate row')
            return set(values)
        previous=canonical(rows);now=canonical(current[table])
        if table in APPEND_ONLY:
            ids=[r.get('id')for r in current[table]]
            if any(type(v)not in(int,str)or not v for v in ids)or len({str(v)for v in ids})!=len(ids):raise ValueError('append primary id invalid or duplicate')
        if not previous<=now or (table not in APPEND_ONLY and previous!=now):raise ValueError('old survivor changed or foreign append')
        if now!=previous:observed[table]={'addedObserved':len(now-previous),'newRowsAccepted':False}
    return observed
