import pg5288_morning_launch_selected as entry
import pg5281_factory_finish as finish


if __name__=='__main__':
    raise SystemExit(finish.publish_current(entry=entry,run_name='pg5288-morning-launch-green-v1',
        proof_name='PG5290-morning-launch-bytecode-v1',counts=(1005,124),
        spec='1083_MorningAdmission・Launch・Process7_factory所有_PT仕様.md',
        proof_key='morningLaunchBytecodeProofSha256',extra={'rawDirectoryFactories':7}))
