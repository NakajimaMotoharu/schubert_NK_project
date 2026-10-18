"""Seventeen actual Directory factories including nested Completion; no native credit."""
import pg5280_morning_execution_selected as entry
import pg5265_owned_factory_proof as proof

SOURCE='480abc783abe4ee3f03cefc4a73a0423cd808a53'
OUT='PG5282-morning-execution-bytecode-v1'
SCOPES={'MorningStartupRoots':4,'MorningControlScope':4,'MorningCurrentInvalidation':1,
        'MorningExpiryExecution':2,'MorningCleanupExecution':3,'MorningBrokerExecution':2,
        'MorningBrokerExecution$Completion':1}


def main():
    _,value=proof.prove(entry=entry,run_name='pg5280-morning-execution-green-v1',
        prior_name='pg5272-cleanup-factory-green-v1',source=SOURCE,tests=977,suites=120,
        package='dev.codex.schubert.nk.batch.file.',scopes=SCOPES,
        kinds={name:{'OwnedTransferDirectory.open:':count} for name,count in SCOPES.items()},out_name=OUT)
    value.update(rawDirectoryFactories=17,nativeOwnerExecutionQualified=False)
    proof.publish(entry,value,OUT)


if __name__=='__main__':main()
