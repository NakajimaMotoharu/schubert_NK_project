"""Literal current prior-run fixture guards; no operations or production expected generator."""
def prior_history(rows, day):
    if type(rows) is not list or len(rows) != 472 or type(day) is not str: return False
    if any(type(r) is not dict or not {'business_date', 'run_id', 'status'} <= set(r) for r in rows): return False
    today = [r for r in rows if r['business_date'] == day]
    return len(today) == 10 and {r['run_id'] for r in today} == {'b7e73994-b951-4696-bdd1-cfbc8a10e734'} and all(r['status'] == 'SUCCESS' for r in today)


def empty_oracle(low, high):
    categories={'notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references','inbox_scan_candidates'}
    if type(low) is not dict or type(high) is not dict or set(low)!=categories or low!=high: return False
    if any(type(v) is not list for v in low.values()): return False
    sessions=low['web_http_sessions']
    return len(sessions)==115 and all(type(v)is str and bool(v)for v in sessions) and len(set(sessions))==115 and all(v==[]for k,v in low.items()if k!='web_http_sessions')
