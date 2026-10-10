"""New-only corrected failed capture: fresh two Backup SUCCESS, eight cleanup SKIP.

Previous PG1120 failed slot/log is immutable; no recovery/VM operation authority.
"""
import ast
from pathlib import Path
import pg1120_current_failed_capture as previous

R=Path(__file__).resolve().parent


def payload():
    raw=previous.PAYLOAD.replace('failed-capture-v1','failed-capture-v2')
    old="require(all(r['run_id']==RUN and r['business_date']=='2026-10-10'and r['status']=='SKIPPED'"
    # Limit the pre-existing ALREADY_SUCCESSFUL oracle to the eight non-Backup
    # steps. Backup has a separate independent manifest/files/DB oracle below.
    marker="for r in delta))\ndef original_oracle"
    if raw.count(old)!=1 or raw.count(marker)!=1:raise ValueError('fixed failed row clause refused')
    raw=raw.replace(marker,"for r in delta if r['step']not in {'BACKUP_DB','BACKUP_CONFIG'}))\ndef original_oracle")
    marker="else:require(durable[kind]==old)"
    if raw.count(marker)!=1:raise ValueError('fixed Backup delta clause refused')
    raw=raw.replace(marker,"elif kind=='backup':pass # Independent fresh Backup oracle below; never infer unchanged.\n  else:require(durable[kind]==old)")
    marker="for name,digest in baseline['artifacts'].items():require(hashlib.sha256((release/name).read_bytes()).hexdigest()==digest)"
    extra=r'''
 profile_raw=pathlib.Path('/etc/schubert-nk/backup-profile.json').read_bytes()
 require(hashlib.sha256(profile_raw).hexdigest()==baseline['artifacts']['config/effective/backup-profile.json'])
 profile=json.loads(profile_raw)
 recipient=pathlib.Path('/etc/schubert-nk/credentials/backup-recipient').read_bytes()
 uid=int(command(['/usr/bin/id','-u','schubert-backup']).strip());gid=int(command(['/usr/bin/id','-g','schubert-backup']).strip())
 backupSummary=backup.qualify(RUN,CUTOFF,baseline['durable']['backup'],durable['backup'],rs['schubert.batch_runs'],profile,recipient,(uid,gid),lambda name:pathlib.Path(name).read_bytes())
'''
    if raw.count(marker)!=1:raise ValueError('fixed input artifact binding refused')
    raw=raw.replace(marker,marker+'\n'+extra)
    raw=raw.replace("'units':us,'actor':actor","'backupSummary':backupSummary,'units':us,'actor':actor")
    raw=raw.replace("'new10ExactSkip':True","'freshBackupTwoSuccessVerified':True,'cleanupEightExactSkip':True")
    raw=raw.replace("'oldOriginalsBackupCredentialsProofsPreserved':True","'oldOriginalsBackupCredentialsProofsPreserved':True,'backupManifestSha256':value['backupSummary']['manifestSha256']")
    oracle=(R/'pg1121_fresh_backup_oracle.py').read_text()
    raw="import types\nbackup=types.ModuleType('independent_fresh_backup');exec("+repr(oracle)+",backup.__dict__)\n"+raw
    ast.parse(raw);return raw


def main():
    import inspect
    code=inspect.getsource(previous.main).replace('pg1120-current-failed-capture-v1','pg1122-current-failed-capture-v2')
    env=dict(previous.__dict__);env['PAYLOAD']=payload()
    exec(compile(code,'<new-only corrected fresh failed capture>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
