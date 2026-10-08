"""Literal current prior-run fixture guards; no operations or production expected generator."""
import uuid


def invalid_epoch(raw):
    if type(raw) is not bytes: return False
    try:
        rows = raw.decode('ascii').split('\n')
        keys = ('state','boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256')
        if len(rows) != 9 or rows[0] != 'NKEPOCH1' or rows[-1] != '': return False
        if any(not row.startswith(key+'=') for row,key in zip(rows[1:-1],keys)): return False
        v = {key:row[len(key)+1:] for row,key in zip(rows[1:-1],keys)}
        identifier = uuid.UUID(v['epoch_id'])
        return (v['state']=='INVALID' and v['permit_sha256']=='-' and identifier.version==4
                and str(identifier)==v['epoch_id'] and v['boot_id']=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
                and v['run_id']=='b62b6984-ffc2-4c9d-aea9-e232d9d1ec9e'
                and v['cutoff_utc']=='2026-10-08T07:36:21.802335Z'
                and v['activation_id']=='57f0e73d-d334-4882-9284-04246011da54')
    except (ValueError, UnicodeError): return False


def prior_history(rows, day):
    if type(rows) is not list or len(rows) != 482 or day != '2026-10-09': return False
    if any(type(r) is not dict or not {'business_date', 'run_id', 'status'} <= set(r) for r in rows): return False
    today = [r for r in rows if r['business_date'] == day]
    return not today


def empty_oracle(low, high):
    categories={'notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references','inbox_scan_candidates'}
    if type(low) is not dict or type(high) is not dict or set(low)!=categories or low!=high: return False
    if any(type(v) is not list for v in low.values()): return False
    sessions=low['web_http_sessions']
    return len(sessions)==229 and all(type(v)is str and bool(v)for v in sessions) and len(set(sessions))==229 and all(v==[]for k,v in low.items()if k!='web_http_sessions')
