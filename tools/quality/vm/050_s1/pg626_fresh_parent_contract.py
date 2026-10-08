"""SS341/343 same-day ordinary fresh run, never completed-run resume."""
import datetime
import hashlib
import json
import pathlib
import re
import uuid

STEPS={'BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY'}


def invalid_epoch(raw):
    if type(raw)is not bytes:return False
    try:
        lines=raw.decode('ascii').splitlines()
        keys=('state','boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256')
        if len(lines)!=8 or lines[0]!='NKEPOCH1'or not raw.endswith(b'\n'):return False
        if any(not row.startswith(key+'=')for row,key in zip(lines[1:],keys)):return False
        v={key:row[len(key)+1:]for row,key in zip(lines[1:],keys)}
        identifier=uuid.UUID(v['epoch_id'])
        return (v['state']=='INVALID'and v['permit_sha256']=='-'and identifier.version==4
                and str(identifier)==v['epoch_id']and v['boot_id']=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
                and v['run_id']=='3a53b979-fa01-47dd-92a6-7b26affcfb5c'
                and v['cutoff_utc']=='2026-10-08T15:32:46.368375Z'
                and v['activation_id']=='970bbce1-6bba-4db0-ace1-680ee7dfde92')
    except(ValueError,UnicodeError):return False


def prior_history(rows,day):
    if type(rows)is not list or len(rows)!=492 or day!='2026-10-09':return False
    if any(type(r)is not dict or not {'business_date','run_id','status','step'}<=set(r)for r in rows):return False
    today=[r for r in rows if r['business_date']==day]
    return (len(today)==10 and {r['step']for r in today}==STEPS
            and all(r['run_id']=='3a53b979-fa01-47dd-92a6-7b26affcfb5c'and r['status']=='SUCCESS'for r in today))


def skipped_cleanup_oracle(low,high):
    categories={'notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references','inbox_scan_candidates'}
    return (type(low)is dict and type(high)is dict and set(low)==set(high)==categories and low==high
            and all(type(v)is list and all(e is not None for e in v)for v in low.values()))


def retention_upper(root,rows):
    """Content/DB pair upper bound; unverified bundles remain protected.

    Counts eligible possibilities conservatively; expected retention selection is
    independently confirmed after the actual run. All original bytes must first
    be preserved privately; a rejected proof never permits deleting arbitrary files.
    """
    assert isinstance(root,pathlib.Path)and root.is_dir()and not root.is_symlink()
    names=[];possible=[];protected=[]
    by_id={r['id']:r for r in rows['schubert.batch_runs']}
    for p in sorted(root.iterdir()):
        names.append(p.name)
        if not re.fullmatch(r'[0-9]{8}-[0-9]{6}-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',p.name)or p.is_symlink()or not p.is_dir():protected.append(p.name);continue
        if {f.name for f in p.iterdir()}!={'MANIFEST.json','config.tar','credentials.tar.age','schubert_nk.dump'}:protected.append(p.name);continue
        m=json.loads((p/'MANIFEST.json').read_bytes())
        claims=[m['databaseStep'],m['configurationStep']]
        found=[by_id.get(c['id'])for c in claims]
        if any(r is None or r['status']!='SUCCESS'for r in found):protected.append(p.name);continue
        assert len({r['id']for r in found})==2 and {r['step']for r in found}=={'BACKUP_DB','BACKUP_CONFIG'}
        assert all(r['run_id']==m['runId']and r['attempt']==c['attempt']and datetime.datetime.fromisoformat(r['started_at'].replace('Z','+00:00'))==datetime.datetime.fromisoformat(c['startedAt'].replace('Z','+00:00'))for r,c in zip(found,claims))
        assert all(not (p/n).is_symlink()and (p/n).is_file()and (p/n).stat().st_size==c['size']and hashlib.sha256((p/n).read_bytes()).hexdigest()==c['sha256']for n,c in m['files'].items())
        possible.append(p.name)
    assert len(names)==12 and len(possible)==7 and len(protected)==5
    assert possible[0]=='20260930-120030-31100027-2222-4333-8444-555555555555'
    return {'oldNames':names,'eligibleUpperBound':7,'protectedLowerBound':5,'protectedNames':protected,'maximumEligibleAfterNew':8,'retentionLimit':7,'expectedRetentionDeletes':1,'expectedDeleted':[possible[0]],'independentPostVerificationRequired':True}
