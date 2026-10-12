"""SS341: fresh Backup pair plus eight same-day skip rows; bundle oracle separate."""
from pg1602_current_newrun_rows_oracle import source as previous

def source():
    raw=previous()
    old="    for row in batch:\n        require(row['run_id']==run"
    new="""    for row in batch:
        if row['step'] in {'BACKUP_DB','BACKUP_CONFIG'}:
            count=1 if row['step']=='BACKUP_DB' else 2
            require(row['run_id']==run and row['business_date']=='2026-10-12' and row['status']=='SUCCESS' and row['error_code'] is None and row['error_summary'] is None)
            require(all(type(row[k]) is int for k in ['target_count','success_count','failure_count','byte_count']))
            require(row['target_count']==row['success_count']==count and row['failure_count']==0 and row['byte_count']>0)
            require(start<=instant(row['started_at'])<=instant(row['ended_at'])<=end)
            continue
        require(row['run_id']==run"""
    if raw.count(old)!=1:raise ValueError('ordinary Backup-pair oracle boundary refused')
    raw=raw.replace(old,new).replace("'newSkippedSteps':10","'newSkippedSteps':8,'freshBackupSuccessSteps':2,'backupBundleByteOraclePending':True")
    raw=raw.replace("sum(r['status']=='SUCCESS'for r in baseline)!=1","row['step'] not in {'BACKUP_DB','BACKUP_CONFIG'} and sum(r['status']=='SUCCESS'for r in baseline)!=1")
    compile(raw,'<independent ordinary new-run rows>','exec');return raw

def qualify(old,new,lower,upper):
    env={};exec(compile(source(),'<independent ordinary new-run rows>','exec'),env)
    return env['qualify'](old,new,lower,upper)
