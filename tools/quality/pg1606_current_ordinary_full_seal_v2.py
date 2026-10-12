"""New-only ordinary full seal; correct prior schema and Backup-vs-skip oracle.

BUG1134/YKT902. Backup manifest/retention qualification remains explicit pending;
this read-only seal cannot authorize another Root/Backup or a formal acceptance.
"""
import inspect
import pg1603_current_newrun_completed_seal as prior
from pg1605_current_ordinary_rows_oracle_v2 import source as oracle

def payload():
    raw=prior.payload()
    raw=prior.once(raw,'ORACLE='+repr(prior.oracle()),'ORACLE='+repr(oracle()))
    raw=raw.replace('pg1603-current-newrun-completed-seal-v1','pg1606-current-ordinary-full-seal-v2')
    raw=prior.once(raw,"before=json.loads(before_raw)","before=json.loads(before_raw)\nrequire(set(before)=={'backup','configuration','extraDurable','native','originals','pid1','rows','runtime','startup','unitFilesActual','units'})\nbefore['durable']={'backup':before['backup'],'originals':before['originals'],**before['extraDurable']}\nbefore['oneTimeRuntime']=before['runtime']")
    # This observed DONE end is data qualified by the independent receipt.
    raw=raw.replace("'genuineCompletion':proof.result,","'genuineCompletion':proof.result,'doneEndUtc':proof.done.decode('ascii').splitlines()[4],")
    raw=raw.replace("'genuineCompletion':current['genuineCompletion'],","'genuineCompletion':current['genuineCompletion'],'doneEndUtc':current['doneEndUtc'],")
    raw=raw.replace("'businessFullOraclePending':False","'businessFullOraclePending':True,'sqlOracleQualified':True,'backupManifestRetentionOraclePending':True")
    compile(raw,'<correct current ordinary full private seal>','exec');return raw

def main():
    raw=inspect.getsource(prior.prior.main).replace('pg1578-current-completed-seal-v1','pg1606-current-ordinary-full-seal-v2').replace('pg1577-current-root-done-receipt-v1','pg1601-current-newrun-done-receipt-v1')
    ns={**prior.prior.__dict__,'payload':payload};exec(compile(raw,'<new-slot correct ordinary fullseal transport>','exec'),ns)
    return ns['main']()

if __name__=='__main__':raise SystemExit(main())
