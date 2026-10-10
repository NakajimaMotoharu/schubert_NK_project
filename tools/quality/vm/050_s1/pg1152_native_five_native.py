"""Stage immutable current native-five operator then execute exactly once."""
import ast
import inspect
import pg1139_failed_recovery_native as prior


def source():
    text=inspect.getsource(prior)
    for old,new in [
        ('pg1138-failed-recovery-frozen-v3.safe.json','pg1151-native-five-frozen-v3.safe.json'),
        ('pg1134-issued-api-tools-v3','pg1148-native-five-tools-v3'),
        ('Pg1134SingleApiIntentTest','Pg1148NativeRoleDirectoryTest'),
        ('Pg1134SingleApiRecovery','Pg1148NativeRolePreparation'),
        ('pg1139-fixed-stage-v1','pg1152-fixed-stage-v1'),
        ('pg1139-stage-v1.exit','pg1152-stage-v1.exit'),
        ("'pg1139-'+action+'-v1'","'pg1152-'+action+'-v1'"),
        ("'pg1139-' + sys.argv[1] + '-v1'","'pg1152-' + sys.argv[1] + '-v1'"),
        ('PG1139_IMMUTABLE_STAGE','PG1152_IMMUTABLE_STAGE'),
        ('pg1139_failed_recovery_native.py','pg1152_native_five_native.py'),
        ('PG1139 immutable current failed recovery','PG1152 immutable current native five'),
        ("len(frozen['phases'])==4","len(frozen['phases'])==3")]:
        if old not in text:raise ValueError('fixed five-role transport binding refused')
        text=text.replace(old,new)
    ast.parse(text);return text


if __name__=='__main__':exec(compile(source(),'<new-only current native-five transport>','exec'),{'__file__':__file__,'__name__':'__main__'})
