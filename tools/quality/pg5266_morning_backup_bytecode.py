"""Nine Morning Backup Directory owners, including direct openBackup method reference."""
import subprocess
import pg5138_factory_bytecode as bytecode
import pg5264_morning_backup_selected as entry
import pg5265_owned_factory_proof as proof

SOURCE='4661101cae269ae709343282f029c5894d97fb95'
OUT='PG5266-morning-backup-bytecode-v1'


def main():
    run,value=proof.prove(entry=entry,run_name='pg5264-morning-backup-green-v1',
        prior_name='pg5256-backup-worker-green-v1',source=SOURCE,tests=882,suites=105,
        package='dev.codex.schubert.nk.batch.file.',
        scopes={'MorningBackupArtifacts':7,'MorningBackupRetention':1,'MorningBackupReuse':1},
        kinds={'MorningBackupArtifacts':{'OwnedTransferDirectory.open:':5,'OwnedTransferDirectory.openExistingChild:':2},
               'MorningBackupRetention':{'OwnedTransferDirectory.open:':1},'MorningBackupReuse':{'OwnedTransferDirectory.open:':1}},out_name=OUT)
    verbose=subprocess.check_output([str(bytecode.JAVAP),'-p','-c','-v','-classpath',
        str(run/'source/src/schubert-nk-batch/target/classes'),'dev.codex.schubert.nk.batch.file.MorningBackupArtifacts'],text=True)
    if 'REF_invokeStatic dev/codex/schubert/nk/batch/file/MorningBackupArtifacts.openBackup:()Ldev/codex/schubert/nk/storage/OwnedTransferDirectory;' not in verbose:
        raise ValueError('openBackup must be direct raw-return method reference under prebuilt protection')
    value.update(rawDirectoryFactories=9,directHelperFactories=1,nativeOwnerExecutionQualified=False)
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
