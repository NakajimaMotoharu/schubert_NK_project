"""Independent INVALID8633, exact42 history and current seven Backup retention."""
import datetime
import hashlib
import json
import pathlib
import re
import uuid

STEPS = {'BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION',
         'CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY'}


def invalid_epoch(raw):
    if type(raw) is not bytes:
        return False
    try:
        keys = ('state','boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256')
        lines = raw.decode('ascii').splitlines()
        if len(lines) != 8 or lines[0] != 'NKEPOCH1' or not raw.endswith(b'\n'):
            return False
        if any(not line.startswith(key+'=') for line, key in zip(lines[1:], keys)):
            return False
        v = {key: line[len(key)+1:] for line, key in zip(lines[1:], keys)}
        u = uuid.UUID(v['epoch_id'])
        return (v['state']=='INVALID' and v['permit_sha256']=='-' and u.version==4 and str(u)==v['epoch_id']
                and v['boot_id']=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
                and v['run_id']=='55ac70e7-0180-4c32-8c91-5a379ebedf24'
                and v['cutoff_utc']=='2026-10-09T03:00:51.014287Z'
                and v['activation_id']=='ab8895ca-4fb1-440d-b174-bc9f1f27505a')
    except (ValueError, UnicodeError):
        return False


def previous_prior_history(rows, day):
    if type(rows) is not list or len(rows)!=524 or day!='2026-10-09':
        return False
    if any(type(r) is not dict or not {'business_date','run_id','status','step','attempt'}<=set(r) for r in rows):
        return False
    last = [r for r in rows if r['run_id']=='8633b77f-77dc-4a78-88b4-41165f159b43']
    older = [r for r in rows if r['run_id']!='8633b77f-77dc-4a78-88b4-41165f159b43']
    return (previous_history(older,day) and len(last)==10 and {r['step'] for r in last}==STEPS
            and len([r for r in rows if r['business_date']==day])==42
            and all(r['business_date']==day and r['status']==('SUCCESS' if r['step'] in {'BACKUP_DB','BACKUP_CONFIG'} else 'SKIPPED')
                    and r['attempt']==(5 if r['step'] in {'BACKUP_DB','BACKUP_CONFIG'} else 4) for r in last))


def retention_upper(root, rows):
    assert isinstance(root,pathlib.Path) and root.is_dir() and not root.is_symlink()
    names = []; possible = []; protected = []; by_id = {r['id']:r for r in rows['schubert.batch_runs']}
    for p in sorted(root.iterdir()):
        names.append(p.name)
        if not re.fullmatch(r'[0-9]{8}-[0-9]{6}-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',p.name) or p.is_symlink() or not p.is_dir():
            protected.append(p.name); continue
        if {f.name for f in p.iterdir()}!={'MANIFEST.json','config.tar','credentials.tar.age','schubert_nk.dump'}:
            protected.append(p.name); continue
        m = json.loads((p/'MANIFEST.json').read_bytes())
        claims = [m['databaseStep'],m['configurationStep']]; found = [by_id.get(c['id']) for c in claims]
        assert set(m['files'])=={'schubert_nk.dump','config.tar','credentials.tar.age'}
        if any(r is None or r['status']!='SUCCESS' for r in found):
            protected.append(p.name); continue
        assert len({r['id'] for r in found})==2 and {r['step'] for r in found}=={'BACKUP_DB','BACKUP_CONFIG'}
        assert all(r['run_id']==m['runId'] and r['attempt']==c['attempt'] and datetime.datetime.fromisoformat(r['started_at'].replace('Z','+00:00'))==datetime.datetime.fromisoformat(c['startedAt'].replace('Z','+00:00')) for r,c in zip(found,claims))
        assert all(not (p/n).is_symlink() and (p/n).is_file() and (p/n).stat().st_size==c['size'] and hashlib.sha256((p/n).read_bytes()).hexdigest()==c['sha256'] for n,c in m['files'].items())
        possible.append(p.name)
    assert len(names)==12 and len(possible)==7 and len(protected)==5
    assert possible[0]=='20261008-130310-b7e73994-b951-4696-bdd1-cfbc8a10e734'
    return {'oldNames':names,'eligibleUpperBound':7,'protectedLowerBound':5,'protectedNames':protected,
            'maximumEligibleAfterNew':8,'retentionLimit':7,'expectedRetentionDeletes':1,
            'expectedDeleted':[possible[0]],'independentPostVerificationRequired':True}


def previous_history(rows,day):
    if type(rows)is not list or len(rows)!=514 or day!='2026-10-09':return False
    if any(type(r)is not dict or not {'business_date','run_id','status','step','attempt'}<=set(r)for r in rows):return False
    today=[r for r in rows if r['business_date']==day]
    prior=[r for r in today if r['run_id']=='3a53b979-fa01-47dd-92a6-7b26affcfb5c']
    mid=[r for r in today if r['run_id']=='e49243d5-de84-4714-8612-6912ddc17e9e']
    last=[r for r in today if r['run_id']=='601297d0-a8ba-47da-852b-0ffeae409965']
    backups={'BACKUP_DB','BACKUP_CONFIG'}
    return (len(today)==32 and len(prior)==10 and {r['step']for r in prior}==STEPS
            and all(r['status']=='SUCCESS'and r['attempt']==1 for r in prior)
            and len(mid)==12 and {r['step']for r in mid}==STEPS
            and {r['step']for r in mid if r['status']=='SUCCESS'}==backups
            and {r['step']for r in mid if r['status']=='SKIPPED'}==STEPS
            and len([r for r in mid if r['status']=='SUCCESS'and r['step']in backups and r['attempt']==2])==2
            and len([r for r in mid if r['status']=='SKIPPED'and r['attempt']==(3 if r['step']in backups else 2)])==10
            and len(last)==10 and {r['step']for r in last}==STEPS
            and all(r['status']==('SUCCESS'if r['step']in backups else'SKIPPED')
                    and r['attempt']==(4 if r['step']in backups else 3)for r in last))


def skipped_cleanup_oracle(low,high):
    categories={'notifications','questions','auth_sessions','login_ip_attempts','web_http_sessions','schubert.mq_outbox','schubert_web_session.web_log_outbox','app_logs','batch_runs','schubert.inbox_inspection_progress','schubert.log_cleanup_progress','web_receipt_references','inbox_scan_candidates'}
    return (type(low)is dict and type(high)is dict and set(low)==set(high)==categories and low==high
            and all(type(v)is list and all(e is not None for e in v)for v in low.values()))


def prior_history(rows, day):
    # Independent literal next cohort: old524/42 unchanged + ten55ac ->534/52.
    if type(rows) is not list or len(rows)!=534 or day!='2026-10-09':return False
    if any(type(r)is not dict or not {'business_date','run_id','status','step','attempt'}<=set(r)for r in rows):return False
    last=[r for r in rows if r['run_id']=='55ac70e7-0180-4c32-8c91-5a379ebedf24']
    older=[r for r in rows if r['run_id']!='55ac70e7-0180-4c32-8c91-5a379ebedf24']
    return (previous_prior_history(older,day) and len(last)==10 and {r['step']for r in last}==STEPS
        and len([r for r in rows if r['business_date']==day])==52
        and all(r['business_date']==day and r['status']==('SUCCESS'if r['step']in {'BACKUP_DB','BACKUP_CONFIG'}else'SKIPPED')
                and r['attempt']==(6 if r['step']in {'BACKUP_DB','BACKUP_CONFIG'}else 5)for r in last))
