import pg5280_morning_execution_selected as entry
import pg5281_factory_finish as finish
from pg5282_morning_execution_bytecode import SOURCE


if __name__=='__main__':
    finish.classify_current(entry=entry,source=SOURCE,
        previous_ref='018_NK-OPS-001/evidence/provisional/PG5278-scope-classification-cleanup-factory-v1/manifest.json',
        previous_sha='f83538f6f210f339e83b7ea8a524a64dfdc65a8cac39171c1b1377e05f1e0217',
        previous_source='3551be4f84f14c07c63425a807690478067532c1',
        qualified_ref='018_NK-OPS-001/evidence/provisional/pg5280-morning-execution-green-v1-metadata-v2/manifest.json',
        tests=977,suites=120,counts={'FIXED_LIMITED':183,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':53},
        out_name='PG5286-scope-classification-morning-execution-v1')
