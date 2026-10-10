"""New-only actual failed capture including lawful seven-generation retirement."""
import ast
import inspect
from pathlib import Path
import pg1120_current_failed_capture as transport
from pg1126_current_failed_capture_v4 import payload as previous
from pg1129_retired_backup_proof import proof


def payload():
    retired=proof()
    raw=previous().replace('failed-capture-v4','failed-capture-v5')
    marker="(uid,gid),lambda name:pathlib.Path(name).read_bytes())"
    if raw.count(marker)!=1:raise ValueError('fixed independent Backup post insertion refused')
    raw=raw.replace(marker,"(uid,gid),lambda name:pathlib.Path(name).read_bytes(),retired=RETIREMENT)")
    old="recipient=pathlib.Path('/etc/schubert-nk/credentials/backup-recipient').read_bytes()"
    if raw.count(old)!=1:raise ValueError('fixed canonical recipient input insertion refused')
    raw=raw.replace(old,"recipient=(release/'config/effective/backup-age-recipient').read_bytes()\n require(hashlib.sha256(recipient).hexdigest()==artifactSummary['currentArtifactHashes']['config/effective/backup-age-recipient'])")
    raw=raw.replace("'oldOriginalsBackupCredentialsProofsPreserved':True",
                    "'oldOriginalsCredentialsProofsPreserved':True,'backupSevenGenerationRetentionVerified':True,'retiredBackupPrivatePreservationSha256':RETIREMENT['privateProofSha256']")
    raw='RETIREMENT='+repr(retired)+'\n'+raw
    ast.parse(raw);return raw


def main():
    raw=inspect.getsource(transport.main)
    raw=raw.replace('pg1120-current-failed-capture-v1','pg1130-current-failed-capture-v5')
    raw=raw.replace('PG1120-current-failed-capture-v1','PG1130-current-failed-capture-v5')
    env=dict(transport.__dict__);env['PAYLOAD']=payload()
    exec(compile(raw,'<new-only complete current failed capture>','exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
