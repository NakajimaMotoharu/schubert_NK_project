import pg5288_morning_launch_selected as entry
import pg5281_factory_finish as finish
from pg5290_morning_launch_bytecode import SOURCE


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5286-scope-classification-morning-execution-v1/manifest.json',
        previous_sha='78c25810fe5b44bc9adb8da09b923d07ad0fa44db5c89adc702d42c85bcac306',
        previous_source='480abc783abe4ee3f03cefc4a73a0423cd808a53',
        qualified_ref='018_NK-OPS-001/evidence/provisional/pg5288-morning-launch-green-v1-metadata-v2/manifest.json',
        tests=1005,suites=124,counts={'FIXED_LIMITED':190,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':46},
        out_name='PG5294-scope-classification-morning-launch-v1')
