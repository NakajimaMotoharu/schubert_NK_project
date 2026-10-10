"""Independent SS341/V013 fresh-day session deletion and unchanged-row oracle.

No Production method or SQL execution; whole Backup/HTTP/step oracle separate.
"""
import datetime
import json

def require(value):
    if not value:
        raise ValueError('fresh-day independent row postcondition refused')

def instant(value):
    require(type(value) is str)
    v = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(v.tzinfo is not None)
    return v

def deleted_sessions(table, rows, cutoff):
    require(type(rows) is list and isinstance(cutoff, datetime.datetime) and cutoff.tzinfo is not None)
    limit = cutoff - datetime.timedelta(hours=24)
    selected = []
    for row in rows:
        require(type(row) is dict)
        if table == 'schubert.auth_sessions':
            require(type(row.get('revoked')) is bool)
            wanted = instant(row['expires_at']) <= limit or (row['revoked'] and row['revoked_at'] is not None and instant(row['revoked_at']) <= limit)
        elif table == 'schubert.login_ip_attempts':
            end = instant(row['window_started_at']) + datetime.timedelta(minutes=15)
            if row['locked_until'] is not None:
                end = max(end, instant(row['locked_until']))
            wanted = end <= limit
        elif table == 'schubert_web_session.web_http_sessions':
            wanted = instant(row['expires_at']) <= cutoff
        else:
            raise ValueError('unknown session cleanup table')
        if wanted:
            selected.append(row)
    return selected

def session_post(old, new, cutoff):
    require(type(old) is dict and type(new) is dict and set(old) == set(new) and len(old) == 24)
    session_tables = {'schubert.auth_sessions','schubert.login_ip_attempts','schubert_web_session.web_http_sessions'}
    variable = session_tables | {'schubert.batch_runs','schubert.app_logs','schubert_web_session.web_log_outbox','schubert.inbox_inspection_progress','schubert.log_cleanup_progress'}
    require(variable <= set(old))
    counts = {}
    additions = {}
    seal = lambda row: json.dumps(row,sort_keys=True,separators=(',',':'))
    for table, rows in old.items():
        require(type(rows) is list and type(new[table]) is list and all(type(v) is dict for v in rows + new[table]))
        a, b = [seal(v) for v in rows], [seal(v) for v in new[table]]
        require(len(set(a)) == len(a) and len(set(b)) == len(b))
        expected = deleted_sessions(table,rows,cutoff) if table in session_tables else []
        removed = [v for v,key in zip(rows,a) if key not in set(b)]
        require(removed == expected)
        counts[table] = len(removed)
        additions[table] = [v for v,key in zip(new[table],b) if key not in set(a)]
        if table not in variable or table in session_tables - {'schubert_web_session.web_http_sessions'}:
            require(not additions[table])
    return {'expectedSessionDeletes':sum(counts[t] for t in session_tables),'removedByTable':counts,'addedByTable':{t:len(v) for t,v in additions.items()},'unrelatedRowsUnchanged':True,'businessFullAccepted':False}

def zero_progress_post(old,new,cutoff,run,upper):
    """SS331/341/V012/V014 zero-eligible fixture only; no inferred oracle."""
    require(not [r for r in old['schubert.app_logs'] if instant(r['logged_at']) < cutoff-datetime.timedelta(hours=2160)])
    require(not [r for r in old['schubert.request_inbox'] if r['processing_state'] in {'COMPLETED','ERROR'} and instant(r['expires_at']) < cutoff])
    result={}
    for table,counters,cursors in [('schubert.log_cleanup_progress',['target_count','deleted_count','skipped_count'],['after_logged_at','after_id']),('schubert.inbox_inspection_progress',['inspected_count','deleted_count','protected_count'],['after_message_id'])]:
        before=old[table];after=new[table]
        require(all(r in after for r in before))
        added=[r for r in after if r not in before]
        require(len(added)==1)
        row=added[0]
        require(set(row)=={'run_id','cutoff','completed_at'}|set(counters)|set(cursors))
        require(row['run_id']==run and instant(row['cutoff'])==cutoff and cutoff<=instant(row['completed_at'])<=upper)
        require(all(type(row[k])is int and row[k]==0 for k in counters) and all(row[k]is None for k in cursors))
        result[table]={'added':1,'independentEligible':0,'counts':[0,0,0],'completed':True}
    return result
