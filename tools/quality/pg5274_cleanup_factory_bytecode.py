"""Twelve real Cleanup/Transfer/lock owners; native-only branches stay unqualified."""
import pg5272_cleanup_factory_selected as entry
import pg5265_owned_factory_proof as proof

SOURCE='3551be4f84f14c07c63425a807690478067532c1'
OUT='PG5274-cleanup-factory-bytecode-v1'


def main():
    _,value=proof.prove(entry=entry,run_name='pg5272-cleanup-factory-green-v1',
        prior_name='pg5264-morning-backup-green-v1',source=SOURCE,tests=907,suites=111,
        package='dev.codex.schubert.nk.batch.file.',
        scopes={'CleanupExpiryExecution':2,'CleanupMaintenanceWork':2,'CleanupNativeExecution':3,
                'CleanupNativePreflight':2,'MaintenanceFileLock':2,'TransferCleanup':1},
        kinds={'CleanupExpiryExecution':{'OwnedTransferDirectory.open:':2},
               'CleanupMaintenanceWork':{'OwnedTransferDirectory.open:':2},
               'CleanupNativeExecution':{'OwnedTransferDirectory.open:':3},
               'CleanupNativePreflight':{'OwnedTransferDirectory.open:':2,'Method openBackup:':1},
               'MaintenanceFileLock':{'OwnedTransferDirectory.open:':1,'OwnedTransferDirectory.openExistingChild:':1},
               'TransferCleanup':{'OwnedTransferDirectory.openExistingDate:':1}},out_name=OUT)
    value.update(rawDirectoryFactories=12,additionalHelperTailProofs=1,nativeOwnerExecutionQualified=False)
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
