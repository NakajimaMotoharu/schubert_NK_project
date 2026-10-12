"""BUG1131: current Backup is proven by PID1, never by its present GC zero."""
import inspect
import pg1584_current_native_catalog as prior

def backup_window(rows):
    def require(v):
        if not v:raise ValueError('current Backup genuine generation refused')
    require(type(rows)is list and bool(rows));cursors=set()
    binding={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-backup.service','INVOCATION_ID':'d479dcdf4d784f898979844b130dd450'}
    for r in rows:
        require(type(r)is dict and all(r.get(k)==v for k,v in binding.items()))
        stamp=r.get('__MONOTONIC_TIMESTAMP');cursor=r.get('__CURSOR');real=r.get('__REALTIME_TIMESTAMP')
        require(type(stamp)is str and stamp.isdigit()and 32043431270<=int(stamp)<=33583425972)
        require(type(real)is str and real.isdigit()and type(cursor)is str and bool(cursor)and cursor not in cursors);cursors.add(cursor)
        require(r.get('JOB_RESULT')in(None,'done'))
    starts=[r for r in rows if r.get('MESSAGE_ID')=='7d4958e842da4a758f6c1cdc7b36dcc5'and r.get('JOB_ID')=='51019'and r.get('JOB_TYPE')=='start']
    done=[r for r in rows if r.get('MESSAGE_ID')=='39f53479d3a045ac8e11786248231fbf'and r.get('JOB_ID')=='51019'and r.get('JOB_TYPE')=='start'and r.get('JOB_RESULT')=='done']
    success=[r for r in rows if r.get('MESSAGE_ID')=='7ad2d189f7e94e70a38c781354912448']
    stop=[r for r in rows if r.get('MESSAGE_ID')=='9d1aaa27d60140bd96365438aad20286'and r.get('JOB_ID')=='51166'and r.get('JOB_TYPE')=='stop'and r.get('JOB_RESULT')=='done']
    require(len(starts)==len(done)==len(success)==len(stop)==1)
    require([int(v[0]['__MONOTONIC_TIMESTAMP'])for v in [starts,done,success,stop]]==[32060797641,32061771845,32062391348,32062392052])
    return (32060797641,32062391348)

def catalog_source():
    raw=prior.CODE
    marker="names=[('cleanup/cleanup.exec'"
    insertion="""backup_raw=subprocess.check_output(['journalctl','--boot=3d69f5af6bac46b1a5407591c4a79a0d','_PID=1','UNIT=schubert-nk-backup.service','INVOCATION_ID=d479dcdf4d784f898979844b130dd450','-o','json','--no-pager'],timeout=20)
backup_rows=[json.loads(line)for line in backup_raw.splitlines()];backup_start,backup_end=backup_window(backup_rows)
"""
    if raw.count(marker)!=1:raise ValueError('one actual catalog boundary required')
    raw=raw.replace(marker,insertion+"names=[('backup/backup.exec','schubert-nk-backup.service'),('cleanup/cleanup.exec'")
    raw=raw.replace(" if unit=='schubert-nk-morning-controller.service':start=32043431270;end=33583425972", " if unit=='schubert-nk-backup.service':start=backup_start;end=backup_end\n elif unit=='schubert-nk-morning-controller.service':start=32043431270;end=33583425972")
    raw=raw.replace('len(selected)==7','len(selected)==8').replace('in selected})==7','in selected})==8')
    raw=raw.replace("{'backup/backup.exec','ordinary-inspector196/", "{'ordinary-inspector196/")
    raw=raw.replace("'oldSixArchiveUnchanged':True", "'oldSixArchiveUnchanged':True,'backupPid1GenerationVerified':True,'backupJournalSha256':hashlib.sha256(backup_raw).hexdigest()")
    raw='import subprocess\n'+inspect.getsource(backup_window)+'\n'+raw
    compile(raw,'<genuine current eight catalog>','exec');return raw

def main():
    raw=inspect.getsource(prior.main).replace('pg1584-current-native-catalog-v1','pg1586-current-native-catalog-v2')
    env={**prior.__dict__,'CODE':catalog_source()};exec(compile(raw,'<new-only current Backup catalog>','exec'),env)
    return env['main']()

if __name__=='__main__':raise SystemExit(main())
