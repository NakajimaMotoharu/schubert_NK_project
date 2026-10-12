"""Current2741 native eight; all old4d6 fourteen bytes preserved, never imported."""
import ast
import inspect
import re
import pg1616_current_ordinary_native_catalog_v2 as prior
from pg1703_new_source_owned_stop_sources import bind,context,SOURCE

ROOT_START=66941284515
ROOT_END=68542820690


def backup_window(rows):
    def require(v):
        if not v:raise ValueError('independent sameRoot Backup journal refused')
    require(type(rows)is list and bool(rows))
    fixed={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0',
           '_COMM':'systemd','UNIT':'schubert-nk-backup.service'}
    invocations=set();cursors=set()
    for row in rows:
        require(type(row)is dict and all(row.get(k)==v for k,v in fixed.items()))
        require(type(row.get('INVOCATION_ID'))is str and re.fullmatch('[a-f0-9]{32}',row['INVOCATION_ID'])is not None)
        invocations.add(row['INVOCATION_ID']);cursor=row.get('__CURSOR');stamp=row.get('__MONOTONIC_TIMESTAMP')
        require(type(cursor)is str and bool(cursor)and cursor not in cursors);cursors.add(cursor)
        require(type(stamp)is str and stamp.isdigit()and ROOT_START<=int(stamp)<=ROOT_END)
        require(type(row.get('__REALTIME_TIMESTAMP'))is str and row['__REALTIME_TIMESTAMP'].isdigit())
        require(row.get('JOB_RESULT')in(None,'done'))
    require(len(invocations)==1)
    start=[r for r in rows if r.get('MESSAGE_ID')=='7d4958e842da4a758f6c1cdc7b36dcc5'and r.get('JOB_TYPE')=='start']
    done=[r for r in rows if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='done']
    success=[r for r in rows if r.get('MESSAGE_ID')=='7ad2d189f7e94e70a38c781354912448']
    stop=[r for r in rows if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done']
    require(len(start)==len(done)==len(success)==len(stop)==1)
    job=start[0].get('JOB_ID');stopjob=stop[0].get('JOB_ID')
    require(type(job)is str and job.isdigit()and int(job)>0 and done[0].get('JOB_ID')==job)
    require(type(stopjob)is str and stopjob.isdigit()and int(stopjob)>0 and stopjob!=job)
    times=[int(g[0]['__MONOTONIC_TIMESTAMP'])for g in [start,done,success,stop]]
    require(times==sorted(times))
    return times[0],times[2]


def catalog_source():
    _,_,done,_=context()
    raw=bind(prior.catalog_source())
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='backup_window')
    lines=raw.splitlines(keepends=True)
    raw=''.join(lines[:node.lineno-1])+inspect.getsource(backup_window)+''.join(lines[node.end_lineno:])
    raw='ROOT_START=66941284515\nROOT_END='+str(done['endMonotonicUs'])+'\n'+raw
    raw=raw.replace("'INVOCATION_ID=1c085a5e6e874ba1b0d647c92ab3c34c',",'')
    marker="backup_rows=[json.loads(line)for line in backup_raw.splitlines()];backup_start,backup_end=backup_window(backup_rows)"
    if raw.count(marker)!=1:raise ValueError('one independent current Backup journal filter required')
    raw=raw.replace(marker,"backup_rows=[json.loads(line)for line in backup_raw.splitlines()];backup_rows=[r for r in backup_rows if ROOT_START<=int(r['__MONOTONIC_TIMESTAMP'])<=ROOT_END];backup_start,backup_end=backup_window(backup_rows)")
    raw=raw.replace('pg1600-current-ordinary-once-v2','pg1699-new-current-ordinary-once-v1')
    raw=raw.replace('len(old)==10','len(old)==14').replace('oldTenArchiveUnchanged','oldFourteenArchiveUnchanged')
    # Preserve every old path/hash; exclude exactly its non-overwritten histories.
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.Expr)
              and isinstance(n.value,ast.Call)and ast.unparse(n).startswith('require(set(excluded) =='))
    lines=raw.splitlines(keepends=True)
    raw=''.join(lines[:node.lineno-1])+"require(set(excluded)==set(old)-{v['relative']for v in selected})\n"+''.join(lines[node.end_lineno:])
    compile(raw,'<actual current native eight with preserved old fourteen>','exec')
    return raw


def main():
    raw=inspect.getsource(prior.prior.prior.prior.prior.main)
    raw=raw.replace('pg1584-current-native-catalog-v1','pg1708-new-source-native-catalog-v1')
    raw=raw.replace('pg1583-current-terminal-post-v1','pg1707-new-source-terminal-post-v1')
    ns={**prior.prior.prior.prior.prior.__dict__,'CODE':catalog_source(),'SOURCE':SOURCE}
    exec(compile(raw,'<sameSource native catalog readonly transport>','exec'),ns)
    return ns['main']()


if __name__=='__main__':raise SystemExit(main())
