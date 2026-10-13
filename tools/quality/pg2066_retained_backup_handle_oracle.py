"""Independent retained manifest handle selection with approved later skip history."""
import inspect
import pg1259_fresh_backup_manifest_oracle as historical


def retained_handle(rows,run,step,handle,finish):
    require(type(rows)is list and all(type(row)is dict for row in rows))
    same=[row for row in rows if row.get('run_id')==run and row.get('step')==step]
    selected=[row for row in same if row.get('id')==handle['id']and row.get('attempt')==handle['attempt']]
    require(len(selected)==1)
    row=selected[0];ids=set();attempts=set()
    for extra in same:
        require(type(extra.get('id'))is int and extra['id']>0 and extra['id']not in ids)
        require(type(extra.get('attempt'))is int and extra['attempt']>0 and extra['attempt']not in attempts)
        ids.add(extra['id']);attempts.add(extra['attempt'])
        if extra is row:continue
        require(extra['attempt']>handle['attempt']and extra['business_date']==row['business_date'])
        require(extra['status']=='SKIPPED'and extra['error_code']=='ALREADY_SUCCESSFUL'and extra['error_summary']=='step already successful for business date')
        require(all(type(extra[k])is int and extra[k]==0 for k in ['target_count','success_count','failure_count','byte_count']))
        require(extra['started_at']==extra['ended_at']and utc6(extra['started_at'].replace('+00:00','Z'))>=finish)
    return row


require=historical.require
utc6=historical.utc6


def source():
    raw=inspect.getsource(historical)
    old="matched=[row for row in rows if row['run_id']==run and row['step']==step]\n        require(len(matched)==1);row=matched[0]"
    if raw.count(old)!=1:raise ValueError('one historical same-run-step selection required')
    raw=raw.replace(old,'row=retained_handle(rows,run,step,handle,finish)')
    raw+='\n'+inspect.getsource(retained_handle)
    compile(raw,'<independent retained Backup handle oracle>','exec');return raw
