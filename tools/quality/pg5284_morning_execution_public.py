import pg5280_morning_execution_selected as entry
import pg5281_factory_finish as finish


if __name__=='__main__':
    raise SystemExit(finish.publish_current(entry=entry,run_name='pg5280-morning-execution-green-v1',
        proof_name='PG5282-morning-execution-bytecode-v1',counts=(977,120),
        spec='1081_MorningRoot・Control・Execution17_factory所有_PT仕様.md',
        proof_key='morningExecutionBytecodeProofSha256',extra={'rawDirectoryFactories':17}))
