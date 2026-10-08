"""Independent completed epoch/history and eight-to-seven retention bound."""
import ast
import datetime
import hashlib
import json
import pathlib
import re
import uuid
from pg626_fresh_parent_contract import skipped_cleanup_oracle


def completed_epoch(raw):
    if type(raw)is not bytes:return False
    try:
        lines=raw.decode('ascii').splitlines();keys=('state','boot_id','epoch_id','run_id','cutoff_utc','activation_id','permit_sha256')
        if len(lines)!=8 or lines[0]!='NKEPOCH1' or not raw.endswith(b'\n'):return False
        if any(not line.startswith(key+'=')for line,key in zip(lines[1:],keys)):return False
        v={key:line[len(key)+1:]for line,key in zip(lines[1:],keys)}
        epoch=uuid.UUID(v['epoch_id'])
        return (v['state']=='ISSUED'and epoch.version==4 and str(epoch)==v['epoch_id']
                and re.fullmatch('[0-9a-f]{64}',v['permit_sha256'])is not None
                and v['boot_id']=='cc9ed874-7f4f-450e-a188-8de1e42c8441'
                and v['run_id']=='e49243d5-de84-4714-8612-6912ddc17e9e'
                and v['cutoff_utc']=='2026-10-08T18:32:42.140966Z'
                and v['activation_id']=='7d381b67-b37b-48c6-99ac-e04a336f887d')
    except(ValueError,UnicodeError):return False


def prior_history(rows,day):
    if type(rows)is not list or len(rows)!=504 or day!='2026-10-09':return False
    if any(type(r)is not dict or not {'business_date','run_id','status','step','attempt'}<=set(r)for r in rows):return False
    today=[r for r in rows if r['business_date']==day]
    steps={'BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY'}
    prior=[r for r in today if r['run_id']=='3a53b979-fa01-47dd-92a6-7b26affcfb5c']
    current=[r for r in today if r['run_id']=='e49243d5-de84-4714-8612-6912ddc17e9e']
    original=[r for r in current if r['status']=='SUCCESS']
    skip=[r for r in current if r['status']=='SKIPPED']
    return (len(today)==22 and len(prior)==10 and {r['step']for r in prior}==steps and all(r['status']=='SUCCESS'for r in prior)
            and len(current)==12 and len(original)==2 and {r['step']for r in original}=={'BACKUP_DB','BACKUP_CONFIG'}
            and all(r['attempt']==2 for r in original)and len(skip)==10 and {r['step']for r in skip}==steps and all(r['attempt']==3 for r in skip))


def retention_upper(root,rows):
    source=(pathlib.Path(__file__).parent/'pg626_fresh_parent_contract.py').read_text()
    parsed=ast.parse(source);node=next(n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name=='retention_upper')
    raw=ast.get_source_segment(source,node)
    for old,new in (
        ('len(names)==12 and len(possible)==7','len(names)==13 and len(possible)==8'),
        ("'eligibleUpperBound':7","'eligibleUpperBound':8"),
        ("'maximumEligibleAfterNew':8","'maximumEligibleAfterNew':9"),
        ("'expectedRetentionDeletes':1","'expectedRetentionDeletes':2"),
        ("'expectedDeleted':[possible[0]]","'expectedDeleted':possible[:2]"),
    ):
        assert raw.count(old)==1;raw=raw.replace(old,new)
    env={'pathlib':pathlib,'re':re,'json':json,'datetime':datetime,'hashlib':hashlib}
    exec(compile(raw,'<independent success-pair retention selector>','exec'),env)
    return env['retention_upper'](root,rows)


__all__=['completed_epoch','prior_history','skipped_cleanup_oracle','retention_upper']
